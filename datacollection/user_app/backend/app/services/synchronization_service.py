import os
import pickle
import shutil
import time
import zipfile
from typing import List

import cv2

from ..hololens import hl2ss
from ..models.recording import Recording
from ..post_processing.compress_data_service import CompressDataService
from ..utils.constants import Synchronization_Constants as const


def create_directories(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)


def write_pickle_data(pickle_data, pickle_file_path):
	with open(pickle_file_path, 'wb') as pickle_file:
		pickle.dump(pickle_data, pickle_file)


def read_stream_pkl_data(stream_pkl_file_path):
	pkl_frames = []
	with open(stream_pkl_file_path, 'rb') as stream_file:
		while stream_file.seekable():
			try:
				pkl_frames.append(pickle.load(stream_file))
			except EOFError:
				break
	return pkl_frames


def get_ts_to_stream_frame(
		stream_directory,
		stream_extension,
		ts_index=-1
):
	stream_extension_length = len(stream_extension)
	stream_frames = [frame for frame in os.listdir(stream_directory) if frame.endswith(stream_extension)]
	
	def get_ts_from_stream_file_name(stream_file_name):
		_splits = (stream_file_name[:-stream_extension_length].split("_"))
		if _splits[ts_index] == "depth" or _splits[ts_index] == "ab":
			return int(_splits[ts_index - 1])
		return int(_splits[ts_index])
	
	stream_frames = sorted(stream_frames, key=lambda x: get_ts_from_stream_file_name(x))
	
	ts_to_stream_frame = {}
	for stream_frame in stream_frames:
		ts = get_ts_from_stream_file_name(stream_frame)
		ts_to_stream_frame[ts] = stream_frame
	
	return ts_to_stream_frame


def extract_zip_file(zip_file_path, output_directory):
	print("Extracting zip file: ", zip_file_path)
	start_time = time.time()
	with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
		zip_ref.extractall(output_directory)
	print("Extracting zip file took: ", time.time() - start_time)


def make_video(images_folder, video_name):
	images = [img for img in os.listdir(images_folder) if img.endswith(".jpg")]
	images = sorted(images, key=lambda x: int((x[:-4].split("-"))[-1]))
	
	frame = cv2.imread(os.path.join(images_folder, images[0]))
	height, width, layers = frame.shape
	
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	# video = cv2.VideoWriter(video_name, 0, 30, (width, height))
	video = cv2.VideoWriter(video_name, fourcc, 30, (width, height))
	
	for image in images:
		video.write(cv2.imread(os.path.join(images_folder, image)))
	
	cv2.destroyAllWindows()
	video.release()


