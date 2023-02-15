import os
import queue
import threading
import time
import logging
from fractions import Fraction
from threading import Thread
import av
import cv2
import numpy as np
import multiprocessing as mp
from datacollection.error.backend import hl2ss_mp
from datacollection.error.backend.Recording import Recording
from datacollection.error.backend.constants import *

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('Created Hololens service file')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_directories(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class HololensServiceBak:

    def __init__(self):
        self.tsfirst = None
        self.rm_pv_enable = True
        self.rm_vlc_depth_enable = True
        self.lock = threading.Lock()
        self.packet_queue = queue.PriorityQueue()
        self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPG # case-sensitive Codecs
        self.vlc_fourcc = cv2.VideoWriter_fourcc(*'H264')  # mp4v, H264, DIVX # case-sensitive Codecs

        self._recording = False
        self._recording_thread = None

    def _init_params(self, recording_instance: Recording):
        self.device_ip = recording_instance.device_ip

        self.recording_id = "{}_{}_{}_{}".format(recording_instance.activity, recording_instance.place_id,
                                                 recording_instance.person_id, recording_instance.rec_number)

        self.depth_dir_path = "../{}/depth/".format(self.recording_id)
        self.ab_dir_path = "../{}/ab/".format(self.recording_id)
        self.pv_dir_path = "../{}/pv/".format(self.recording_id)
        # self.vlc_dir_path = "../{}/vlc/".format(self.recording_id)
        self.lf_dir_path = "../{}/lf/".format(self.recording_id)
        self.ll_dir_path = "../{}/ll/".format(self.recording_id)
        self.rf_dir_path = "../{}/rf/".format(self.recording_id)
        self.rr_dir_path = "../{}/rr/".format(self.recording_id)

        create_directories(self.depth_dir_path)
        create_directories(self.ab_dir_path)
        create_directories(self.pv_dir_path)
        # create_directories(self.vlc_dir_path)
        create_directories(self.lf_dir_path)
        create_directories(self.ll_dir_path)
        create_directories(self.rf_dir_path)
        create_directories(self.rr_dir_path)

        self.video_file_name = os.path.join(self.pv_dir_path, "{}.mp4".format(self.recording_id))
        self.container = av.open(self.video_file_name, 'w')
        self.stream_video = self.container.add_stream(hl2ss.get_video_codec_name(VIDEO_PROFILE), rate=FRAMERATE)
        self.stream_audio = self.container.add_stream(hl2ss.get_audio_codec_name(AUDIO_PROFILE),
                                                      rate=hl2ss.Parameters_MICROPHONE.SAMPLE_RATE)

        self.display_map = {
            hl2ss.StreamPort.RM_VLC_LEFTFRONT: self._display_basic,
            hl2ss.StreamPort.RM_VLC_LEFTLEFT: self._display_basic,
            hl2ss.StreamPort.RM_VLC_RIGHTFRONT: self._display_basic,
            hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: self._display_basic,
            hl2ss.StreamPort.RM_DEPTH_AHAT: self._display_depth,
            hl2ss.StreamPort.RM_DEPTH_LONGTHROW: self._display_depth,
            hl2ss.StreamPort.PHOTO_VIDEO: self._display_basic
        }

        try:
            self.writers_map = {
                hl2ss.StreamPort.RM_VLC_LEFTFRONT:
                    cv2.VideoWriter(os.path.join(self.lf_dir_path, '{}_lf.mp4'.format(self.recording_id)),
                                    self.fourcc, VLC_FPS, (VLC_WIDTH, VLC_HEIGHT), 0),
                hl2ss.StreamPort.RM_VLC_LEFTLEFT:
                    cv2.VideoWriter(os.path.join(self.ll_dir_path, '{}_ll.mp4'.format(self.recording_id)),
                                    self.fourcc, VLC_FPS, (VLC_WIDTH, VLC_HEIGHT), 0),
                hl2ss.StreamPort.RM_VLC_RIGHTFRONT:
                    cv2.VideoWriter(os.path.join(self.rf_dir_path, '{}_rf.mp4'.format(self.recording_id)),
                                    self.fourcc, VLC_FPS, (VLC_WIDTH, VLC_HEIGHT), 0),
                hl2ss.StreamPort.RM_VLC_RIGHTRIGHT:
                    cv2.VideoWriter(os.path.join(self.rr_dir_path, '{}_rr.mp4'.format(self.recording_id)),
                                    self.fourcc, VLC_FPS, (VLC_WIDTH, VLC_HEIGHT), 0),
                hl2ss.StreamPort.RM_DEPTH_AHAT: None,
                hl2ss.StreamPort.RM_DEPTH_LONGTHROW: None,
                hl2ss.StreamPort.PHOTO_VIDEO: None,
            }
        except Exception as e:
            logger.log(logging.ERROR, str(e))

        logger.log(logging.INFO, "Configuring producers")
        # Configure Producer
        self.producer = hl2ss_mp.producer()

        try:
            self.producer.configure_rm_vlc(True, self.device_ip, hl2ss.StreamPort.RM_VLC_LEFTFRONT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)
            self.producer.configure_rm_vlc(True, self.device_ip, hl2ss.StreamPort.RM_VLC_LEFTLEFT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)
            self.producer.configure_rm_vlc(True, self.device_ip, hl2ss.StreamPort.RM_VLC_RIGHTFRONT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)
            self.producer.configure_rm_vlc(True, self.device_ip, hl2ss.StreamPort.RM_VLC_RIGHTRIGHT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)

            self.producer.configure_rm_depth_ahat(True, self.device_ip, hl2ss.StreamPort.RM_DEPTH_AHAT,
                                                  hl2ss.ChunkSize.RM_DEPTH_AHAT, AHAT_MODE, AHAT_PROFILE, AHAT_BITRATE)
            self.producer.configure_rm_depth_longthrow(True, self.device_ip, hl2ss.StreamPort.RM_DEPTH_LONGTHROW,
                                                       hl2ss.ChunkSize.RM_DEPTH_LONGTHROW, LT_MODE, LT_FILTER)

            self.producer.configure_pv(True, self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO,
                                       hl2ss.ChunkSize.PHOTO_VIDEO,
                                       PV_MODE, PV_WIDTH, PV_HEIGHT, PV_FRAMERATE, PV_PROFILE, PV_BITRATE, PV_FORMAT)
        except Exception as e:
            logger.log(logging.ERROR, str(e))

        # Start PV
        self.client_rc = hl2ss.tx_rc(self.device_ip, hl2ss.IPCPort.REMOTE_CONFIGURATION)
        hl2ss.start_subsystem_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO)
        self.client_rc.wait_for_pv_subsystem(True)

        # Configure Consumer
        logger.log(logging.INFO, "Configuring consumers")
        self.manager = mp.Manager()
        self.consumer = hl2ss_mp.consumer()
        self.sinks = {}

    def _receive_pv(self):
        codec_video = av.CodecContext.create(hl2ss.get_video_codec_name(VIDEO_PROFILE), 'r')
        pv_client = hl2ss.rx_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO, hl2ss.ChunkSize.PHOTO_VIDEO,
                                hl2ss.StreamMode.MODE_0, FRAME_WIDTH, FRAME_HEIGHT, FRAMERATE, VIDEO_PROFILE,
                                VIDEO_BITRATE)
        pv_client.open()
        logger.log(logging.INFO, "Configuring personal videos")
        while self.rm_pv_enable:
            data = pv_client.get_next_packet()
            self.lock.acquire()
            if not self.tsfirst:
                self.tsfirst = data.timestamp
            self.lock.release()
            for packet in codec_video.parse(data.payload):
                packet.stream = self.stream_video
                packet.pts = data.timestamp - self.tsfirst
                packet.dts = packet.pts
                packet.time_base = self.time_base
                self.packet_queue.put((packet.pts, packet))
        pv_client.close()

    def _receive_mc(self):
        codec_audio = av.CodecContext.create(hl2ss.get_audio_codec_name(AUDIO_PROFILE), 'r')
        mc_client = hl2ss.rx_microphone(self.device_ip, hl2ss.StreamPort.MICROPHONE, hl2ss.ChunkSize.MICROPHONE,
                                        AUDIO_PROFILE)
        mc_client.open()
        logger.log(logging.INFO, "Configuring microphone")
        while self.rm_pv_enable:
            data = mc_client.get_next_packet()
            self.lock.acquire()
            leave = self.tsfirst is None
            self.lock.release()

            if leave:
                continue
            for packet in codec_audio.parse(data.payload):
                packet.stream = self.stream_audio
                packet.pts = data.timestamp - self.tsfirst
                packet.dts = packet.pts
                packet.time_base = self.time_base
                self.packet_queue.put((packet.pts, packet))
        mc_client.close()

    def _mux_audio_video(self):
        logger.log(logging.INFO, "Configuring muxing")
        while self.rm_pv_enable:
            tuple = self.packet_queue.get()
            ts = tuple[0]
            self.container.mux(tuple[1])

    def _display_basic(self, port, data, video_writer, display=False):
        port_name = hl2ss.get_port_name(port)
        if display:
            cv2.imshow(port_name, data.payload)
        if video_writer is not None:
            video_writer.write(data.payload)
            return
        if port == hl2ss.StreamPort.PHOTO_VIDEO:
            cv2.imwrite(os.path.join(self.pv_dir_path,
                                     "{}_{}_{}.png".format(self.recording_id, port_name, data.timestamp)), data.payload)
        else:
            cv2.imwrite(os.path.join(self.vlc_dir_path,
                                     "{}_{}_{}.png".format(self.recording_id, port_name, data.timestamp)), data.payload)

    def _display_depth(self, port, data, video_writer=None, display=False):
        port_name = hl2ss.get_port_name(port)
        if display:
            cv2.imshow(port_name + '-depth', data.payload.depth * 8)  # Scaled for visibility
            cv2.imshow(port_name + '-ab', data.payload.ab / np.max(data.payload.ab))  # Normalized for visibility

        cv2.imwrite(os.path.join(self.depth_dir_path,
                                 "{}_{}_{}.png".format(self.recording_id, port_name, data.timestamp)),
                    data.payload.depth)
        cv2.imwrite(os.path.join(self.ab_dir_path,
                                 "{}_{}_{}.png".format(self.recording_id, port_name, data.timestamp)), data.payload.ab)

    def _start_record_sensor_streams(self, recording_instance: Recording):
        # Initialize all Parameters, Producers, Consumers, Display Map, Writer Map
        logger.log(logging.INFO, "Initializing parameters")
        self._init_params(recording_instance)

        for port in PORTS:
            self.producer.initialize(port, BUFFER_ELEMENTS)
            self.producer.start(port)

        logger.log(logging.INFO, "Started all producers")

        for port in PORTS:
            self.sinks[port] = self.consumer.create_sink(self.producer, port, self.manager, None)
            self.sinks[port].get_attach_response()

        logger.log(logging.INFO, "Created all sinks")

        self.thread_pv = threading.Thread(target=self._receive_pv)
        self.thread_mc = threading.Thread(target=self._receive_mc)
        self.thread_mux = threading.Thread(target=self._mux_audio_video)

        # Personal Video, Microphone audio are captured and placed in packet queue by two different threads
        # Another thread muxes audio and video
        self.threads = [self.thread_pv, self.thread_mc, self.thread_mux]

        # Start all the threads corresponding to each type
        for thread in self.threads:
            thread.start()

        logger.log(logging.INFO, "Begin capturing data")
        # Here we capture data from all the other sources which include following cameras of hololens
        # LEFT-FRONT, LEFT-LEFT, RIGHT-RIGHT, RIGHT-FRONT, AHAT-DEPTH, LT-DEPTH
        while self.rm_vlc_depth_enable:
            if self.tsfirst is None:
                continue
            for port in PORTS:
                data = self.sinks[port].get_most_recent_frame()
                if data is not None:
                    self.display_map[port](port, data, self.writers_map[port])
            cv2.waitKey(1)

    def _stop_record_sensor_streams(self):
        time.sleep(1)

        logger.log(logging.INFO, "Stopping all record streams")
        # Make the shared conditional variables so that process of capturing the frames stops
        self.rm_vlc_depth_enable = False
        self.rm_pv_enable = False

        # Release all the Videowriter instances attached to different ports
        for port in PORTS:
            if self.writers_map[port] is None:
                continue
            self.writers_map[port].release()
        self.container.close()

        # Clear all sinks attached to each port corresponding to cameras
        # LL, LF, RR, RF, AT, LT
        for port in PORTS:
            self.sinks[port].detach()

        logger.log(logging.INFO, "Detached all sinks")

        # Stop all producers attached to each port
        for port in PORTS:
            self.producer.stop(port)

        logger.log(logging.INFO, "Detached all ports")

        # Wait for threads related to - PV, MC, MUXING to stop
        for thread in reversed(self.threads):
            thread.join()

        logger.log(logging.INFO, "Detached all threads")

        # Stopping PV systems
        hl2ss.stop_subsystem_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO)
        self.client_rc.wait_for_pv_subsystem(False)

        logger.log(logging.INFO, "Stopped all systems")

    def start_recording(self, recording_instance: Recording):
        if self._recording:
            logger.log(logging.INFO, "Already a process is recording videos")
            return
        logger.log(logging.INFO, "Starting a process to record videos")
        self._recording = True
        self._start_record_sensor_streams(recording_instance)

    # self._recording_thread = Thread(target=self._start_record_sensor_streams, args=(recording_instance,))
    # self._recording_thread.start()

    def stop_recording(self):
        if not self._recording:
            print("Not recording")
            return
        self._recording = False
        self._stop_record_sensor_streams()
    # if self._recording_thread is not None:
    # 	self._recording_thread.join()


if __name__ == '__main__':
    hl2_service = HololensServiceBak()
    rec = Recording("Coffee", "PL1", "P1", "R1", False)
    rec.set_device_ip('192.168.1.152')
    rec_thread = threading.Thread(target=hl2_service.start_recording, args=(rec,))
    rec_thread.start()
    time.sleep(600)
    hl2_service.stop_recording()
    rec_thread.join()