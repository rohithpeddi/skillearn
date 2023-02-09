import logging
import multiprocessing as mp
import os
import pickle
import queue
import threading
import time
from fractions import Fraction

import cv2
import numpy as np

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

    def _receive_pv(self):
        pv_port = hl2ss.StreamPort.PHOTO_VIDEO
        pv_client = hl2ss.rx_decoded_pv(self.device_ip, pv_port, hl2ss.ChunkSize.PHOTO_VIDEO,
                                        hl2ss.StreamMode.MODE_1, FRAME_WIDTH, FRAME_HEIGHT, FRAMERATE, VIDEO_PROFILE,
                                        VIDEO_BITRATE, VIDEO_DECODE)
        pv_client.open()
        logger.log(logging.INFO, "Configuring PhotoVideo")
        pv_pose = []
        while self.rm_enable:
            data = pv_client.get_next_packet()
            pv_pose.append([data.timestamp, data.pose])
            self._write_frame_async(pv_port, data, self.async_storage_map[pv_port])

        with open(os.path.join(self.rec_data_dir, 'pv_pose.pkl'), 'wb') as f:
            pickle.dump(pv_pose, f)
        print(f'pv_pose: {len(pv_pose)}')
        pv_client.close()

    def _receive_vlc(self, vlc_port):
        port_name = hl2ss.get_port_name(vlc_port)
        vlc_client = hl2ss.rx_decoded_rm_vlc(self.device_ip, vlc_port,
                                             hl2ss.ChunkSize.RM_VLC,
                                             VLC_MODE, VLC_PROFILE, VLC_BITRATE)
        vlc_client.open()
        logger.log(logging.INFO, "Configuring VLC")
        vlc_pose = []
        while self.rm_enable:
            data = vlc_client.get_next_packet()
            vlc_pose.append([data.timestamp, data.pose])
            self._write_frame_async(vlc_port, data, self.async_storage_map[vlc_port])
        # np.savez(os.path.join(self.port_dir_map[vlc_port], 'vlc_pose'), vlc_pose)
        with open(os.path.join(self.rec_data_dir, f'{port_name}_pose.pkl'), 'wb') as f:
            pickle.dump(vlc_pose, f)
        print(f'{port_name}_pose: {len(vlc_pose)}')
        vlc_client.close()

    def _receive_depth_ahat(self):
        depth_port = hl2ss.StreamPort.RM_DEPTH_AHAT
        ahat_client = hl2ss.rx_decoded_rm_depth_ahat(self.device_ip, depth_port,
                                                     hl2ss.ChunkSize.RM_DEPTH_AHAT,
                                                     AHAT_MODE, AHAT_PROFILE, AHAT_BITRATE)
        ahat_client.open()
        logger.log(logging.INFO, "Configuring Depth AHaT")
        while self.rm_enable:
            data = ahat_client.get_next_packet()
            self._write_depth_async(depth_port, data, self.async_storage_map[depth_port])
        ahat_client.close()

    def _receive_depth_longthrow(self):
        depth_port = hl2ss.StreamPort.RM_DEPTH_LONGTHROW
        longthrow_client = hl2ss.rx_decoded_rm_depth_longthrow(self.device_ip, depth_port,
                                                               hl2ss.ChunkSize.RM_DEPTH_LONGTHROW,
                                                               LT_MODE, LT_FILTER)
        longthrow_client.open()
        logger.log(logging.INFO, "Configuring Depth longthrow")
        while self.rm_enable:
            data = longthrow_client.get_next_packet()
            self._write_depth_async(depth_port, data, self.async_storage_map[depth_port])
        longthrow_client.close()

    def _receive_microphone(self):
        audio_port = hl2ss.StreamPort.MICROPHONE
        audio_client = hl2ss.rx_decoded_microphone(self.device_ip, audio_port,
                                                   hl2ss.ChunkSize.MICROPHONE,
                                                   AUDIO_PROFILE)
        audio_client.open()
        logger.log(logging.INFO, "Configuring Audio Microphone")
        audio_data = []
        while self.rm_enable:
            data = audio_client.get_next_packet()
            audio_data.append([data.timestamp, data.payload])
        with open(os.path.join(self.port_dir_map[audio_port], f'audio_data.pkl'), 'wb') as f:
            pickle.dump(audio_data, f)
        print(f'audio_data: {len(audio_data)}')
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
        with open(os.path.join(self.port_dir_map[spatial_port], f'spatial_data.pkl'), 'wb') as f:
            pickle.dump(spatial_data, f)
        print(f'spatial_data: {len(spatial_data)}')
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
        with open(os.path.join(self.port_dir_map[imu_port], f'{port_name}_data.pkl'), 'wb') as f:
            pickle.dump(imu_data, f)
        print(f'{port_name}_data: {len(imu_data)}')
        imu_client.close()

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

        self.writer_map = {
            hl2ss.StreamPort.RM_VLC_LEFTFRONT: self._write_frame_async,
            hl2ss.StreamPort.RM_VLC_LEFTLEFT: self._write_frame_async,
            hl2ss.StreamPort.RM_VLC_RIGHTFRONT: self._write_frame_async,
            hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: self._write_frame_async,

            hl2ss.StreamPort.RM_DEPTH_AHAT: self._write_depth_async,
            hl2ss.StreamPort.RM_DEPTH_LONGTHROW: self._write_depth_async,

            hl2ss.StreamPort.PHOTO_VIDEO: self._write_frame_async,
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
        pool_per_stream = int(mp.cpu_count() / total_streams)
        pool_per_stream = max(2, pool_per_stream)
        try:
            self.async_storage_map = {
                hl2ss.StreamPort.RM_VLC_LEFTFRONT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_VLC_LEFTLEFT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_VLC_RIGHTFRONT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_VLC_RIGHTRIGHT: mp.Pool(pool_per_stream),

                hl2ss.StreamPort.RM_DEPTH_AHAT: mp.Pool(pool_per_stream),
                hl2ss.StreamPort.RM_DEPTH_LONGTHROW: mp.Pool(pool_per_stream),

                hl2ss.StreamPort.PHOTO_VIDEO: mp.Pool(4),
            }
        except Exception as e:
            logger.log(logging.ERROR, str(e))

        # Start PV
        self.client_rc = hl2ss.tx_rc(self.device_ip, hl2ss.IPCPort.REMOTE_CONFIGURATION)
        hl2ss.start_subsystem_pv(self.device_ip, hl2ss.StreamPort.PHOTO_VIDEO)
        self.client_rc.wait_for_pv_subsystem(True)

    def _write_frame_async(self, port, data, writer_pool: mp.Pool, display=False):
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

        self.thread_pv = threading.Thread(target=self._receive_pv)
        self.thread_mc = threading.Thread(target=self._receive_microphone)

        self.thread_vlc_ll = threading.Thread(target=self._receive_vlc, args=(hl2ss.StreamPort.RM_VLC_LEFTLEFT,))
        self.thread_vlc_lf = threading.Thread(target=self._receive_vlc, args=(hl2ss.StreamPort.RM_VLC_LEFTFRONT,))
        self.thread_vlc_rf = threading.Thread(target=self._receive_vlc, args=(hl2ss.StreamPort.RM_VLC_RIGHTFRONT,))
        self.thread_vlc_rr = threading.Thread(target=self._receive_vlc, args=(hl2ss.StreamPort.RM_VLC_RIGHTRIGHT,))

        self.thread_ahat = threading.Thread(target=self._receive_depth_ahat)
        self.thread_longthrow = threading.Thread(target=self._receive_depth_longthrow)

        self.thread_spatial = threading.Thread(target=self._receive_spatial)
        self.thread_imu_acc = threading.Thread(target=self._receive_imu, args=(hl2ss.StreamPort.RM_IMU_ACCELEROMETER,))
        self.thread_imu_gyro = threading.Thread(target=self._receive_imu, args=(hl2ss.StreamPort.RM_IMU_GYROSCOPE,))
        self.thread_imu_mag = threading.Thread(target=self._receive_imu, args=(hl2ss.StreamPort.RM_IMU_MAGNETOMETER,))

        # Threads for each stream
        self.threads = [self.thread_pv,
                        self.thread_mc,
                        self.thread_vlc_ll, self.thread_vlc_lf, self.thread_vlc_rf, self.thread_vlc_rr,
                        self.thread_ahat, self.thread_longthrow,
                        self.thread_spatial,
                        self.thread_imu_acc, self.thread_imu_gyro, self.thread_imu_mag,
                        ]

        # Start all the threads corresponding to each type
        for thread in self.threads:
            thread.start()

    def _stop_record_sensor_streams(self):
        time.sleep(1)

        logger.log(logging.INFO, "Stopping all record streams")
        # Make the shared conditional variables so that process of capturing the frames stops
        self.rm_enable = False

        # Start all the threads corresponding to each type
        for thread in self.threads:
            thread.join()

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
    rec = Recording("Coffee", "P1", "K1", "R1", False)
    rec.set_device_ip('192.168.10.133')
    rec_thread = threading.Thread(target=hl2_service.start_recording, args=(rec,))
    rec_thread.start()
    time.sleep(10)
    hl2_service.stop_recording()
    rec_thread.join()