class SynchronizationServiceV2:
	
	def __init__(
			self,
			data_parent_directory: str,
			recording: Recording,
			base_stream: str,
			synchronize_streams: List[str],
	):
		self.base_stream = base_stream
		self.synchronize_streams = synchronize_streams
		self.recording = recording
		self.recording_id = self.recording.get_recording_id()
		self.data_recording_directory = os.path.join(data_parent_directory, self.recording_id)
		
		self.raw_data_directory = os.path.join(self.data_recording_directory, const.RAW)
		self.sync_data_directory = os.path.join(self.data_recording_directory, const.SYNC)
		create_directories(self.sync_data_directory)
		
		self.raw_hololens_info_file = os.path.join(self.raw_data_directory, const.HOLOLENS_INFO_FILE_NAME)
		
		self.raw_base_stream_directory = os.path.join(self.raw_data_directory, self.base_stream)
		self.sync_base_stream_directory = os.path.join(self.sync_data_directory, self.base_stream)
		
		self.ts_to_base_stream_frame = None
		self.base_stream_keys = None
		
		self.pv_stream_suffix = "color-%06d.jpg"
		self.depth_stream_suffix = "depth-%06d.png"
		self.ab_stream_suffix = "ab-%06d.png"
		
		self.num_of_frames = 0
		self.depth_mode = None
		self.depth_width = None
		self.depth_height = None
		self.pv_width = None
		self.pv_height = None
		self.meta_yaml_data = {}
		
		self.device_id = self._get_device_id()
	
	def is_synchronizable(self):
		if not os.path.exists(self.raw_base_stream_directory):
			return False
		for stream in self.synchronize_streams:
			if not os.path.exists(os.path.join(self.raw_data_directory, stream)):
				return False
		return True
	
	def _get_device_id(self):
		with open(self.raw_hololens_info_file, 'r') as f:
			hololens_info_data = f.readlines()
		for line in hololens_info_data:
			if line.startswith("Hololens2 Name"):
				return line.split(":")[1].strip()
	
	def get_image_characteristics(self, image_path):
		image = cv2.imread(image_path)
		return image.shape[1], image.shape[0]
	
	def get_ts_pkl_frame_map(self, stream_pkl_file_path):
		ts_to_stream_payload = {}
		pkl_frames = read_stream_pkl_data(stream_pkl_file_path)
		for pkl_frame in pkl_frames:
			ts, payload = pkl_frame if type(pkl_frame) is tuple else (pkl_frame.ts, pkl_frame.payload)
			if type(payload) is bytearray:
				payload = hl2ss.unpack_si(payload)
			ts_to_stream_payload[ts] = payload
		return ts_to_stream_payload
	
	def create_sync_stream_pkl_data(self, stream_pkl_file_path, sync_stream_output_directory, base_ts_to_stream_ts):
		# 1. Load pickle file data into a dictionary
		ts_to_stream_payload = self.get_ts_pkl_frame_map(stream_pkl_file_path)
		
		# 2. Use the base_stream_keys and loaded pickle file data to synchronize them
		synced_ts_to_stream_payload = {}
		for base_stream_key in self.base_stream_keys:
			stream_ts = base_ts_to_stream_ts[base_stream_key]
			stream_payload = ts_to_stream_payload[stream_ts]
			synced_ts_to_stream_payload[base_stream_key] = (stream_ts, stream_payload)
		write_pickle_data(synced_ts_to_stream_payload, sync_stream_output_directory)
	
	def create_sync_stream_frames(
			self,
			stream_directory,
			stream_extension,
			sync_stream_output_directory,
			stream_suffix,
			base_ts_to_stream_ts
	):
		ts_to_stream_frame = get_ts_to_stream_frame(stream_directory, stream_extension)
		for base_stream_counter, base_stream_key in enumerate(self.base_stream_keys):
			stream_ts = base_ts_to_stream_ts[base_stream_key]
			shutil.copy(
				os.path.join(stream_directory, ts_to_stream_frame[stream_ts]),
				os.path.join(sync_stream_output_directory, stream_suffix % base_stream_counter)
			)
		return
	
	def get_stream_keys_from_dir(self, stream_directory, stream_extension, ts_index):
		ts_to_stream_frame = get_ts_to_stream_frame(stream_directory, stream_extension, ts_index)
		return ts_to_stream_frame.keys()
	
	def get_stream_keys_from_pkl(self, pkl_file_path):
		ts_to_stream_frame_pkl = self.get_ts_pkl_frame_map(pkl_file_path)
		return ts_to_stream_frame_pkl.keys()
	
	def create_base_ts_to_stream_ts_map(self, get_stream_keys_fn, params):
		stream_keys = sorted(get_stream_keys_fn(**params))
		base_ts_to_stream_ts = {}
		base_idx_to_stream_idx = {}
		
		for base_stream_counter, base_stream_key in enumerate(self.base_stream_keys):
			stream_ts_idx = 0 if base_stream_counter == 0 else base_idx_to_stream_idx[base_stream_counter - 1]
			best_base_ts_stream_ts_distance = abs(base_stream_key - stream_keys[stream_ts_idx])
			
			while stream_ts_idx < len(stream_keys) and abs(
					base_stream_key - stream_keys[stream_ts_idx]) <= best_base_ts_stream_ts_distance:
				best_base_ts_stream_ts_distance = abs(base_stream_key - stream_keys[stream_ts_idx])
				stream_ts_idx += 1
			
			stream_ts_idx -= 1
			stream_ts = stream_keys[stream_ts_idx]
			print("Base Stream Key: %d, Stream Timestamp: %d" % (base_stream_key, stream_ts))
			base_idx_to_stream_idx[base_stream_counter] = stream_ts_idx
			
			if abs(base_stream_key - stream_ts) > 1e8:
				print("Difference between base stream key and stream timestamp is greater than 1 second")
				base_ts_to_stream_ts[base_stream_key] = None
			else:
				base_ts_to_stream_ts[base_stream_key] = stream_ts
		
		return base_ts_to_stream_ts
	
	def sync_streams(self):
		# meta.yaml file data
		self.meta_yaml_data["device_id"] = self.device_id
		# 1. Create base stream keys used to synchronize the rest of the data
		frames_zip_file_path = os.path.join(self.raw_base_stream_directory, const.FRAMES_ZIP)
		raw_base_stream_frames_dir = os.path.join(self.raw_base_stream_directory, const.FRAMES)
		if os.path.exists(frames_zip_file_path) and not os.path.exists(raw_base_stream_frames_dir):
			extract_zip_file(frames_zip_file_path, raw_base_stream_frames_dir)

		self.ts_to_base_stream_frame = get_ts_to_stream_frame(raw_base_stream_frames_dir, const.JPEG_EXTENSION, -1)
		self.base_stream_keys = sorted(self.ts_to_base_stream_frame.keys())
		self.num_of_frames = len(self.base_stream_keys)
		self.meta_yaml_data["num_of_frames"] = self.num_of_frames
		
		sample_base_stream_frame_path = os.path.join(
			raw_base_stream_frames_dir,
			os.listdir(raw_base_stream_frames_dir)[0]
		)

		self.pv_width, self.pv_height = self.get_image_characteristics(sample_base_stream_frame_path)
		self.meta_yaml_data["pv_width"] = self.pv_width
		self.meta_yaml_data["pv_height"] = self.pv_height
		
		sync_base_stream_frames_dir = os.path.join(self.sync_base_stream_directory, const.FRAMES)
		create_directories(sync_base_stream_frames_dir)
		
		# 2. Copy base stream frames into the sync output folder
		print("Copying base stream frames into the sync output folder")
		for base_stream_counter, base_stream_key in enumerate(self.base_stream_keys):
			src_file = os.path.join(raw_base_stream_frames_dir, self.ts_to_base_stream_frame[base_stream_key])
			dest_file = os.path.join(sync_base_stream_frames_dir, self.pv_stream_suffix % base_stream_counter)
			shutil.copy(src_file, dest_file)
		print("Done copying base stream frames into the sync output folder")
		
		# Synchronize PV Pose
		pv_pose_pkl = f'{self.recording.id}_pv_pose.pkl'
		pv_pose_file_path = os.path.join(self.raw_base_stream_directory, pv_pose_pkl)
		sync_pv_pose_file_path = os.path.join(self.sync_base_stream_directory, pv_pose_pkl)
		
		print("Copying PV Pose into the sync output folder")
		shutil.copy(pv_pose_file_path, sync_pv_pose_file_path)
		print("Done copying PV Pose into the sync output folder")
		
		recording_base_stream_mp4_file_path = os.path.join(self.raw_base_stream_directory, f"{self.recording.id}.mp4")
		if not os.path.exists(recording_base_stream_mp4_file_path):
			print("Recording base stream mp4 file does not exist")
			print("Creating recording base stream mp4 file")
			make_video(raw_base_stream_frames_dir, recording_base_stream_mp4_file_path)
			print("Done creating recording base stream mp4 file")
			
		for stream_name in self.synchronize_streams:
			if stream_name == const.DEPTH_AHAT:
				# Files and directories
				raw_depth_parent_directory = os.path.join(self.raw_data_directory, const.DEPTH_AHAT)
				sync_depth_parent_directory = os.path.join(self.sync_data_directory, const.DEPTH_AHAT)
				create_directories(sync_depth_parent_directory)
				
				depth_ahat_pkl = f'{self.recording.id}_depth_ahat_pose.pkl'
				raw_depth_pose_file_path = os.path.join(raw_depth_parent_directory, depth_ahat_pkl)
				sync_depth_pose_file_path = os.path.join(sync_depth_parent_directory, depth_ahat_pkl)
				
				raw_depth_data_directory = os.path.join(raw_depth_parent_directory, const.DEPTH)
				depth_frames_zip_file_path = os.path.join(raw_depth_parent_directory, const.DEPTH_ZIP)
				if os.path.exists(depth_frames_zip_file_path) and not os.path.exists(raw_depth_data_directory):
					print("Extracting depth frames zip file")
					extract_zip_file(depth_frames_zip_file_path, raw_depth_data_directory)
					print("Done extracting depth frames zip file")
				
				sync_depth_data_directory = os.path.join(sync_depth_parent_directory, const.DEPTH)
				create_directories(sync_depth_data_directory)
				
				raw_depth_ab_directory = os.path.join(raw_depth_parent_directory, const.AB)
				ab_frames_zip_file_path = os.path.join(raw_depth_parent_directory, const.AB_ZIP)
				if os.path.exists(depth_frames_zip_file_path) and not os.path.exists(raw_depth_ab_directory):
					print("Extracting ab frames zip file")
					extract_zip_file(ab_frames_zip_file_path, raw_depth_ab_directory)
					print("Done extracting ab frames zip file")
				
				sync_depth_ab_directory = os.path.join(sync_depth_parent_directory, const.AB)
				create_directories(sync_depth_ab_directory)
				
				# 0. Create base stream timestamp - synchronize stream timestamp mapping
				base_ts_to_stream_ts = self.create_base_ts_to_stream_ts_map(
					self.get_stream_keys_from_dir,
					[raw_depth_data_directory, const.PNG_EXTENSION, -1]
				)
				
				# 1. Synchronize Pose
				print("Synchronizing Depth Pose data")
				self.create_sync_stream_pkl_data(
					raw_depth_pose_file_path,
					sync_depth_pose_file_path,
					base_ts_to_stream_ts
				)
				print("Done synchronizing Depth Pose data")
				
				# 2. Synchronize Depth data
				print("Synchronizing Depth data")
				self.create_sync_stream_frames(
					raw_depth_data_directory,
					const.PNG_EXTENSION,
					sync_depth_data_directory,
					self.depth_stream_suffix,
					base_ts_to_stream_ts
				)
				print("Done synchronizing Depth data")
				
				# 3. Synchronize Active Brightness data
				print("Synchronizing Active Brightness data")
				self.create_sync_stream_frames(
					raw_depth_ab_directory,
					const.PNG_EXTENSION,
					sync_depth_ab_directory,
					self.ab_stream_suffix,
					base_ts_to_stream_ts
				)
				print("Done synchronizing Active Brightness data")
				
				sample_depth_frame = os.path.join(raw_depth_data_directory, os.listdir(raw_depth_data_directory)[0])
				self.depth_width, self.depth_height = self.get_image_characteristics(sample_depth_frame)
				self.meta_yaml_data["depth_mode"] = const.AHAT
				self.meta_yaml_data["depth_width"] = self.depth_width
				self.meta_yaml_data["depth_height"] = self.depth_height
				
				# 4. Compress all frames into a zip file in both raw and sync directories
				print("Compressing Depth data")
				CompressDataService.compress_dir(sync_depth_parent_directory, const.DEPTH)
				print("Done compressing Depth data")
				print("Compressing Active Brightness data")
				CompressDataService.compress_dir(sync_depth_parent_directory, const.AB)
				print("Done compressing Active Brightness data")
				
				# 5. Delete raw frames directory
				print("Deleting frames directory")
				CompressDataService.delete_dir(raw_depth_data_directory)
				CompressDataService.delete_dir(sync_depth_data_directory)
				print("Done deleting raw frames directory")
				print("Deleting ab directory")
				CompressDataService.delete_dir(raw_depth_ab_directory)
				CompressDataService.delete_dir(sync_depth_ab_directory)
				print("Done deleting ab directory")
			elif stream_name == const.SPATIAL:
				# 1. Synchronize spatial data
				spatial_directory = os.path.join(self.raw_data_directory, const.SPATIAL)
				sync_spatial_directory = os.path.join(self.sync_data_directory, const.SPATIAL)
				create_directories(sync_spatial_directory)
				
				spatial_data_file = f'{self.recording.id}_spatial.pkl'
				spatial_file_path = os.path.join(spatial_directory, spatial_data_file)
				sync_spatial_file_path = os.path.join(sync_spatial_directory, spatial_data_file)
				
				base_ts_to_stream_ts = self.create_base_ts_to_stream_ts_map(
					self.get_stream_keys_from_pkl,
					[spatial_file_path]
				)
				
				print("Synchronizing Spatial data")
				self.create_sync_stream_pkl_data(spatial_file_path, sync_spatial_file_path, base_ts_to_stream_ts)
				print("Done synchronizing Spatial data")
			elif stream_name in const.IMU_LIST:
				imu_directory = os.path.join(self.raw_data_directory, const.IMU)
				sync_imu_directory = os.path.join(self.sync_data_directory, const.IMU)
				create_directories(sync_imu_directory)
				
				imu_data_file = f'{self.recording.id}_{stream_name}.pkl'
				imu_file_path = os.path.join(imu_directory, imu_data_file)
				sync_imu_file_path = os.path.join(sync_imu_directory, imu_data_file)
				
				base_ts_to_stream_ts = self.create_base_ts_to_stream_ts_map(
					self.get_stream_keys_from_pkl,
					[imu_file_path]
				)
				
				print(f"Synchronizing {stream_name} data")
				self.create_sync_stream_pkl_data(imu_file_path, sync_imu_file_path, base_ts_to_stream_ts)
				print(f"Done synchronizing {stream_name} data")
		
		print("Compressing pv frames directory")
		CompressDataService.compress_dir(self.sync_base_stream_directory, const.FRAMES)
		print("Done compressing pv frames directory")
		
		# Delete raw frames directory
		print("Deleting pv frames directory")
		CompressDataService.delete_dir(raw_base_stream_frames_dir)
		CompressDataService.delete_dir(sync_base_stream_frames_dir)
		print("Done deleting pv frames directory")
		
		with open(os.path.join(self.sync_data_directory, "meta.yaml"), "w") as meta_yaml_file:
			for key, value in self.meta_yaml_data.items():
				meta_yaml_file.write(f"{key}: {value}\n")