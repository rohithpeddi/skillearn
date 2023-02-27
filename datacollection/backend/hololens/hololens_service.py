import logging
import os
import threading

import numpy as np
import redis

from datacollection.backend.Recording import Recording
from datacollection.backend.constants import *
from datacollection.backend.hololens.hl2ss import *
from datacollection.backend.hololens.hololens_rest_api import *

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('Created Hololens service file')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class Producer:

    def __init__(self, redis_pool, recording, port_to_stream, active_streams):
        self.redis_pool = redis_pool
        self.recording = recording

        self.port_to_stream = port_to_stream
        self.active_streams = active_streams

        self.enable_streams = True
        self.stream_threads = []

    # Currently we capture data from streams from only PHOTO VIDEO, DEPTH AHAT, SPATIAL INPUT, MICROPHONE
    def _fetch_stream_client(self, stream_port):
        stream_client = None
        if stream_port == StreamPort.PHOTO_VIDEO:
            # If the RAW images takes a lot of time to transfer
            # 1. Change the resolution of video frames and check
            # 2. Else use encoded format for frames
            # 3. Else move to REST-API approach
            stream_client = rx_pv(self.recording.device_ip, stream_port, ChunkSize.PHOTO_VIDEO, StreamMode.MODE_1,
                                  PV_FRAME_WIDTH, PV_FRAME_HEIGHT, PV_FRAMERATE, PV_VIDEO_PROFILE_RAW,
                                  PV_VIDEO_BITRATE_RAW)

        elif stream_port == StreamPort.RM_DEPTH_AHAT:
            stream_client = rx_rm_depth_ahat(self.recording.device_ip, stream_port, ChunkSize.RM_DEPTH_AHAT,
                                             AHAT_MODE, AHAT_PROFILE_RAW, AHAT_BITRATE_RAW)
        elif stream_port == StreamPort.MICROPHONE:
            stream_client = rx_microphone(self.recording.device_ip, stream_port, ChunkSize.MICROPHONE,
                                          AUDIO_PROFILE_RAW)
        elif stream_port == StreamPort.SPATIAL_INPUT:
            stream_client = rx_si(self.recording.device_ip, stream_port, ChunkSize.SPATIAL_INPUT)

        return stream_client

    def _process_stream(self, stream_port):
        logger.log(logging.INFO,
                   f"Configuring {self.port_to_stream[stream_port]} Producer for recording {self.recording.__str__()}")

        stream_client = self._fetch_stream_client(stream_port)

        if stream_client is None:
            logger.log(logging.ERROR, f'Stream client is not configured for stream {self.port_to_stream[stream_port]}')
            return

        stream_client.open()

        logger.log(logging.INFO, f"Created stream client for {self.port_to_stream[stream_port]}")

        # Create a redis client and push the stream data to the queue named stream_port continuously
        stream_redis_client = redis.Redis(connection_pool=self.redis_pool)

        stream_queue_name = self.port_to_stream[stream_port]

        while self.enable_streams:
            stream_data = stream_client.get_next_packet()
            stream_redis_client.lpush(stream_queue_name, bytes(pack_packet(stream_data)))

        logger.log(logging.INFO, f"Closing stream client for {self.port_to_stream[stream_port]}")

        stream_client.close()

    def start_processing_streams(self):
        for stream_port in self.active_streams:
            stream_thread = threading.Thread(target=self._process_stream, args=(stream_port,))
            self.stream_threads.append(stream_thread)

        for stream_thread in self.stream_threads:
            stream_thread.start()

    def stop_processing_streams(self):
        self.enable_streams = False

        for stream_thread in self.stream_threads:
            stream_thread.join()


class FileWriter:

    def __init__(self, file_path):
        self._opened_file = open(file_path, 'ab')

    def write(self, stream_packet):
        self._opened_file.write(stream_packet)

    def close(self):
        self._opened_file.close()


