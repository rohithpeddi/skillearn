import os

from ..models.recording import Recording
from ..models.recording_summary import RecordingSummary
from ..services.firebase_service import FirebaseService

from ..utils.constants import Recording_Constants as const


class RecordingDataSummarizationService:
	
	def __init__(self, recording_id, recording_data_directory, is_spatial_enabled=False):
		self.recording_id = recording_id
		self.recording_data_directory = recording_data_directory
		
		self.is_hololens_enabled = False
		self.is_spatial_enabled = is_spatial_enabled
		
		self.db_service = FirebaseService()
		self.recording_summary = self.db_service.fetch_recording_summary(self.recording_id)
		
		if self.recording_summary is None:
			self.recording_summary = self.create_recording_summary()
	
	def create_recording_summary(self):
		recording_dict = self.db_service.fetch_recording(self.recording_id)
		recording = Recording.from_dict(recording_dict)
		
		raw_data_directory = os.path.join(self.recording_data_directory, const.RAW)
		if os.path.exists(raw_data_directory):
			self.is_hololens_enabled = True
		else:
			self.is_hololens_enabled = False
			self.is_spatial_enabled = False
		
		recording_summary = RecordingSummary(
			self.recording_id,
			recording,
			self.is_hololens_enabled,
			self.is_spatial_enabled
		)
		
		gopro_data_directory = os.path.join(self.recording_data_directory, const.GOPRO)
		if os.path.exists(gopro_data_directory):
			# 1. Update Metadata, Download Links, File Sizes
			gopro_4k_file = os.path.join(gopro_data_directory, f"{self.recording_id}.MP4")
			if os.path.exists(gopro_4k_file):
				recording_summary.metadata.GOPRO_RESOLUTION_4k = True
				recording_summary.file_sizes.GOPRO_RESOLUTION_4k = os.path.getsize(gopro_4k_file)
			
			gopro_360p_file = os.path.join(gopro_data_directory, f"{self.recording_id}_360p.mp4")
			if os.path.exists(gopro_360p_file):
				recording_summary.metadata.GOPRO_RESOLUTION_360p = True
				recording_summary.file_sizes.GOPRO_RESOLUTION_360p = os.path.getsize(gopro_360p_file)
		
		if os.path.exists(raw_data_directory):
			raw_depth_ahat_directory = os.path.join(raw_data_directory, const.DEPTH_AHAT)
			if os.path.exists(raw_depth_ahat_directory):
				raw_ab_zip_file = os.path.join(raw_depth_ahat_directory, "ab.zip")
				if os.path.exists(raw_ab_zip_file):
					recording_summary.metadata.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = True
					recording_summary.file_sizes.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = os.path.getsize(raw_ab_zip_file)
				
				raw_depth_zip_file = os.path.join(raw_depth_ahat_directory, "depth.zip")
				if os.path.exists(raw_depth_zip_file):
					recording_summary.metadata.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = True
					recording_summary.file_sizes.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = os.path.getsize(raw_depth_zip_file)
				
				if self.is_spatial_enabled:
					raw_depth_pose_pkl_file = os.path.join(raw_depth_ahat_directory,
					                                       f"{self.recording_id}_depth_ahat_pose.pkl")
					if os.path.exists(raw_depth_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_DEPTH_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_DEPTH_POSE_PKL = os.path.getsize(
							raw_depth_pose_pkl_file)
			
			raw_pv_directory = os.path.join(raw_data_directory, const.PV)
			if os.path.exists(raw_pv_directory):
				raw_frames_zip_file = os.path.join(raw_pv_directory, "frames.zip")
				if os.path.exists(raw_frames_zip_file):
					recording_summary.metadata.HOLOLENS_RAW_PV_FRAMES_ZIP = True
					recording_summary.file_sizes.HOLOLENS_RAW_PV_FRAMES_ZIP = os.path.getsize(raw_frames_zip_file)
				
				if self.is_spatial_enabled:
					raw_pv_pose_pkl_file = os.path.join(raw_pv_directory, f"{self.recording_id}_pv_pose.pkl")
					if os.path.exists(raw_pv_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_PV_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_PV_POSE_PKL = os.path.getsize(raw_pv_pose_pkl_file)
			
			raw_mc_directory = os.path.join(raw_data_directory, const.MC)
			if os.path.exists(raw_mc_directory):
				raw_mc_pkl_file = os.path.join(raw_mc_directory, f"{self.recording_id}_mc.pkl")
				if os.path.exists(raw_mc_pkl_file):
					recording_summary.metadata.HOLOLENS_RAW_MC_PKL = True
					recording_summary.file_sizes.HOLOLENS_RAW_MC_PKL = os.path.getsize(raw_mc_pkl_file)
			
			if self.is_spatial_enabled:
				raw_spatial_directory = os.path.join(raw_data_directory, const.SPATIAL)
				if os.path.exists(raw_spatial_directory):
					raw_spatial_pkl_file = os.path.join(raw_spatial_directory, f"{self.recording_id}_spatial.pkl")
					if os.path.exists(raw_spatial_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_SPATIAL_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_SPATIAL_PKL = os.path.getsize(raw_spatial_pkl_file)
				
				raw_imu_data_directory = os.path.join(raw_data_directory, const.IMU)
				if os.path.exists(raw_imu_data_directory):
					raw_imu_accelerometer_pkl_file = os.path.join(raw_imu_data_directory,
					                                              f"{self.recording_id}_imu_accelerometer.pkl")
					if os.path.exists(raw_imu_accelerometer_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = os.path.getsize(
							raw_imu_accelerometer_pkl_file)
					
					raw_imu_gyroscope_pkl_file = os.path.join(raw_imu_data_directory,
					                                          f"{self.recording_id}_imu_gyroscope.pkl")
					if os.path.exists(raw_imu_gyroscope_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = os.path.getsize(
							raw_imu_gyroscope_pkl_file)
					
					raw_imu_magnetometer_pkl_file = os.path.join(raw_imu_data_directory,
					                                             f"{self.recording_id}_imu_magnetometer.pkl")
					if os.path.exists(raw_imu_magnetometer_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = os.path.getsize(
							raw_imu_magnetometer_pkl_file)
		
		sync_data_directory = os.path.join(self.recording_data_directory, const.SYNC)
		if os.path.exists(sync_data_directory):
			sync_depth_ahat_directory = os.path.join(sync_data_directory, const.DEPTH_AHAT)
			if os.path.exists(sync_depth_ahat_directory):
				sync_ab_zip_file = os.path.join(sync_depth_ahat_directory, "ab.zip")
				if os.path.exists(sync_ab_zip_file):
					recording_summary.metadata.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = True
					recording_summary.file_sizes.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = os.path.getsize(sync_ab_zip_file)
				
				sync_depth_zip_file = os.path.join(sync_depth_ahat_directory, "depth.zip")
				if os.path.exists(sync_depth_zip_file):
					recording_summary.metadata.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = True
					recording_summary.file_sizes.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = os.path.getsize(
						sync_depth_zip_file)
				
				if self.is_spatial_enabled:
					sync_depth_pose_pkl_file = os.path.join(sync_depth_ahat_directory,
					                                        f"{self.recording_id}_depth_ahat_pose.pkl")
					if os.path.exists(sync_depth_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_DEPTH_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_DEPTH_POSE_PKL = os.path.getsize(
							sync_depth_pose_pkl_file)
			
			sync_pv_directory = os.path.join(sync_data_directory, const.PV)
			if os.path.exists(sync_pv_directory):
				sync_frames_zip_file = os.path.join(sync_pv_directory, "frames.zip")
				if os.path.exists(sync_frames_zip_file):
					recording_summary.metadata.HOLOLENS_SYNC_PV_FRAMES_ZIP = True
					recording_summary.file_sizes.HOLOLENS_SYNC_PV_FRAMES_ZIP = os.path.getsize(sync_frames_zip_file)
				
				if self.is_spatial_enabled:
					sync_pv_pose_pkl_file = os.path.join(sync_pv_directory, f"{self.recording_id}_pv_pose.pkl")
					if os.path.exists(sync_pv_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_PV_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_PV_POSE_PKL = os.path.getsize(sync_pv_pose_pkl_file)
			
			sync_mc_directory = os.path.join(sync_data_directory, const.MC)
			if os.path.exists(sync_mc_directory):
				sync_mc_pkl_file = os.path.join(sync_mc_directory, f"{self.recording_id}_mc.pkl")
				if os.path.exists(sync_mc_pkl_file):
					recording_summary.metadata.HOLOLENS_SYNC_MC_PKL = True
					recording_summary.file_sizes.HOLOLENS_SYNC_MC_PKL = os.path.getsize(sync_mc_pkl_file)
			
			if self.is_spatial_enabled:
				sync_spatial_directory = os.path.join(sync_data_directory, const.SPATIAL)
				if os.path.exists(sync_spatial_directory):
					sync_spatial_pkl_file = os.path.join(sync_spatial_directory, f"{self.recording_id}_spatial.pkl")
					if os.path.exists(sync_spatial_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_SPATIAL_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_SPATIAL_PKL = os.path.getsize(sync_spatial_pkl_file)
				
				sync_imu_data_directory = os.path.join(sync_data_directory, const.IMU)
				if os.path.exists(sync_imu_data_directory):
					sync_imu_accelerometer_pkl_file = os.path.join(sync_imu_data_directory,
					                                               f"{self.recording_id}_imu_accelerometer.pkl")
					if os.path.exists(sync_imu_accelerometer_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = os.path.getsize(
							sync_imu_accelerometer_pkl_file)
					
					sync_imu_gyroscope_pkl_file = os.path.join(sync_imu_data_directory,
					                                           f"{self.recording_id}_imu_gyroscope.pkl")
					if os.path.exists(sync_imu_gyroscope_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = os.path.getsize(
							sync_imu_gyroscope_pkl_file)
					
					sync_imu_magnetometer_pkl_file = os.path.join(sync_imu_data_directory,
					                                              f"{self.recording_id}_imu_magnetometer.pkl")
					if os.path.exists(sync_imu_magnetometer_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = os.path.getsize(
							sync_imu_magnetometer_pkl_file)
		
		self.db_service.update_recording_summary(recording_summary.to_dict())
		return recording_summary
