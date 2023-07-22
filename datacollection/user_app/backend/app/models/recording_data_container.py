from ..utils.constants import Recording_Constants as const


class RecordingDataContainer:
	
	def __init__(
			self,
			is_holo_lens_enabled: bool,
			is_spatial_enabled: bool,
	):
		self.is_hololens_enabled = is_holo_lens_enabled
		self.is_spatial_enabled = is_spatial_enabled
		
		self.GOPRO_RESOLUTION_360p = None
		self.GOPRO_RESOLUTION_4k = None
		
		self.HOLOLENS_RAW_PV_FRAMES_ZIP = None
		self.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = None
		self.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = None
		self.HOLOLENS_RAW_MC_PKL = None
		
		self.HOLOLENS_SYNC_PV_FRAMES_ZIP = None
		self.HOLOLENS_SYNC_PV_VIDEO = None
		self.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = None
		self.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = None
		
		self.HOLOLENS_RAW_SPATIAL_PKL = None
		self.HOLOLENS_SYNC_SPATIAL_PKL = None
		
		self.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = None
		self.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = None
		self.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = None
		
		self.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = None
		self.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = None
		self.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = None
		
		self.HOLOLENS_RAW_PV_POSE_PKL = None
		self.HOLOLENS_SYNC_PV_POSE_PKL = None
		
		self.HOLOLENS_RAW_DEPTH_POSE_PKL = None
		self.HOLOLENS_SYNC_DEPTH_POSE_PKL = None
		
		self.HOLOLENS_DEVICE_INFO = None
	
	# def update_recording_data_json(self):
	# 	self.recording_data_json = {const.GOPRO: {}}
	# 	self.recording_data_json[const.GOPRO][const.GOPRO_RESOLUTION_4K] = self.GOPRO_RESOLUTION_4k
	# 	self.recording_data_json[const.GOPRO][const.GOPRO_RESOLUTION_360P] = self.GOPRO_RESOLUTION_360p
	#
	# 	if self.is_holo_lens_enabled:
	#
	# 		self.recording_data_json[const.HOLOLENS] = {}
	# 		self.recording_data_json[const.HOLOLENS][const.RAW] = {}
	# 		self.recording_data_json[const.HOLOLENS][const.SYNC] = {}
	#
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.PV] = {}
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.DEPTH_AHAT] = {}
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.MC] = {}
	#
	# 		self.recording_data_json[const.HOLOLENS][const.SYNC][const.PV] = {}
	# 		self.recording_data_json[const.HOLOLENS][const.SYNC][const.DEPTH_AHAT] = {}
	#
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.PV][
	# 			const.FRAMES_ZIP] = self.HOLOLENS_RAW_PV_FRAMES_ZIP
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.DEPTH_AHAT][
	# 			const.AB_ZIP] = self.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.DEPTH_AHAT][
	# 			const.DEPTH_ZIP] = self.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.MC][const.MC_PKL] = self.HOLOLENS_RAW_MC_PKL
	# 		self.recording_data_json[const.HOLOLENS][const.RAW][const.HOLOLENS_DEVICE_INFO] = self.HOLOLENS_DEVICE_INFO
	#
	# 		self.recording_data_json[const.HOLOLENS][const.SYNC][const.PV][
	# 			const.FRAMES_ZIP] = self.HOLOLENS_SYNC_PV_FRAMES_ZIP
	# 		self.recording_data_json[const.HOLOLENS][const.SYNC][const.PV][const.PV_VIDEO] = self.HOLOLENS_SYNC_PV_VIDEO
	# 		self.recording_data_json[const.HOLOLENS][const.SYNC][const.DEPTH_AHAT][
	# 			const.AB_ZIP] = self.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP
	# 		self.recording_data_json[const.HOLOLENS][const.SYNC][const.DEPTH_AHAT][
	# 			const.DEPTH_ZIP] = self.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP
	#
	# 		if self.is_spatial_enabled:
	# 			self.recording_data_json[const.HOLOLENS][const.RAW][const.SPATIAL_POSE] = self.HOLOLENS_RAW_SPATIAL_PKL
	# 			self.recording_data_json[const.HOLOLENS][const.SYNC][
	# 				const.SPATIAL_POSE] = self.HOLOLENS_SYNC_SPATIAL_PKL
	#
	# 			self.recording_data_json[const.HOLOLENS][const.RAW][const.IMU][
	# 				const.IMU_MAGNETOMETER_PKL] = self.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL
	# 			self.recording_data_json[const.HOLOLENS][const.RAW][const.IMU][
	# 				const.IMU_GYROSCOPE_PKL] = self.HOLOLENS_RAW_IMU_GYROSCOPE_PKL
	# 			self.recording_data_json[const.HOLOLENS][const.RAW][const.IMU][
	# 				const.IMU_ACCELEROMETER_PKL] = self.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL
	#
	# 			self.recording_data_json[const.HOLOLENS][const.SYNC][const.IMU][
	# 				const.IMU_MAGNETOMETER_PKL] = self.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL
	# 			self.recording_data_json[const.HOLOLENS][const.SYNC][const.IMU][
	# 				const.IMU_GYROSCOPE_PKL] = self.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL
	# 			self.recording_data_json[const.HOLOLENS][const.SYNC][const.IMU][
	# 				const.IMU_ACCELEROMETER_PKL] = self.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL
	#
	# 			self.recording_data_json[const.HOLOLENS][const.RAW][const.PV][
	# 				const.PV_POSE] = self.HOLOLENS_RAW_PV_POSE_PKL
	# 			self.recording_data_json[const.HOLOLENS][const.SYNC][const.PV][
	# 				const.PV_POSE] = self.HOLOLENS_SYNC_PV_POSE_PKL
	#
	# 			self.recording_data_json[const.HOLOLENS][const.RAW][const.DEPTH_AHAT][
	# 				const.DEPTH_POSE] = self.HOLOLENS_RAW_DEPTH_POSE_PKL
	# 			self.recording_data_json[const.HOLOLENS][const.SYNC][const.DEPTH_AHAT][
	# 				const.DEPTH_POSE] = self.HOLOLENS_SYNC_DEPTH_POSE_PKL
	
	def to_dict(self):
		rdc_dict = {
			const.IS_HOLO_LENS_ENABLED: self.is_hololens_enabled,
			const.IS_SPATIAL_ENABLED: self.is_spatial_enabled,
			
			const.GOPRO_RESOLUTION_360P: self.GOPRO_RESOLUTION_360p,
			const.GOPRO_RESOLUTION_4K: self.GOPRO_RESOLUTION_4k,
		}
		
		if self.is_hololens_enabled:
			rdc_dict[const.HOLOLENS_RAW_PV_FRAMES_ZIP] = self.HOLOLENS_RAW_PV_FRAMES_ZIP
			rdc_dict[const.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP] = self.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP
			rdc_dict[const.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP] = self.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP
			rdc_dict[const.HOLOLENS_RAW_MC_PKL] = self.HOLOLENS_RAW_MC_PKL
			
			rdc_dict[const.HOLOLENS_DEVICE_INFO] = self.HOLOLENS_DEVICE_INFO
			
			rdc_dict[const.HOLOLENS_SYNC_PV_FRAMES_ZIP] = self.HOLOLENS_SYNC_PV_FRAMES_ZIP
			rdc_dict[const.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP] = self.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP
			rdc_dict[const.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP] = self.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP
			rdc_dict[const.PV_VIDEO] = self.HOLOLENS_SYNC_PV_VIDEO
			
			if self.is_spatial_enabled:
				rdc_dict[const.HOLOLENS_RAW_SPATIAL_POSE_PKL] = self.HOLOLENS_RAW_SPATIAL_PKL
				rdc_dict[const.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL] = self.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL
				rdc_dict[const.HOLOLENS_RAW_IMU_GYROSCOPE_PKL] = self.HOLOLENS_RAW_IMU_GYROSCOPE_PKL
				rdc_dict[const.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL] = self.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL
				
				rdc_dict[const.HOLOLENS_SYNC_SPATIAL_POSE_PKL] = self.HOLOLENS_SYNC_SPATIAL_PKL
				rdc_dict[const.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL] = self.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL
				rdc_dict[const.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL] = self.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL
				rdc_dict[const.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL] = self.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL
				
				rdc_dict[const.HOLOLENS_RAW_PV_POSE_PKL] = self.HOLOLENS_RAW_PV_POSE_PKL
				rdc_dict[const.HOLOLENS_SYNC_PV_POSE_PKL] = self.HOLOLENS_SYNC_PV_POSE_PKL
				
				rdc_dict[const.HOLOLENS_RAW_DEPTH_POSE_PKL] = self.HOLOLENS_RAW_DEPTH_POSE_PKL
				rdc_dict[const.HOLOLENS_SYNC_DEPTH_POSE_PKL] = self.HOLOLENS_SYNC_DEPTH_POSE_PKL
	
	@classmethod
	def from_dict(cls, recording_data_container_dict) -> "RecordingDataContainer":
		recording_data_container = cls(
			recording_data_container_dict[const.IS_HOLO_LENS_ENABLED],
			recording_data_container_dict[const.IS_SPATIAL_ENABLED]
		)
		
		data_json = recording_data_container_dict[const.DATA_JSON]
		
		recording_data_container.GOPRO_RESOLUTION_360p = data_json[const.GOPRO][
			const.GOPRO_RESOLUTION_360P]
		recording_data_container.GOPRO_RESOLUTION_4k = data_json[const.GOPRO][const.GOPRO_RESOLUTION_4K]
		
		if recording_data_container.is_hololens_enabled:
			recording_data_container.HOLOLENS_RAW_PV_FRAMES_ZIP = \
				data_json[const.HOLOLENS][const.RAW][const.PV][const.FRAMES_ZIP]
			recording_data_container.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = \
				data_json[const.HOLOLENS][const.RAW][const.DEPTH_AHAT][const.AB_ZIP]
			recording_data_container.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = \
				data_json[const.HOLOLENS][const.RAW][const.DEPTH_AHAT][const.DEPTH_ZIP]
			recording_data_container.HOLOLENS_RAW_MC_PKL = \
				data_json[const.HOLOLENS][const.RAW][const.MC][const.MC_PKL]
			recording_data_container.HOLOLENS_DEVICE_INFO = \
				data_json[const.HOLOLENS][const.HOLOLENS_DEVICE_INFO]
			
			recording_data_container.HOLOLENS_SYNC_PV_FRAMES_ZIP = \
				data_json[const.HOLOLENS][const.SYNC][const.PV][const.FRAMES_ZIP]
			recording_data_container.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = \
				data_json[const.HOLOLENS][const.SYNC][const.DEPTH_AHAT][const.AB_ZIP]
			recording_data_container.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = \
				data_json[const.HOLOLENS][const.SYNC][const.DEPTH_AHAT][const.DEPTH_ZIP]
			
			if recording_data_container.is_spatial_enabled:
				recording_data_container.HOLOLENS_RAW_SPATIAL_PKL = \
					data_json[const.HOLOLENS][const.RAW][const.SPATIAL][const.SPATIAL_POSE]
				recording_data_container.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = \
					data_json[const.HOLOLENS][const.RAW][const.IMU][const.IMU_MAGNETOMETER_PKL]
				recording_data_container.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = \
					data_json[const.HOLOLENS][const.RAW][const.IMU][const.IMU_GYROSCOPE_PKL]
				recording_data_container.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = \
					data_json[const.HOLOLENS][const.RAW][const.IMU][const.IMU_ACCELEROMETER_PKL]
				recording_data_container.HOLOLENS_RAW_DEPTH_POSE_PKL = \
					data_json[const.HOLOLENS][const.RAW][const.DEPTH_AHAT][const.DEPTH_POSE]
				recording_data_container.HOLOLENS_RAW_PV_POSE_PKL = \
					data_json[const.HOLOLENS][const.RAW][const.PV][const.PV_POSE]
				
				recording_data_container.HOLOLENS_SYNC_SPATIAL_PKL = \
					data_json[const.HOLOLENS][const.SYNC][const.SPATIAL][const.SPATIAL_POSE]
				recording_data_container.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = \
					data_json[const.HOLOLENS][const.SYNC][const.IMU][const.IMU_MAGNETOMETER_PKL]
				recording_data_container.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = \
					data_json[const.HOLOLENS][const.SYNC][const.IMU][const.IMU_GYROSCOPE_PKL]
				recording_data_container.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = \
					data_json[const.HOLOLENS][const.SYNC][const.IMU][const.IMU_ACCELEROMETER_PKL]
				recording_data_container.HOLOLENS_SYNC_DEPTH_POSE_PKL = \
					data_json[const.HOLOLENS][const.SYNC][const.DEPTH_AHAT][const.DEPTH_POSE]
				recording_data_container.HOLOLENS_SYNC_PV_POSE_PKL = \
					data_json[const.HOLOLENS][const.SYNC][const.PV][const.PV_POSE]
				recording_data_container.HOLOLENS_SYNC_PV_VIDEO = \
					data_json[const.HOLOLENS][const.SYNC][const.PV][const.PV_VIDEO]
		
		recording_data_container.update_recording_data_json()
		return recording_data_container
