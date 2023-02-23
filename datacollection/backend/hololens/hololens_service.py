import logging
import os
import threading

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
		stream_redis_client = redis.Redis(self.redis_pool)
		
		while self.enable_streams:
			stream_data = stream_client.get_next_packet_packed()
			stream_redis_client.lpush(stream_port, stream_data)
		
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
		self._opened_file = open(file_path, 'wb')
	
	def write(self, stream_packet):
		self._opened_file.write(stream_packet)
	
	def close(self):
		self._opened_file.close()


class Consumer:
	
	def __init__(self, redis_pool, recording, port_to_stream, active_streams, port_to_dir, port_to_writer):
		self.redis_pool = redis_pool
		self.redis_pool = redis_pool
		self.recording = recording
		
		self.port_to_stream = port_to_stream
		self.active_streams = active_streams
		self.port_to_dir = port_to_dir
		self.port_to_writer = port_to_writer
		
		self.store_frame_as_binary = False
		self.enable_streams = True
		self.stream_threads = []
	
	def _process_stream_data(self, stream_port, stream_data, **kwargs):
		if stream_port == StreamPort.PHOTO_VIDEO:
			kwargs[PV_WRITER].write(stream_data)
		elif stream_port == StreamPort.RM_DEPTH_AHAT:
			kwargs[DEPTH_AHAT_WRITER].write(stream_data)
		elif stream_port == StreamPort.MICROPHONE:
			kwargs[MICROPHONE_WRITER].write(stream_data)
		elif stream_port == StreamPort.SPATIAL_INPUT:
			kwargs[SPATIAL_WRITER].write(stream_data)
	
	def _process_stream(self, stream_port):
		logger.log(logging.INFO,
		           f"Configuring {self.port_to_stream[stream_port]} Consumer for recording {self.recording.__str__()}")
		
		# Create a redis client and push the stream data to the queue named stream_port continuously
		stream_redis_client = redis.Redis(self.redis_pool)
		done_processing = False
		
		# Filewriter function that dumps the raw data available into a file named after the recording
		stream_file_path = os.path.join(self.port_to_dir[stream_port],
		                                f'{self.recording.get_recording_id()}_{self.port_to_stream[stream_port]}.bin')
		stream_writer = FileWriter(stream_file_path)
		kwargs = {
			self.port_to_writer[stream_port]: stream_writer
		}
		
		while True:
			stream_data = stream_redis_client.brpop(stream_port, timeout=3)
			
			if stream_data is None:
				# Finished processing of the streams
				if not self.enable_streams:
					done_processing = True
					logger.log(logging.INFO,
					           f"Finished {self.port_to_stream[stream_port]} Consumer processing for recording {self.recording.__str__()}")
				break
			else:
				self._process_stream_data(stream_port, stream_data, **kwargs)
		
		if not done_processing:
			# Might be a temporary hold on the data, can come back in sometime
			# So make the process recursive
			logger.log(logging.INFO,
			           f"Reached Timeout {self.port_to_stream[stream_port]} Consumer but stream data is not yet done, so initialized processing again")
			self._process_stream(stream_port)
		else:
			stream_writer.close()
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
		self._recording = True
		self.lock = threading.Lock()
		
		self.redis_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, max_connections=REDIS_MAX_CONNECTIONS)
	
	def _init_params(self, recording: Recording):
		self.recording = recording
		self.device_ip = self.recording.device_ip
		self.device_name = get_hostname(self.device_ip)
		
		self.data_dir = "../../../data"
		self.rec_data_dir = os.path.join(self.data_dir, self.recording.get_recording_id())
		self.port_to_dir = {
			StreamPort.RM_DEPTH_AHAT: {
				'ab': os.path.join(self.rec_data_dir, 'dep_ahat_ab'),
				'depth': os.path.join(self.rec_data_dir, 'dep_ahat_depth'),
			},
			StreamPort.PHOTO_VIDEO: os.path.join(self.rec_data_dir, 'pv'),
			StreamPort.MICROPHONE: os.path.join(self.rec_data_dir, 'mc'),
			StreamPort.SPATIAL_INPUT: os.path.join(self.rec_data_dir, 'spatial'),
			StreamPort.RM_IMU_ACCELEROMETER: os.path.join(self.rec_data_dir, 'imu_acc'),
			StreamPort.RM_IMU_GYROSCOPE: os.path.join(self.rec_data_dir, 'imu_gyro'),
			StreamPort.RM_IMU_MAGNETOMETER: os.path.join(self.rec_data_dir, 'imu_mag'),
		}
		
		self.port_to_stream = {
			StreamPort.RM_DEPTH_AHAT: "depth",
			StreamPort.PHOTO_VIDEO: "pv",
			StreamPort.MICROPHONE: "mc",
			StreamPort.SPATIAL_INPUT: "si",
		}
		
		self.active_streams = [StreamPort.RM_DEPTH_AHAT, StreamPort.PHOTO_VIDEO, StreamPort.MICROPHONE,
		                       StreamPort.SPATIAL_INPUT]
		
		for port in self.active_streams:
			if port == StreamPort.RM_DEPTH_AHAT:
				create_directories(self.port_to_dir[port]['ab'])
				create_directories(self.port_to_dir[port]['depth'])
			else:
				create_directories(self.port_to_dir[port])
		
		# Start PV
		self.client_rc = ipc_rc(self.device_ip, IPCPort.REMOTE_CONFIGURATION)
		start_subsystem_pv(self.device_ip, StreamPort.PHOTO_VIDEO)
		self.client_rc.wait_for_pv_subsystem(True)
	
	def _start_record_sensor_streams(self, recording_instance: Recording):
		# Initialize all Parameters, Producers, Consumers, Display Map, Writer Map
		logger.log(logging.INFO, "Initializing parameters")
		self._init_params(recording_instance)
		
		self.producer = Producer(self.redis_pool, self.recording, self.port_to_stream, self.active_streams)
		self.producer.start_processing_streams()
		
		self.consumer = Consumer(self.redis_pool, self.recording, self.port_to_stream, self.active_streams,
		                         self.port_to_dir, self.port_to_writer)
		self.consumer.start_processing_streams()
		
		while self.rm_enable:
			time.sleep(60)
	
	def _stop_record_sensor_streams(self):
		
		logger.log(logging.INFO, "Stopping all record streams")
		
		self.producer.stop_processing_streams()
		self.consumer.stop_processing_streams()
		
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
	ip_address = '10.176.198.58'
	hl2_service = HololensService()
	rec = Recording("Coffee", "PL1", "P1", "R2", False)
	rec.set_device_ip(ip_address)
	rec_thread = threading.Thread(target=hl2_service.start_recording, args=(rec,))
	rec_thread.start()
	start_mrc(ip_address)
	client = hl2ss.ipc_rc(ip_address, hl2ss.IPCPort.REMOTE_CONFIGURATION)
	utc_offset = client.get_utc_offset(32)
	print('QPC timestamp to UTC offset is {offset} hundreds of nanoseconds'.format(offset=utc_offset))
	print("Recording Started")
	sleep_min = 1
	for min_done in range(sleep_min):
		print("Minutes done {}".format(min_done))
		time.sleep(10)
	
	hl2_service.stop_recording()
	stop_mrc(ip_address)
	print("Recording Stopped")
	rec_thread.join()
