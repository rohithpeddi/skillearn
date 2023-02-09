import logging
import multiprocessing as mp
import os
import queue
import threading
import time
from fractions import Fraction

import cv2
import numpy as np

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


class HololensService:

    def __init__(self):
        self.rm_enable = True
        self.lock = threading.Lock()
        self.packet_queue = queue.PriorityQueue()
        self.time_base = Fraction(1, hl2ss.TimeBase.HUNDREDS_OF_NANOSECONDS)

        self._recording = False
        self._recording_thread = None

    def _init_params(self, rec: Recording):
        self.device_ip = rec.device_ip
        self.rec_id = f"{rec.activity}_{rec.place_id}_{rec.person_id}_{rec.rec_number}"
        self.data_dir = "../../../data"
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
            hl2ss.StreamPort.PERSONAL_VIDEO: os.path.join(self.rec_data_dir, 'pv'),
            hl2ss.StreamPort.MICROPHONE: os.path.join(self.rec_data_dir, 'mc'),
            hl2ss.StreamPort.SPATIAL_INPUT: os.path.join(self.rec_data_dir, 'spatial'),
        }

        for port in PORTS:
            if port == hl2ss.StreamPort.RM_DEPTH_AHAT or port == hl2ss.StreamPort.RM_DEPTH_LONGTHROW:
                create_directories(self.port_dir_map[port]['ab'])
                create_directories(self.port_dir_map[port]['depth'])
            else:
                create_directories(self.port_dir_map[port])

        self.writer_map = {
            hl2ss.StreamPort.RM_VLC_LEFTFRONT: self._write_frame_async,
            hl2ss.StreamPort.RM_VLC_LEFTLEFT: self._write_frame_async,
            hl2ss.StreamPort.RM_VLC_RIGHTFRONT: self._write_frame_async,
            hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: self._write_frame_async,

            hl2ss.StreamPort.RM_DEPTH_AHAT: self._write_depth_async,
            hl2ss.StreamPort.RM_DEPTH_LONGTHROW: self._write_depth_async,

            hl2ss.StreamPort.PERSONAL_VIDEO: self._write_frame_async,
            hl2ss.StreamPort.MICROPHONE: self._write_audio_async,

            hl2ss.StreamPort.SPATIAL_INPUT: self._write_spatial_async,
        }

        total_streams = 8  # (PV, Pose), Audio, Depth, ((VLC, Pose) * 4), MLC
        pool_per_stream = int(mp.cpu_count() / total_streams)
        pool_per_stream = max(1, pool_per_stream)
        try:
            self.async_storage_map = {
                hl2ss.StreamPort.RM_VLC_LEFTFRONT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_VLC_LEFTLEFT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_VLC_RIGHTFRONT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: mp.Pool(pool_per_stream),

                hl2ss.StreamPort.RM_DEPTH_AHAT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_DEPTH_LONGTHROW: mp.Pool(pool_per_stream),

                hl2ss.StreamPort.PERSONAL_VIDEO: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.MICROPHONE: mp.Pool(pool_per_stream),

                hl2ss.StreamPort.SPATIAL_INPUT: mp.Pool(pool_per_stream),
            }
        except Exception as e:
            logger.log(logging.ERROR, str(e))

        logger.log(logging.INFO, "Configuring producers")
        # Configure Producer
        self.producer = hl2ss_mp.producer()

        try:
            # VLC
            self.producer.configure_rm_vlc(True, self.device_ip,
                                           hl2ss.StreamPort.RM_VLC_LEFTFRONT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)
            self.producer.configure_rm_vlc(True, self.device_ip,
                                           hl2ss.StreamPort.RM_VLC_LEFTLEFT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)
            self.producer.configure_rm_vlc(True, self.device_ip,
                                           hl2ss.StreamPort.RM_VLC_RIGHTFRONT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)
            self.producer.configure_rm_vlc(True, self.device_ip,
                                           hl2ss.StreamPort.RM_VLC_RIGHTRIGHT,
                                           hl2ss.ChunkSize.RM_VLC,
                                           VLC_MODE, VLC_PROFILE, VLC_BITRATE)
            # Depth
            self.producer.configure_rm_depth_ahat(True, self.device_ip,
                                                  hl2ss.StreamPort.RM_DEPTH_AHAT,
                                                  hl2ss.ChunkSize.RM_DEPTH_AHAT,
                                                  AHAT_MODE, AHAT_PROFILE, AHAT_BITRATE)
            self.producer.configure_rm_depth_longthrow(True, self.device_ip,
                                                       hl2ss.StreamPort.RM_DEPTH_LONGTHROW,
                                                       hl2ss.ChunkSize.RM_DEPTH_LONGTHROW,
                                                       LT_MODE, LT_FILTER)
            # PhotoVideo
            self.producer.configure_pv(True, self.device_ip,
                                       hl2ss.StreamPort.PERSONAL_VIDEO,
                                       hl2ss.ChunkSize.PERSONAL_VIDEO,
                                       PV_MODE, PV_WIDTH, PV_HEIGHT, PV_FRAMERATE,
                                       PV_PROFILE, PV_BITRATE, PV_FORMAT)

            # Audio
            self.producer.configure_microphone(True, self.device_ip,
                                               hl2ss.StreamPort.MICROPHONE,
                                               hl2ss.ChunkSize.MICROPHONE,
                                               MC_PROFILE)
            # Spatial
            self.producer.configure_si(self.device_ip,
                                       hl2ss.StreamPort.SPATIAL_INPUT,
                                       hl2ss.ChunkSize.SPATIAL_INPUT, )
        except Exception as e:
            logger.log(logging.ERROR, str(e))

        # Start PV
        self.client_rc = hl2ss.tx_rc(self.device_ip, hl2ss.IPCPort.REMOTE_CONFIGURATION)
        hl2ss.start_subsystem_pv(self.device_ip, hl2ss.StreamPort.PERSONAL_VIDEO)
        self.client_rc.wait_for_pv_subsystem(True)

        # Configure Consumer
        logger.log(logging.INFO, "Configuring consumers")
        self.manager = mp.Manager()
        self.consumer = hl2ss_mp.consumer()
        self.sinks = {}

    def _write_frame_async(self, port, data, writer_pool: mp.Pool, display=False):
        port_name = hl2ss.get_port_name(port)
        dir_path = self.port_dir_map[port]
        file_path = os.path.join(dir_path, f"{self.rec_id}_{port_name}_{data.timestamp}.jpg")
        if display:
            cv2.imshow(port_name, data.payload)
            cv2.waitKey(1)
        if writer_pool is not None:
            writer_pool.apply_async(cv2.imwrite(file_path, data.payload))

    def _write_depth_async(self, port, data, writer_pool: mp.Pool, display=False):
        port_name = hl2ss.get_port_name(port)
        dir_path_ab = self.port_dir_map[port]['ab']
        dir_path_depth = self.port_dir_map[port]['depth']
        file_path_ab = os.path.join(dir_path_ab, f"{self.rec_id}_{port_name}_{data.timestamp}_ab.png")
        file_path_depth = os.path.join(dir_path_depth, f"{self.rec_id}_{port_name}_{data.timestamp}_depth.png")
        if display:
            cv2.imshow(port_name + '-depth', data.payload.depth * 8)  # Scaled for visibility
            cv2.imshow(port_name + '-ab', data.payload.ab / np.max(data.payload.ab))  # Normalized for visibility
            cv2.waitKey(1)
        if writer_pool is not None:
            writer_pool.apply_async(cv2.imwrite(file_path_ab, data.payload.ab))
            writer_pool.apply_async(cv2.imwrite(file_path_depth, data.payload.depth))

    def _write_spatial_async(self, port, data, writer_pool: mp.Pool, display=False):
        pass

    def _write_audio_async(self, port, data, writer_pool: mp.Pool, display=False):
        pass

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

        logger.log(logging.INFO, "Begin capturing data")
        # Here we capture data from all the other sources which include following cameras of hololens
        # LEFT-FRONT, LEFT-LEFT, RIGHT-RIGHT, RIGHT-FRONT, AHAT-DEPTH, LT-DEPTH
        while self.rm_enable:
            for port in PORTS:
                data = self.sinks[port].get_most_recent_frame()
                if data is not None:
                    self.writer_map[port](port, data, self.async_storage_map[port])
            cv2.waitKey(1)

    def _stop_record_sensor_streams(self):
        time.sleep(1)

        logger.log(logging.INFO, "Stopping all record streams")
        # Make the shared conditional variables so that process of capturing the frames stops
        self.rm_enable = False

        # Clear all sinks attached to each port corresponding to cameras
        # LL, LF, RR, RF, AT, LT
        for port in PORTS:
            self.sinks[port].detach()

        logger.log(logging.INFO, "Detached all sinks")

        # Stop all producers attached to each port
        for port in PORTS:
            self.producer.stop(port)

        # Release all the pools instances attached to different ports
        for port in PORTS:
            if self.async_storage_map[port] is None:
                continue
            self.async_storage_map[port].close()

        logger.log(logging.INFO, "Detached all ports")

        # Stopping PV systems
        hl2ss.stop_subsystem_pv(self.device_ip, hl2ss.StreamPort.PERSONAL_VIDEO)
        self.client_rc.wait_for_pv_subsystem(False)

        logger.log(logging.INFO, "Stopped all systems")

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


if __name__ == '__main__':
    hl2_service = HololensService()
    rec = Recording("Coffee", "P5", "K1", "R1", False)
    rec.set_device_ip('10.176.140.28')
    rec_thread = threading.Thread(target=hl2_service.start_recording, args=(rec,))
    rec_thread.start()
    time.sleep(5.0)
    hl2_service.stop_recording()
    rec_thread.join()
