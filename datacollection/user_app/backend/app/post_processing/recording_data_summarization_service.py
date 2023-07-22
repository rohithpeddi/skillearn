import os

from moviepy.video.io.VideoFileClip import VideoFileClip

from ..models.recording import Recording
from ..models.recording_summary import RecordingSummary
from ..services.box_service import BoxService
from ..services.firebase_service import FirebaseService

from ..utils.constants import Recording_Constants as const
from ..utils.logger_config import get_logger

logger = get_logger(__name__)


def get_file_size(file_path):
	size = os.path.getsize(file_path)
	if size < 1024:
		return str(size) + " bytes"
	elif size < 1048576:
		return str(size // 1024) + " KB"
	elif size < 1073741824:
		return str(size // 1048576) + " MB"
	else:
		return str(size // 1073741824) + " GB"


def get_video_duration(video_path):
	video_clip = VideoFileClip(video_path)
	recording_duration = round(video_clip.duration / 60, 3)
	video_clip.close()
	return recording_duration


class RecordingDataSummarizationService:
	
	def __init__(self, recording_id, recording_data_directory, is_spatial_enabled=False):
		self.recording_id = recording_id
		self.recording_data_directory = recording_data_directory
		
		self.is_hololens_enabled = False
		self.is_spatial_enabled = is_spatial_enabled
		
		self.db_service = FirebaseService()
		self.box_service = BoxService()
		
		self.recording_summary = None
		self.recording_summary_dict = self.db_service.fetch_recording_summary(self.recording_id)
		
		if self.recording_summary_dict is None:
			logger.info("Creating recording summary for recording id: {}".format(self.recording_id))
			self.create_recording_summary()
		else:
			self.recording_summary = RecordingSummary.from_dict(self.recording_summary_dict)
			logger.info("Recording summary already exists for recording id: {}".format(self.recording_id))
	
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
		
		recording_duration = None
		
		gopro_data_directory = os.path.join(self.recording_data_directory, const.GOPRO)
		if os.path.exists(gopro_data_directory):
			# 1. Update Metadata, Download Links, File Sizes
			gopro_4k_file = os.path.join(gopro_data_directory, f"{self.recording_id}.MP4")
			if os.path.exists(gopro_4k_file):
				recording_summary.metadata.GOPRO_RESOLUTION_4k = True
				recording_summary.file_sizes.GOPRO_RESOLUTION_4k = get_file_size(gopro_4k_file)
			
			gopro_360p_file = os.path.join(gopro_data_directory, f"{self.recording_id}_360p.mp4")
			if os.path.exists(gopro_360p_file):
				recording_summary.metadata.GOPRO_RESOLUTION_360p = True
				recording_summary.file_sizes.GOPRO_RESOLUTION_360p = get_file_size(gopro_360p_file)
				
				recording_duration = get_video_duration(gopro_360p_file)
				recording_summary.duration = recording_duration
		
		if os.path.exists(raw_data_directory):
			raw_depth_ahat_directory = os.path.join(raw_data_directory, const.DEPTH_AHAT)
			if os.path.exists(raw_depth_ahat_directory):
				raw_ab_zip_file = os.path.join(raw_depth_ahat_directory, "ab.zip")
				if os.path.exists(raw_ab_zip_file):
					recording_summary.metadata.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = True
					recording_summary.file_sizes.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = get_file_size(raw_ab_zip_file)
				
				raw_depth_zip_file = os.path.join(raw_depth_ahat_directory, "depth.zip")
				if os.path.exists(raw_depth_zip_file):
					recording_summary.metadata.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = True
					recording_summary.file_sizes.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = get_file_size(raw_depth_zip_file)
				
				if self.is_spatial_enabled:
					raw_depth_pose_pkl_file = os.path.join(raw_depth_ahat_directory,
					                                       f"{self.recording_id}_depth_ahat_pose.pkl")
					if os.path.exists(raw_depth_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_DEPTH_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_DEPTH_POSE_PKL = get_file_size(
							raw_depth_pose_pkl_file)
			
			raw_pv_directory = os.path.join(raw_data_directory, const.PV)
			if os.path.exists(raw_pv_directory):
				raw_frames_zip_file = os.path.join(raw_pv_directory, "frames.zip")
				if os.path.exists(raw_frames_zip_file):
					recording_summary.metadata.HOLOLENS_RAW_PV_FRAMES_ZIP = True
					recording_summary.file_sizes.HOLOLENS_RAW_PV_FRAMES_ZIP = get_file_size(raw_frames_zip_file)
				
				if self.is_spatial_enabled:
					raw_pv_pose_pkl_file = os.path.join(raw_pv_directory, f"{self.recording_id}_pv_pose.pkl")
					if os.path.exists(raw_pv_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_PV_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_PV_POSE_PKL = get_file_size(raw_pv_pose_pkl_file)
			
			raw_mc_directory = os.path.join(raw_data_directory, const.MC)
			if os.path.exists(raw_mc_directory):
				raw_mc_pkl_file = os.path.join(raw_mc_directory, f"{self.recording_id}_mc.pkl")
				if os.path.exists(raw_mc_pkl_file):
					recording_summary.metadata.HOLOLENS_RAW_MC_PKL = True
					recording_summary.file_sizes.HOLOLENS_RAW_MC_PKL = get_file_size(raw_mc_pkl_file)
			
			if self.is_spatial_enabled:
				raw_spatial_directory = os.path.join(raw_data_directory, const.SPATIAL)
				if os.path.exists(raw_spatial_directory):
					raw_spatial_pkl_file = os.path.join(raw_spatial_directory, f"{self.recording_id}_spatial.pkl")
					if os.path.exists(raw_spatial_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_SPATIAL_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_SPATIAL_PKL = get_file_size(raw_spatial_pkl_file)
				
				raw_imu_data_directory = os.path.join(raw_data_directory, const.IMU)
				if os.path.exists(raw_imu_data_directory):
					raw_imu_accelerometer_pkl_file = os.path.join(raw_imu_data_directory,
					                                              f"{self.recording_id}_imu_accelerometer.pkl")
					if os.path.exists(raw_imu_accelerometer_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = get_file_size(
							raw_imu_accelerometer_pkl_file)
					
					raw_imu_gyroscope_pkl_file = os.path.join(raw_imu_data_directory,
					                                          f"{self.recording_id}_imu_gyroscope.pkl")
					if os.path.exists(raw_imu_gyroscope_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = get_file_size(
							raw_imu_gyroscope_pkl_file)
					
					raw_imu_magnetometer_pkl_file = os.path.join(raw_imu_data_directory,
					                                             f"{self.recording_id}_imu_magnetometer.pkl")
					if os.path.exists(raw_imu_magnetometer_pkl_file):
						recording_summary.metadata.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = get_file_size(
							raw_imu_magnetometer_pkl_file)
		
		sync_data_directory = os.path.join(self.recording_data_directory, const.SYNC)
		if os.path.exists(sync_data_directory):
			sync_depth_ahat_directory = os.path.join(sync_data_directory, const.DEPTH_AHAT)
			if os.path.exists(sync_depth_ahat_directory):
				sync_ab_zip_file = os.path.join(sync_depth_ahat_directory, "ab.zip")
				if os.path.exists(sync_ab_zip_file):
					recording_summary.metadata.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = True
					recording_summary.file_sizes.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = get_file_size(sync_ab_zip_file)
				
				sync_depth_zip_file = os.path.join(sync_depth_ahat_directory, "depth.zip")
				if os.path.exists(sync_depth_zip_file):
					recording_summary.metadata.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = True
					recording_summary.file_sizes.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = get_file_size(
						sync_depth_zip_file)
				
				if self.is_spatial_enabled:
					sync_depth_pose_pkl_file = os.path.join(sync_depth_ahat_directory,
					                                        f"{self.recording_id}_depth_ahat_pose.pkl")
					if os.path.exists(sync_depth_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_DEPTH_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_DEPTH_POSE_PKL = get_file_size(
							sync_depth_pose_pkl_file)
			
			sync_pv_directory = os.path.join(sync_data_directory, const.PV)
			if os.path.exists(sync_pv_directory):
				sync_frames_zip_file = os.path.join(sync_pv_directory, "frames.zip")
				if os.path.exists(sync_frames_zip_file):
					recording_summary.metadata.HOLOLENS_SYNC_PV_FRAMES_ZIP = True
					recording_summary.file_sizes.HOLOLENS_SYNC_PV_FRAMES_ZIP = get_file_size(sync_frames_zip_file)
				
				sync_pv_video_file = os.path.join(sync_pv_directory, f"{self.recording_id}.mp4")
				if os.path.exists(sync_pv_video_file):
					recording_summary.metadata.HOLOLENS_SYNC_PV_VIDEO = True
					recording_summary.file_sizes.HOLOLENS_SYNC_PV_VIDEO = get_file_size(sync_pv_video_file)
					
					if recording_duration is None:
						recording_duration = get_video_duration(sync_pv_video_file)
						recording_summary.duration = recording_duration
				
				if self.is_spatial_enabled:
					sync_pv_pose_pkl_file = os.path.join(sync_pv_directory, f"{self.recording_id}_pv_pose.pkl")
					if os.path.exists(sync_pv_pose_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_PV_POSE_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_PV_POSE_PKL = get_file_size(sync_pv_pose_pkl_file)
			
			sync_mc_directory = os.path.join(sync_data_directory, const.MC)
			if os.path.exists(sync_mc_directory):
				sync_mc_pkl_file = os.path.join(sync_mc_directory, f"{self.recording_id}_mc.pkl")
				if os.path.exists(sync_mc_pkl_file):
					recording_summary.metadata.HOLOLENS_SYNC_MC_PKL = True
					recording_summary.file_sizes.HOLOLENS_SYNC_MC_PKL = get_file_size(sync_mc_pkl_file)
			
			if self.is_spatial_enabled:
				sync_spatial_directory = os.path.join(sync_data_directory, const.SPATIAL)
				if os.path.exists(sync_spatial_directory):
					sync_spatial_pkl_file = os.path.join(sync_spatial_directory, f"{self.recording_id}_spatial.pkl")
					if os.path.exists(sync_spatial_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_SPATIAL_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_SPATIAL_PKL = get_file_size(sync_spatial_pkl_file)
				
				sync_imu_data_directory = os.path.join(sync_data_directory, const.IMU)
				if os.path.exists(sync_imu_data_directory):
					sync_imu_accelerometer_pkl_file = os.path.join(sync_imu_data_directory,
					                                               f"{self.recording_id}_imu_accelerometer.pkl")
					if os.path.exists(sync_imu_accelerometer_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = get_file_size(
							sync_imu_accelerometer_pkl_file)
					
					sync_imu_gyroscope_pkl_file = os.path.join(sync_imu_data_directory,
					                                           f"{self.recording_id}_imu_gyroscope.pkl")
					if os.path.exists(sync_imu_gyroscope_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = get_file_size(
							sync_imu_gyroscope_pkl_file)
					
					sync_imu_magnetometer_pkl_file = os.path.join(sync_imu_data_directory,
					                                              f"{self.recording_id}_imu_magnetometer.pkl")
					if os.path.exists(sync_imu_magnetometer_pkl_file):
						recording_summary.metadata.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = True
						recording_summary.file_sizes.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = get_file_size(
							sync_imu_magnetometer_pkl_file)
		
		self.recording_summary = recording_summary
		self.db_service.update_recording_summary(recording_summary)
		return recording_summary
	
	def update_recording_summary_download_links(self, box_recording_folder):
		for recording_specific_item in box_recording_folder.get_items():
			if recording_specific_item.name == const.SYNC:
				for sync_data_item in recording_specific_item.get_items():
					if sync_data_item.name == const.PV:
						logger.info(f"[{self.recording_id}] Updating download links for {const.SYNC} - {const.PV}")
						for pv_data_item in sync_data_item.get_items():
							if pv_data_item.name == const.FRAMES_ZIP:
								self.recording_summary.download_links.HOLOLENS_SYNC_PV_FRAMES_ZIP = pv_data_item.get_shared_link_download_url(
									access='open')
							elif pv_data_item.name == f"{self.recording_id}.mp4":
								self.recording_summary.download_links.HOLOLENS_SYNC_PV_VIDEO = pv_data_item.get_shared_link_download_url(
									access='open')
							elif pv_data_item.name == f"{self.recording_id}_pv_pose.pkl":
								self.recording_summary.download_links.HOLOLENS_SYNC_PV_POSE_PKL = pv_data_item.get_shared_link_download_url(
									access='open')
					elif sync_data_item.name == const.SPATIAL:
						logger.info(f"[{self.recording_id}] Updating download links for {const.SYNC} - {const.SPATIAL}")
						for spatial_data_item in sync_data_item.get_items():
							if spatial_data_item.name == f"{self.recording_id}_spatial.pkl":
								self.recording_summary.download_links.HOLOLENS_SYNC_SPATIAL_PKL = spatial_data_item.get_shared_link_download_url(
									access='open')
					elif sync_data_item.name == const.IMU:
						logger.info(f"[{self.recording_id}] Updating download links for {const.SYNC} - {const.IMU}")
						for imu_data_item in sync_data_item.get_items():
							if imu_data_item.name == f"{self.recording_id}_imu_accelerometer.pkl":
								self.recording_summary.download_links.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = imu_data_item.get_shared_link_download_url(
									access='open')
							elif imu_data_item.name == f"{self.recording_id}_imu_gyroscope.pkl":
								self.recording_summary.download_links.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = imu_data_item.get_shared_link_download_url(
									access='open')
							elif imu_data_item.name == f"{self.recording_id}_imu_magnetometer.pkl":
								self.recording_summary.download_links.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = imu_data_item.get_shared_link_download_url(
									access='open')
					elif recording_specific_item.name == const.DEPTH_AHAT:
						logger.info(f"[{self.recording_id}] Updating download links for {const.SYNC} - {const.DEPTH_AHAT}")
						for depth_ahat_data_item in sync_data_item.get_items():
							if depth_ahat_data_item.name == f"{self.recording_id}_depth_ahat_pose.pkl":
								self.recording_summary.download_links.HOLOLENS_SYNC_DEPTH_POSE_PKL = depth_ahat_data_item.get_shared_link_download_url(
									access='open')
							elif recording_specific_item.name == const.DEPTH_ZIP:
								self.recording_summary.download_links.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = depth_ahat_data_item.get_shared_link_download_url(
									access='open')
							elif recording_specific_item.name == const.AB_ZIP:
								self.recording_summary.download_links.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = depth_ahat_data_item.get_shared_link_download_url(
									access='open')
			elif recording_specific_item.name == const.RAW:
				for raw_data_item in recording_specific_item.get_items():
					if raw_data_item.name == const.PV:
						logger.info(f"[{self.recording_id}] Updating download links for {const.RAW} - {const.PV}")
						for pv_data_item in raw_data_item.get_items():
							if pv_data_item.name == const.FRAMES_ZIP:
								self.recording_summary.download_links.HOLOLENS_RAW_PV_FRAMES_ZIP = pv_data_item.get_shared_link_download_url(
									access='open')
							elif pv_data_item.name == f"{self.recording_id}_pv_pose.pkl":
								self.recording_summary.download_links.HOLOLENS_RAW_PV_POSE_PKL = pv_data_item.get_shared_link_download_url(
									access='open')
					elif raw_data_item.name == const.SPATIAL:
						logger.info(f"[{self.recording_id}] Updating download links for {const.RAW} - {const.SPATIAL}")
						for spatial_data_item in raw_data_item.get_items():
							if spatial_data_item.name == f"{self.recording_id}_spatial.pkl":
								self.recording_summary.download_links.HOLOLENS_RAW_SPATIAL_PKL = spatial_data_item.get_shared_link_download_url(
									access='open')
					elif raw_data_item.name == const.IMU:
						logger.info(f"[{self.recording_id}] Updating download links for {const.RAW} - {const.IMU}")
						for imu_data_item in raw_data_item.get_items():
							if imu_data_item.name == f"{self.recording_id}_imu_accelerometer.pkl":
								self.recording_summary.download_links.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = imu_data_item.get_shared_link_download_url(
									access='open')
							elif imu_data_item.name == f"{self.recording_id}_imu_gyroscope.pkl":
								self.recording_summary.download_links.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = imu_data_item.get_shared_link_download_url(
									access='open')
							elif imu_data_item.name == f"{self.recording_id}_imu_magnetometer.pkl":
								self.recording_summary.download_links.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = imu_data_item.get_shared_link_download_url(
									access='open')
					elif raw_data_item.name == const.DEPTH_AHAT:
						logger.info(f"[{self.recording_id}] Updating download links for {const.RAW} - {const.DEPTH_AHAT}")
						for depth_ahat_data_item in raw_data_item.get_items():
							if depth_ahat_data_item.name == f"{self.recording_id}_depth_ahat_pose.pkl":
								self.recording_summary.download_links.HOLOLENS_RAW_DEPTH_POSE_PKL = depth_ahat_data_item.get_shared_link_download_url(
									access='open')
							elif recording_specific_item.name == const.DEPTH_ZIP:
								self.recording_summary.download_links.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = depth_ahat_data_item.get_shared_link_download_url(
									access='open')
							elif recording_specific_item.name == const.AB_ZIP:
								self.recording_summary.download_links.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = depth_ahat_data_item.get_shared_link_download_url(
									access='open')
					elif recording_specific_item.name == const.MC:
						logger.info(f"[{self.recording_id}] Updating download links for {const.RAW} - {const.MC}")
						for mc_data_item in raw_data_item.get_items():
							if mc_data_item.name == f"{self.recording_id}_mc.pkl":
								self.recording_summary.download_links.HOLOLENS_RAW_MC_PKL = mc_data_item.get_shared_link_download_url(
									access='open')
			elif recording_specific_item.name == const.GOPRO:
				logger.info(f"[{self.recording_id}] Updating download links for {const.GOPRO}")
				for gopro_data_item in recording_specific_item.get_items():
					if gopro_data_item.name == f"{self.recording_id}.MP4":
						self.recording_summary.download_links.GOPRO_RESOLUTION_4k = gopro_data_item.get_shared_link_download_url(
							access='open')
					elif gopro_data_item.name == f"{self.recording_id}_360p.mp4":
						self.recording_summary.download_links.GOPRO_RESOLUTION_360p = gopro_data_item.get_shared_link_download_url(
							access='open')
		
		logger.info(f"[{self.recording_id}] Updating recording summary in firebase database")
		self.db_service.update_recording_summary(self.recording_summary)