class Consumer:

    def __init__(self, redis_pool, recording, port_to_stream, active_streams, port_to_dir):
        self.redis_pool = redis_pool
        self.redis_pool = redis_pool
        self.recording = recording

        self.port_to_stream = port_to_stream
        self.active_streams = active_streams
        self.port_to_dir = port_to_dir

        self.store_frame_as_binary = False
        self.enable_streams = True
        self.stream_threads = []

    def _process_stream_data(self, stream_port, stream_data, **kwargs):
        # Unpack the raw data
        # This packet has timestamp, payload and necessary pose information
        stream_packet = unpack_packet(stream_data)
        stream_name = self.port_to_stream[stream_port]
        stream_directory = self.port_to_dir[stream_port]
        if stream_port == StreamPort.PHOTO_VIDEO:
            # Here we need to save
            # 1. Pose information
            np.savez(os.path.join(stream_directory, kwargs[PV_POSE_FILE_NAME]), stream_packet.pose)

            # 2. PV payload information - decoded
            pv_file_name = f'{self.recording.get_recording_id()}_{stream_name}_{stream_packet.timestamp}.jpg'
            pv_file_path = os.path.join(kwargs[PV_DATA_DIRECTORY], pv_file_name)

            frame_nv12 = np.frombuffer(stream_packet.payload, dtype=np.uint8,
                                       count=int((PV_STRIDE * PV_FRAME_HEIGHT * 3) / 2)).reshape(
                (int(PV_FRAME_HEIGHT * 3 / 2), PV_STRIDE))
            frame_bgr = cv2.cvtColor(frame_nv12[:, :PV_FRAME_WIDTH], cv2.COLOR_YUV2BGR_NV12)

            cv2.imwrite(pv_file_path, frame_bgr)
        elif stream_port == StreamPort.RM_DEPTH_AHAT:
            # Here we need to save
            # 1. Pose information
            # np.savez(os.path.join(stream_directory, kwargs[DEPTH_AHAT_POSE_FILE_NAME]), stream_packet.pose)
            kwargs[DEPTH_AHAT_POSE_WRITER].write(stream_packet.pose)

            # 2. AHAT AB information
            ab_file_name = f'{self.recording.get_recording_id()}_{stream_name}_{stream_packet.timestamp}_ab.png'
            ab_file_path = os.path.join(kwargs[DEPTH_AHAT_AB_DATA_DIRECTORY], ab_file_name)

            ab_data = np.frombuffer(stream_packet.payload, dtype=np.uint16,
                                    offset=Parameters_RM_DEPTH_AHAT.PIXELS * hl2ss._SIZEOF.WORD,
                                    count=Parameters_RM_DEPTH_AHAT.PIXELS).reshape(Parameters_RM_DEPTH_AHAT.SHAPE)
            # frame_ab = cv2.convertScaleAbs(ab_data.astype(np.uint16), alpha=(255.0/np.amax(ab_data)))

            cv2.imwrite(ab_file_path, ab_data)

            # 3. AHAT depth information
            depth_file_name = f'{self.recording.get_recording_id()}_{stream_name}_{stream_packet.timestamp}_depth.png'
            depth_file_path = os.path.join(kwargs[DEPTH_AHAT_DEPTH_DATA_DIRECTORY], depth_file_name)

            depth_data = np.frombuffer(stream_packet.payload, dtype=np.uint16,
                                       count=Parameters_RM_DEPTH_AHAT.PIXELS).reshape(
                Parameters_RM_DEPTH_AHAT.SHAPE)
            # frame_depth = cv2.convertScaleAbs(depth_data.astype(np.uint16), alpha=(255.0/np.amax(depth_data)))

            cv2.imwrite(depth_file_path, depth_data)
        elif stream_port == StreamPort.MICROPHONE:
            kwargs[MICROPHONE_DATA_WRITER].write(stream_packet)
        elif stream_port == StreamPort.SPATIAL_INPUT:
            kwargs[SPATIAL_DATA_WRITER].write(stream_data)

    def _fetch_stream_kwargs(self, stream_port):
        stream_directory = self.port_to_dir[stream_port]
        stream_name = self.port_to_stream[stream_port]
        kwargs = {}
        if stream_port == StreamPort.PHOTO_VIDEO:
            # Here we need to save
            # 1. Pose information
            # 2. PV payload information
            kwargs[PV_POSE_FILE_NAME] = f'{self.recording.get_recording_id()}_{stream_name}_pose'
            kwargs[PV_DATA_DIRECTORY] = stream_directory
        elif stream_port == StreamPort.RM_DEPTH_AHAT:
            # Here we need to save
            # 1. Pose information
            # 2. AHAT AB information
            # 3. AHAT depth information
            stream_file_path = os.path.join(stream_directory,
                                            f'{self.recording.get_recording_id()}_{stream_name}_pose.bin')
            kwargs[DEPTH_AHAT_POSE_WRITER] = FileWriter(stream_file_path)
            kwargs[DEPTH_AHAT_AB_DATA_DIRECTORY] = os.path.join(stream_directory, AB)
            kwargs[DEPTH_AHAT_DEPTH_DATA_DIRECTORY] = os.path.join(stream_directory, DEPTH)
        elif stream_port == StreamPort.MICROPHONE:
            # Here we need to save
            # 1. Dump of the microphone data into a bin file
            stream_file_path = os.path.join(stream_directory, f'{self.recording.get_recording_id()}_{stream_name}.bin')
            kwargs[MICROPHONE_DATA_WRITER] = FileWriter(stream_file_path)
        elif stream_port == StreamPort.SPATIAL_INPUT:
            # Here we need to save
            # 1. Dump of the spatial data into a bin file
            stream_file_path = os.path.join(stream_directory, f'{self.recording.get_recording_id()}_{stream_name}.bin')
            kwargs[SPATIAL_DATA_WRITER] = FileWriter(stream_file_path)

        return kwargs

    def _close_stream_writers(self, stream_port, kwargs):
        if stream_port == StreamPort.MICROPHONE:
            kwargs[MICROPHONE_DATA_WRITER].close()
        elif stream_port == StreamPort.SPATIAL_INPUT:
            kwargs[SPATIAL_DATA_WRITER].close()

    def _process_stream(self, stream_port):
        stream_name = self.port_to_stream[stream_port]

        logger.log(logging.INFO, f"Configuring {stream_name} Consumer for recording {self.recording.__str__()}")

        # Create a redis client and push the stream data to the queue named stream_port continuously
        stream_redis_client = redis.Redis(connection_pool=self.redis_pool)
        done_processing = False

        kwargs = self._fetch_stream_kwargs(stream_port)

        while True:
            stream_data = stream_redis_client.brpop([stream_name], timeout=3)

            if stream_data is None:
                # Finished processing of the streams
                if not self.enable_streams:
                    done_processing = True
                    logger.log(logging.INFO,
                               f"Finished {stream_name} Consumer processing for recording {self.recording.__str__()}")
                break
            else:
                # Convert the bytes received from stream data into byte array
                self._process_stream_data(stream_port, bytearray(stream_data[1]), **kwargs)

        if not done_processing:
            # Might be a temporary hold on the data, can come back in sometime
            # So make the process recursive
            logger.log(logging.INFO,
                       f"Reached Timeout {self.port_to_stream[stream_port]} Consumer but stream data is not yet done, so initialized processing again")
            self._process_stream(stream_port)
        else:
            self._close_stream_writers(stream_port, kwargs)
            return

    def start_processing_streams(self):
        for stream_port in self.active_streams:
            stream_thread = threading.Thread(target=self._process_stream, args=(stream_port,))
            self.stream_threads.append(stream_thread)

        for stream_thread in self.stream_threads:
            stream_thread.start()

    def stop_processing_streams(self):
        self.enable_streams = False

        for stream_thread in self.stream_threads:
            stream_thread.join()


