import copy
import logging
import multiprocessing as mp
import os
import pickle
import re
import threading
import time
from fractions import Fraction
from subprocess import Popen, PIPE

import av
import cv2
import numpy as np

from datacollection.backend.Recording import Recording
from datacollection.backend.constants import *
from datacollection.backend.hololens_rest_api import HL2_REST_Controller

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('Created Hololens service file')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class HololensService:

    def __init__(self, ip_address, mrc=False):
        self.rm_enable = False
        self.threads_stopped = False
        self.lock = threading.Lock()
        self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

        self._recording = False
        self._recording_thread = None

        self.is_pv_decoded = True
        self.is_depth_decoded = True
        self.is_vlc_decoded = True
        self.save_depth_frames = False
        self.mrc = mrc
        if mrc:
            PORTS.remove(hl2ss.StreamPort.PHOTO_VIDEO)
            PORTS.remove(hl2ss.StreamPort.MICROPHONE)
        self.rest_controller = HL2_REST_Controller(ip_address)

    @staticmethod
    def get_mac_address(ip_address):
        # do_ping(IP) - The time between ping and arp check must be small, as ARP may not cache long
        # print(os.system('arp -n ' + str(IP)))
        pid = Popen(["arp", "-n", ip_address], stdout=PIPE)
        s = pid.communicate()[0].decode("utf-8")
        mac_address = None
        mac_matches = re.search(r'(([a-f\d]{1,2}:){5}[a-f\d]{1,2})', s)
        if mac_matches is not None:
            mac_address = mac_matches.groups()[0]
        return mac_address

    def save_hololens2_info(self, ip_address, folder_path):
        mac_address = self.get_mac_address(ip_address)
        host_name = self.rest_controller.get_hostname()
        logger.log(logging.INFO, f"Hololens2 ID: {host_name}")
        logger.log(logging.INFO, f"Hololens2 MAC: {mac_address}")
        with open(os.path.join(folder_path, 'Hololens2Info.dat'), 'w+') as f:
            f.write(f"Name: {host_name}\n")
            f.write(f"MAC: {mac_address}")

    def _receive_pv(self):
        pv_port = hl2ss.StreamPort.PHOTO_VIDEO

        if self.is_pv_decoded:
            pv_client = hl2ss.rx_decoded_pv(self.device_ip, pv_port, hl2ss.ChunkSize.PHOTO_VIDEO,
                                            hl2ss.StreamMode.MODE_1, FRAME_WIDTH, FRAME_HEIGHT, FRAMERATE,
                                            VIDEO_PROFILE, VIDEO_BITRATE, VIDEO_DECODE)
            pv_pose = []
        else:
            pv_client = hl2ss.rx_pv(self.device_ip, pv_port, hl2ss.ChunkSize.PHOTO_VIDEO,
                                    hl2ss.StreamMode.MODE_1, FRAME_WIDTH, FRAME_HEIGHT, FRAMERATE, VIDEO_PROFILE,
                                    VIDEO_BITRATE)
            pv_frames = []

        pv_client.open()
        logger.log(logging.INFO, "Configuring PhotoVideo")

        while self.rm_enable:
            data = pv_client.get_next_packet()
            if self.is_pv_decoded:
                pv_pose.append([data.timestamp, data.pose])
                self._write_pv_frame_async(pv_port, copy.deepcopy(data), self.async_storage_map[pv_port])
            else:
                pv_frames.append([data.timestamp, data.payload, data.pose])

        if self.is_pv_decoded:
            logger.log(logging.INFO, f"Captured pv frames {len(pv_pose)}")
            with open(os.path.join(self.rec_data_dir, 'pv_pose.pkl'), 'wb') as f:
                pickle.dump(pv_pose, f)
        else:
            logger.log(logging.INFO, f"Captured pv frames {len(pv_frames)}")
            with open(os.path.join(self.rec_data_dir, 'pv_frames.pkl'), 'wb') as f:
                pickle.dump(pv_frames, f)

        pv_client.close()

    def _receive_vlc(self, vlc_port):
        port_name = hl2ss.get_port_name(vlc_port)

        if self.is_vlc_decoded:
            vlc_client = hl2ss.rx_decoded_rm_vlc(self.device_ip, vlc_port, hl2ss.ChunkSize.RM_VLC, VLC_MODE,
                                                 VLC_PROFILE, VLC_BITRATE)
            vlc_pose = []
        else:
            vlc_client = hl2ss.rx_rm_vlc(self.device_ip, vlc_port, hl2ss.ChunkSize.RM_VLC, VLC_MODE,
                                         VLC_PROFILE, VLC_BITRATE)
            vlc_frames = []

        vlc_client.open()
        logger.log(logging.INFO, "Configuring VLC")

        while self.rm_enable:
            data = vlc_client.get_next_packet()
            if self.is_vlc_decoded:
                vlc_pose.append([data.timestamp, data.pose])
                self._write_vlc_frame_async(vlc_port, copy.deepcopy(data), self.async_storage_map[vlc_port])
            else:
                vlc_frames.append([data.timestamp, data.payload, data.pose])

        if self.is_vlc_decoded:
            logger.log(logging.INFO, f"Captured {port_name}_pose: {len(vlc_pose)}")
            with open(os.path.join(self.rec_data_dir, f'{port_name}_pose.pkl'), 'wb') as f:
                pickle.dump(vlc_pose, f)
        else:
            logger.log(logging.INFO, f"Captured {port_name}_pose: {len(vlc_frames)}")
            with open(os.path.join(self.rec_data_dir, f'{port_name}_frames.pkl'), 'wb') as f:
                pickle.dump(vlc_frames, f)

        vlc_client.close()

    def _receive_depth_ahat(self):
        depth_port = hl2ss.StreamPort.RM_DEPTH_AHAT
        depth_pose = []
        depth_frames = []
        ahat_client = hl2ss.rx_rm_depth_ahat(self.device_ip, depth_port, hl2ss.ChunkSize.RM_DEPTH_AHAT,
                                             AHAT_MODE, AHAT_PROFILE, AHAT_BITRATE)

        ahat_client.open()
        logger.log(logging.INFO, "Configuring Depth AHaT")

        while self.rm_enable:
            data = ahat_client.get_next_packet()
            if self.save_depth_frames:
                depth_frames.append([data.timestamp, data.payload, data.pose])
            else:
                depth_pose.append([data.timestamp, data.pose])
                self._write_depth_async(depth_port, copy.deepcopy(data), self.async_storage_map[depth_port])

        if self.is_depth_decoded:
            logger.log(logging.INFO, f"Captured {len(depth_pose)}")
            with open(os.path.join(self.rec_data_dir, 'depth_pose.pkl'), 'wb') as f:
                pickle.dump(depth_pose, f)
        else:
            logger.log(logging.INFO, f"Captured {len(depth_frames)}")
            with open(os.path.join(self.rec_data_dir, 'depth_frames.pkl'), 'wb') as f:
                pickle.dump(depth_frames, f)

        ahat_client.close()

    def _receive_microphone(self):
        audio_port = hl2ss.StreamPort.MICROPHONE
        audio_client = hl2ss.rx_microphone(self.device_ip, audio_port,
                                           hl2ss.ChunkSize.MICROPHONE,
                                           AUDIO_PROFILE)
        audio_client.open()
        logger.log(logging.INFO, "Configuring Audio Microphone")
        audio_data = []
        while self.rm_enable:
            data = audio_client.get_next_packet()
            audio_data.append([data.timestamp, data.payload])
        print(f'audio_data: {len(audio_data)}')
        with open(os.path.join(self.port_dir_map[audio_port], f'audio_data.pkl'), 'wb') as f:
            pickle.dump(audio_data, f)
        audio_client.close()

    def _receive_spatial(self):
        spatial_port = hl2ss.StreamPort.SPATIAL_INPUT
        spatial_client = hl2ss.rx_si(self.device_ip, spatial_port,
                                     hl2ss.ChunkSize.SPATIAL_INPUT, )
        spatial_client.open()
        logger.log(logging.INFO, "Configuring Spatial Input")
        spatial_data = []
        while self.rm_enable:
            data = spatial_client.get_next_packet()
            spatial_data.append([data.timestamp, data.payload])
        print(f'spatial_data: {len(spatial_data)}')
        with open(os.path.join(self.port_dir_map[spatial_port], f'spatial_data.pkl'), 'wb') as f:
            pickle.dump(spatial_data, f)

        spatial_client.close()

    def _receive_imu(self, imu_port):
        port_name = hl2ss.get_port_name(imu_port)
        imu_client = hl2ss.rx_rm_imu(self.device_ip, imu_port,
                                     self.imu_chunk_map[imu_port], IMU_MODE)
        imu_client.open()
        logger.log(logging.INFO, "Configuring IMU")
        imu_data = []
        while self.rm_enable:
            data = imu_client.get_next_packet()
            imu_data.append([data.timestamp, data.payload])
        print(f'{port_name}_data: {len(imu_data)}')
        with open(os.path.join(self.port_dir_map[imu_port], f'{port_name}_data.pkl'), 'wb') as f:
            pickle.dump(imu_data, f)
        imu_client.close()

    def _init_params(self, rec: Recording):
        self.device_ip = rec.device_ip
        self.rec_id = f"{rec.activity}_{rec.place_id}_{rec.person_id}_{rec.rec_number}"
        self.data_dir = "../../data"
        self.rec_data_dir = os.path.join(self.data_dir, self.rec_id)
        self.port_dir_map = {
            hl2ss.StreamPort.RM_VLC_LEFTFRONT: os.path.join(self.rec_data_dir, 'vlc_lf'),
            hl2ss.StreamPort.RM_VLC_LEFTLEFT: os.path.join(self.rec_data_dir, 'vlc_ll'),
            hl2ss.StreamPort.RM_VLC_RIGHTFRONT: os.path.join(self.rec_data_dir, 'vlc_rf'),
            hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: os.path.join(self.rec_data_dir, 'vlc_rr'),
            hl2ss.StreamPort.RM_DEPTH_AHAT: {
                'ab': os.path.join(self.rec_data_dir, 'dep_ahat_ab'),
                'depth': os.path.join(self.rec_data_dir, 'dep_ahat_depth'),
            },
            hl2ss.StreamPort.RM_DEPTH_LONGTHROW: {
                'ab': os.path.join(self.rec_data_dir, 'dep_lt_ab'),
                'depth': os.path.join(self.rec_data_dir, 'dep_lt_depth'),
            },
            hl2ss.StreamPort.PHOTO_VIDEO: os.path.join(self.rec_data_dir, 'pv'),
            hl2ss.StreamPort.MICROPHONE: os.path.join(self.rec_data_dir, 'mc'),
            hl2ss.StreamPort.SPATIAL_INPUT: os.path.join(self.rec_data_dir, 'spatial'),
            hl2ss.StreamPort.RM_IMU_ACCELEROMETER: os.path.join(self.rec_data_dir, 'imu_acc'),
            hl2ss.StreamPort.RM_IMU_GYROSCOPE: os.path.join(self.rec_data_dir, 'imu_gyro'),
            hl2ss.StreamPort.RM_IMU_MAGNETOMETER: os.path.join(self.rec_data_dir, 'imu_mag'),
        }

        for port in PORTS:
            if port == hl2ss.StreamPort.RM_DEPTH_AHAT or port == hl2ss.StreamPort.RM_DEPTH_LONGTHROW:
                create_directories(self.port_dir_map[port]['ab'])
                create_directories(self.port_dir_map[port]['depth'])
            else:
                create_directories(self.port_dir_map[port])
        self.save_hololens2_info(self.device_ip, self.rec_data_dir)

        self.writer_map = {
            hl2ss.StreamPort.RM_VLC_LEFTFRONT: self._write_pv_frame_async,
            hl2ss.StreamPort.RM_VLC_LEFTLEFT: self._write_pv_frame_async,
            hl2ss.StreamPort.RM_VLC_RIGHTFRONT: self._write_pv_frame_async,
            hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: self._write_pv_frame_async,

            hl2ss.StreamPort.RM_DEPTH_AHAT: self._write_depth_async,

            hl2ss.StreamPort.PHOTO_VIDEO: self._write_pv_frame_async,
            # hl2ss.StreamPort.MICROPHONE: self._write_audio_async,
            # hl2ss.StreamPort.SPATIAL_INPUT: self._write_spatial_async,
            # hl2ss.StreamPort.RM_IMU_ACCELEROMETER: None,
            # hl2ss.StreamPort.RM_IMU_GYROSCOPE: None,
            # hl2ss.StreamPort.RM_IMU_MAGNETOMETER: None,
        }

        self.imu_chunk_map = {
            hl2ss.StreamPort.RM_IMU_ACCELEROMETER: hl2ss.ChunkSize.RM_IMU_ACCELEROMETER,
            hl2ss.StreamPort.RM_IMU_GYROSCOPE: hl2ss.ChunkSize.RM_IMU_GYROSCOPE,
            hl2ss.StreamPort.RM_IMU_MAGNETOMETER: hl2ss.ChunkSize.RM_IMU_MAGNETOMETER,
        }

        total_streams = 8  # (PV, Pose), Audio, Depth, ((VLC, Pose) * 4), MLC
        # Dell Precision 5820 - CPU - 20, Thread/CPU = 2
        thread_per_cpu = 2
        threads_per_stream = int((mp.cpu_count() * thread_per_cpu) / total_streams)
        # threads_per_stream = max(2, threads_per_stream)
        threads_per_stream = 2
        try:
            self.async_storage_map = {}
            storage_threads_map = {
                hl2ss.StreamPort.RM_VLC_LEFTFRONT: threads_per_stream,
                hl2ss.StreamPort.RM_VLC_LEFTLEFT: threads_per_stream,
                hl2ss.StreamPort.RM_VLC_RIGHTFRONT: threads_per_stream,
                hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: threads_per_stream,
                hl2ss.StreamPort.RM_DEPTH_AHAT: 5,
                hl2ss.StreamPort.RM_DEPTH_LONGTHROW: threads_per_stream,
                hl2ss.StreamPort.PHOTO_VIDEO: 5,
            }
            for port in PORTS:
                self.async_storage_map[port] = mp.Pool(storage_threads_map[port])
        except Exception as e:
            logger.log(logging.ERROR, str(e))

        # Start PV
        self.client_rc = hl2ss.ipc_rc(self.device_ip, hl2ss.IPCPort.REMOTE_CONFIGURATION)
        hl2ss.start_subsystem_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO)
        self.client_rc.wait_for_pv_subsystem(True)

    def _write_pv_frame_async(self, port, data, writer_pool: mp.Pool, display=False):
        port_name = hl2ss.get_port_name(port)
        dir_path = self.port_dir_map[port]
        file_path = os.path.join(dir_path, f"{self.rec_id}_{port_name}_{data.timestamp}.jpg")
        if display:
            cv2.imshow(port_name, data.payload.image)
            cv2.waitKey(1)
        if writer_pool is not None and data.payload is not None:
            writer_pool.apply_async(cv2.imwrite(file_path, data.payload.image))

    def _write_vlc_frame_async(self, port, data, writer_pool: mp.Pool, display=False):
        port_name = hl2ss.get_port_name(port)
        dir_path = self.port_dir_map[port]
        file_path = os.path.join(dir_path, f"{self.rec_id}_{port_name}_{data.timestamp}.jpg")
        if display:
            cv2.imshow(port_name, data.payload)
            cv2.waitKey(1)
        if writer_pool is not None and data.payload is not None:
            writer_pool.apply_async(cv2.imwrite(file_path, data.payload))
            # cv2.imwrite(file_path, data.payload)

    def _write_depth_async(self, port, data, writer_pool: mp.Pool, display=False):
        port_name = hl2ss.get_port_name(port)
        dir_path_ab = self.port_dir_map[port]['ab']
        dir_path_depth = self.port_dir_map[port]['depth']
        file_path_ab = os.path.join(dir_path_ab, f"{self.rec_id}_{port_name}_{data.timestamp}_ab.png")
        file_path_depth = os.path.join(dir_path_depth, f"{self.rec_id}_{port_name}_{data.timestamp}_depth.png")
        depth, ab = None, None
        if AHAT_PROFILE == hl2ss.VideoProfile.RAW:
            depth = np.frombuffer(data.payload, dtype=np.uint16, count=hl2ss.Parameters_RM_DEPTH_AHAT.PIXELS) \
                .reshape(hl2ss.Parameters_RM_DEPTH_AHAT.SHAPE)
            ab = np.frombuffer(data.payload, dtype=np.uint16,
                               offset=hl2ss.Parameters_RM_DEPTH_AHAT.PIXELS * hl2ss._SIZEOF.WORD,
                               count=hl2ss.Parameters_RM_DEPTH_AHAT.PIXELS).reshape(
                hl2ss.Parameters_RM_DEPTH_AHAT.SHAPE)
        else:
            _codec = av.CodecContext.create(hl2ss.get_video_codec_name(AHAT_PROFILE), 'r')
            for packet in _codec.parse(data.payload):
                for frame in _codec.decode(packet):
                    depth, ab = hl2ss._unpack_rm_depth_ahat_nv12_as_yuv420p(frame.to_ndarray().astype(np.uint16))

        if depth is None:
            return
        if display:
            cv2.imshow(port_name + '-depth', depth * 8)  # Scaled for visibility
            cv2.imshow(port_name + '-ab', ab / np.max(ab))  # Normalized for visibility
            cv2.waitKey(1)
        if writer_pool is not None:
            writer_pool.apply_async(cv2.imwrite(file_path_ab, ab))
            writer_pool.apply_async(cv2.imwrite(file_path_depth, depth))

    def _write_spatial_async(self, port, data, writer_pool: mp.Pool, display=False):
        pass

    def _write_audio_async(self, port, data, writer_pool: mp.Pool, display=False):
        pass

    def _start_record_sensor_streams(self, recording_instance: Recording):
        # Initialize all Parameters, Producers, Consumers, Display Map, Writer Map
        logger.log(logging.INFO, "Initializing parameters")
        self._init_params(recording_instance)
        vlc_ports = [
            hl2ss.StreamPort.RM_VLC_LEFTLEFT,
            hl2ss.StreamPort.RM_VLC_LEFTFRONT,
            hl2ss.StreamPort.RM_VLC_RIGHTFRONT,
            hl2ss.StreamPort.RM_VLC_RIGHTRIGHT,
        ]
        imu_ports = [
            hl2ss.StreamPort.RM_IMU_ACCELEROMETER,
            hl2ss.StreamPort.RM_IMU_GYROSCOPE,
            hl2ss.StreamPort.RM_IMU_MAGNETOMETER,
        ]
        self.port_threads = {
            hl2ss.StreamPort.PHOTO_VIDEO: threading.Thread(target=self._receive_pv),
            hl2ss.StreamPort.MICROPHONE: threading.Thread(target=self._receive_microphone),
            hl2ss.StreamPort.RM_DEPTH_AHAT: threading.Thread(target=self._receive_depth_ahat),
            hl2ss.StreamPort.SPATIAL_INPUT: threading.Thread(target=self._receive_spatial),
        }
        for vlc_port in vlc_ports:
            self.port_threads[vlc_port] = threading.Thread(target=self._receive_vlc, args=(vlc_port,))

        for imu_port in imu_ports:
            self.port_threads[imu_port] = threading.Thread(target=self._receive_imu, args=(imu_port,))

        # Start all the threads corresponding to each type
        self.rm_enable = True
        if self.mrc:
            self.rest_controller.start_mrc()
        for port in PORTS:
            self.port_threads[port].start()

        for port in PORTS:
            self.port_threads[port].join()
        self.threads_stopped = True

    def _stop_record_sensor_streams(self):

        logger.log(logging.INFO, "Stopping all record streams")
        # Make the shared conditional variables so that process of capturing the frames stops
        self.rm_enable = False
        while not self.threads_stopped:
            time.sleep(0.5)

        # Start all the threads corresponding to each type
        if self.mrc:
            self.rest_controller.stop_mrc()

        # Release all the pools instances attached to different ports
        for port in PORTS:
            if port not in self.async_storage_map or self.async_storage_map[port] is None:
                continue
            self.async_storage_map[port].close()

        logger.log(logging.INFO, "Detached all ports")

        # Stopping PV systems
        hl2ss.stop_subsystem_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO)
        self.client_rc.wait_for_pv_subsystem(False)

        logger.log(logging.INFO, "Stopped all systems")
        if self.mrc:
            # Downloading the MRC Data
            self.rest_controller.download_most_recent_mrc_file(download_location=self.rec_data_dir)

    def start_recording(self, recording_instance: Recording):
        if self._recording:
            logger.log(logging.INFO, "Already a process is recording videos")
            return
        logger.log(logging.INFO, "Starting a process to record videos")
        self._recording = True
        self._start_record_sensor_streams(recording_instance)

    def stop_recording(self):
        if not self._recording:
            print("Not recording")
            return
        self._recording = False
        self._stop_record_sensor_streams()


def test_hololens2_recording():
    ip_address = '192.168.1.149'
    mrc = False
    hl2_service = HololensService(ip_address=ip_address, mrc=mrc)
    rec = Recording("Omelette", "PL3", "P1", "R1", False)
    rec.set_device_ip(ip_address)

    client = hl2ss.ipc_rc(ip_address, hl2ss.IPCPort.REMOTE_CONFIGURATION)
    utc_offset = client.get_utc_offset(32)
    print('QPC timestamp to UTC offset is {offset} hundreds of nanoseconds'.format(offset=utc_offset))

    # For Recording the Hololens2 Sensor data
    rec_thread = threading.Thread(target=hl2_service.start_recording, args=(rec,))
    rec_thread.start()
    while not hl2_service.rm_enable:
        time.sleep(0.1)
        continue
    print("Recording Started")
    sleep_min = 1
    for min_done in range(sleep_min):
        print("Minutes done {}".format(min_done))
        time.sleep(60)
    hl2_service.stop_recording()
    print("Recording Stopped")
    # rec_thread.join()


if __name__ == '__main__':
    test_hololens2_recording()