class HololensService:

    def __init__(self):
        self.rm_enable = True
        self.is_recording = False
        self.lock = threading.Lock()

        self.redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)

        # # Flush all the keys currently present in the database
        self.redis_connection = redis.Redis(connection_pool=self.redis_pool)
        self.redis_connection.flushdb()

    @staticmethod
    def save_hololens2_info(ip_address, folder_path):
        host_name = get_hostname(ip_address)
        client = hl2ss.ipc_rc(ip_address, hl2ss.IPCPort.REMOTE_CONFIGURATION)
        utc_offset = client.get_utc_offset(32)
        logger.log(logging.INFO, f"Hololens2 ID: {host_name}")
        logger.log(logging.INFO, f"Hololens2 Offset: {utc_offset}")
        with open(os.path.join(folder_path, 'Hololens2Info.dat'), 'w+') as f:
            f.write(f"Hololens2 Name: {host_name}\n")
            f.write(f"HL2 UTC Offset: {utc_offset}")
        logger.log(logging.INFO,
                   'QPC timestamp to UTC offset is {offset} hundreds of nanoseconds'.format(offset=utc_offset))

    def _init_params(self, recording: Recording, active_streams):
        self.recording = recording
        self.device_ip = self.recording.device_ip
        self.device_name = get_hostname(self.device_ip)
        self.file_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(self.file_dir, "../../../../data")
        self.rec_data_dir = os.path.join(self.data_dir, self.recording.get_recording_id())
        self.port_to_dir = {
            StreamPort.PHOTO_VIDEO: os.path.join(self.rec_data_dir, PHOTOVIDEO),
            StreamPort.MICROPHONE: os.path.join(self.rec_data_dir, MICROPHONE),
            StreamPort.RM_DEPTH_AHAT: os.path.join(self.rec_data_dir, DEPTH_AHAT),
            StreamPort.SPATIAL_INPUT: os.path.join(self.rec_data_dir, SPATIAL),
            StreamPort.RM_IMU_ACCELEROMETER: os.path.join(self.rec_data_dir, IMU_ACCELEROMETER),
            StreamPort.RM_IMU_GYROSCOPE: os.path.join(self.rec_data_dir, IMU_GYROSCOPE),
            StreamPort.RM_IMU_MAGNETOMETER: os.path.join(self.rec_data_dir, IMU_MAGNETOMETER),
            StreamPort.RM_VLC_LEFTFRONT: os.path.join(self.rec_data_dir, VLC_LEFTFRONT),
            StreamPort.RM_VLC_LEFTLEFT: os.path.join(self.rec_data_dir, VLC_LEFTLEFT),
            StreamPort.RM_VLC_RIGHTFRONT: os.path.join(self.rec_data_dir, VLC_RIGHTFRONT),
            StreamPort.RM_VLC_RIGHTRIGHT: os.path.join(self.rec_data_dir, VLC_RIGHTRIGHT),
            StreamPort.RM_DEPTH_LONGTHROW: os.path.join(self.rec_data_dir, DEPTH_LT),
        }

        self.port_to_stream = {
            StreamPort.RM_DEPTH_AHAT: DEPTH_AHAT,
            StreamPort.PHOTO_VIDEO: PHOTOVIDEO,
            StreamPort.MICROPHONE: MICROPHONE,
            StreamPort.SPATIAL_INPUT: SPATIAL,
            StreamPort.RM_DEPTH_LONGTHROW: DEPTH_LT,
            StreamPort.RM_IMU_MAGNETOMETER: IMU_MAGNETOMETER,
            StreamPort.RM_IMU_GYROSCOPE: IMU_GYROSCOPE,
            StreamPort.RM_IMU_ACCELEROMETER: IMU_ACCELEROMETER,
            StreamPort.RM_VLC_LEFTLEFT: VLC_LEFTLEFT,
            StreamPort.RM_VLC_LEFTFRONT: VLC_LEFTFRONT,
            StreamPort.RM_VLC_RIGHTRIGHT: VLC_RIGHTRIGHT,
            StreamPort.RM_VLC_RIGHTFRONT: VLC_RIGHTFRONT
        }

        self.active_streams = active_streams

        for port in self.active_streams:
            create_directories(self.port_to_dir[port])
            if (port == StreamPort.RM_DEPTH_AHAT) or (port == StreamPort.RM_DEPTH_LONGTHROW):
                create_directories(os.path.join(self.port_to_dir[port], AB))
                create_directories(os.path.join(self.port_to_dir[port], DEPTH))

        # Start PV
        self.client_rc = hl2ss.ipc_rc(self.device_ip, hl2ss.IPCPort.REMOTE_CONFIGURATION)
        hl2ss.start_subsystem_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO)
        self.client_rc.wait_for_pv_subsystem(True)

    def _start_record_sensor_streams(self, recording: Recording, active_streams: list):
        # Initialize all Parameters, Producers, Consumers, Display Map, Writer Map
        logger.log(logging.INFO, "Initializing parameters")
        self._init_params(recording, active_streams)
        HololensService.save_hololens2_info(recording.device_ip, self.rec_data_dir)

        self.producer = Producer(self.redis_pool, self.recording, self.port_to_stream, self.active_streams)
        self.producer.start_processing_streams()

        self.consumer = Consumer(self.redis_pool, self.recording, self.port_to_stream, self.active_streams,
                                 self.port_to_dir)
        self.consumer.start_processing_streams()

        while self.rm_enable:
            time.sleep(10)

    def _stop_record_sensor_streams(self):

        logger.log(logging.INFO, "Stopping all record streams")

        self.producer.stop_processing_streams()
        self.consumer.stop_processing_streams()

        # Stopping PV systems
        hl2ss.stop_subsystem_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO)
        self.client_rc.wait_for_pv_subsystem(False)

        logger.log(logging.INFO, "Stopped all systems")

    def start_recording(self, recording: Recording, active_streams=None, is_mrc=True):
        if active_streams is None:
            active_streams = [StreamPort.RM_DEPTH_AHAT, StreamPort.SPATIAL_INPUT]

        if self.is_recording:
            logger.log(logging.INFO, "Already a process is recording videos")
            return
        if is_mrc:
            start_mrc(recording.device_ip)

        logger.log(logging.INFO, "Starting a process to record videos")
        self.is_recording = True
        self._start_record_sensor_streams(recording, active_streams)

    def stop_recording(self, is_mrc=True):
        if not self.is_recording:
            print("Not recording")
            return

        if is_mrc:
            stop_mrc(self.recording.device_ip)
        self.is_recording = False
        self._stop_record_sensor_streams()
        time.sleep(3)
        download_most_recent_mrc_file(self.recording.device_ip, self.rec_data_dir, self.recording.get_recording_id())


def record_all_streams(hololens_service: HololensService, recording: Recording):
    active_streams = [StreamPort.RM_DEPTH_AHAT, StreamPort.PHOTO_VIDEO]

    # active_streams = [StreamPort.RM_DEPTH_AHAT, StreamPort.PHOTO_VIDEO, StreamPort.MICROPHONE,
    #                   StreamPort.SPATIAL_INPUT]

    rec_thread = threading.Thread(target=hololens_service.start_recording, args=(recording, active_streams, False))
    rec_thread.start()

    print("Recording Started")
    sleep_min = 15
    for min_done in range(sleep_min):
        print("Minutes done {}".format(min_done))
        time.sleep(60)

    hololens_service.stop_recording(False)
    rec_thread.join()


def record_mixed_streams(hololens_service: HololensService, recording: Recording):
    active_streams = [StreamPort.RM_DEPTH_AHAT, StreamPort.SPATIAL_INPUT]

    rec_thread = threading.Thread(target=hololens_service.start_recording, args=(recording, active_streams, True))
    rec_thread.start()

    print("Recording Started")
    sleep_min = 15
    for min_done in range(sleep_min):
        print("Minutes done {}".format(min_done))
        time.sleep(60)

    hololens_service.stop_recording()
    rec_thread.join()


if __name__ == '__main__':
    ip_address = '192.168.0.117'
    hl2_service = HololensService()
    recording_instance = Recording("Coffee", "PL1", "P1", "R2", False)
    recording_instance.set_device_ip(ip_address)

    record_mixed_streams(hl2_service, recording_instance)
