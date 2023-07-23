from ..utils.constants import Recording_Constants as const


class RecordingDataContainer:
	
	def __init__(
			self,
			is_hololens_enabled: bool,
			is_spatial_enabled: bool,
	):
		self.is_hololens_enabled = is_hololens_enabled
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
	
	def to_dict(self):
		rdc_dict = {
			const.IS_HOLOLENS_ENABLED: self.is_hololens_enabled,
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
			rdc_dict[const.HOLOLENS_SYNC_PV_VIDEO] = self.HOLOLENS_SYNC_PV_VIDEO
			
			if self.is_spatial_enabled:
				rdc_dict[const.HOLOLENS_RAW_SPATIAL_PKL] = self.HOLOLENS_RAW_SPATIAL_PKL
				rdc_dict[const.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL] = self.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL
				rdc_dict[const.HOLOLENS_RAW_IMU_GYROSCOPE_PKL] = self.HOLOLENS_RAW_IMU_GYROSCOPE_PKL
				rdc_dict[const.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL] = self.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL
				
				rdc_dict[const.HOLOLENS_SYNC_SPATIAL_PKL] = self.HOLOLENS_SYNC_SPATIAL_PKL
				rdc_dict[const.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL] = self.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL
				rdc_dict[const.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL] = self.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL
				rdc_dict[const.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL] = self.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL
				
				rdc_dict[const.HOLOLENS_RAW_PV_POSE_PKL] = self.HOLOLENS_RAW_PV_POSE_PKL
				rdc_dict[const.HOLOLENS_SYNC_PV_POSE_PKL] = self.HOLOLENS_SYNC_PV_POSE_PKL
				
				rdc_dict[const.HOLOLENS_RAW_DEPTH_POSE_PKL] = self.HOLOLENS_RAW_DEPTH_POSE_PKL
				rdc_dict[const.HOLOLENS_SYNC_DEPTH_POSE_PKL] = self.HOLOLENS_SYNC_DEPTH_POSE_PKL
		
		return rdc_dict
	
	@classmethod
	def from_dict(cls, rdc_dict) -> "RecordingDataContainer":
		rdc = cls(
			rdc_dict[const.IS_HOLOLENS_ENABLED],
			rdc_dict[const.IS_SPATIAL_ENABLED]
		)

		if const.GOPRO_RESOLUTION_360P in rdc_dict:
			rdc.GOPRO_RESOLUTION_360p = rdc_dict[const.GOPRO_RESOLUTION_360P]

		if const.GOPRO_RESOLUTION_4K in rdc_dict:
			rdc.GOPRO_RESOLUTION_4k = rdc_dict[const.GOPRO_RESOLUTION_4K]
		
		if rdc.is_hololens_enabled:
			if const.HOLOLENS_RAW_PV_FRAMES_ZIP in rdc_dict:
				rdc.HOLOLENS_RAW_PV_FRAMES_ZIP = rdc_dict[const.HOLOLENS_RAW_PV_FRAMES_ZIP]

			if const.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP in rdc_dict:
				rdc.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP = rdc_dict[const.HOLOLENS_RAW_DEPTH_AHAT_AB_ZIP]

			if const.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP in rdc_dict:
				rdc.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP = rdc_dict[const.HOLOLENS_RAW_DEPTH_AHAT_DEPTH_ZIP]

			if const.HOLOLENS_RAW_MC_PKL in rdc_dict:
				rdc.HOLOLENS_RAW_MC_PKL = rdc_dict[const.HOLOLENS_RAW_MC_PKL]

			if const.HOLOLENS_DEVICE_INFO in rdc_dict:
				rdc.HOLOLENS_DEVICE_INFO = rdc_dict[const.HOLOLENS_DEVICE_INFO]

			if const.HOLOLENS_SYNC_PV_FRAMES_ZIP in rdc_dict:
				rdc.HOLOLENS_SYNC_PV_FRAMES_ZIP = rdc_dict[const.HOLOLENS_SYNC_PV_FRAMES_ZIP]

			if const.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP in rdc_dict:
				rdc.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP = rdc_dict[const.HOLOLENS_SYNC_DEPTH_AHAT_AB_ZIP]

			if const.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP in rdc_dict:
				rdc.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP = rdc_dict[const.HOLOLENS_SYNC_DEPTH_AHAT_DEPTH_ZIP]
			
			if rdc.is_spatial_enabled:
				if const.HOLOLENS_SYNC_SPATIAL_PKL in rdc_dict:
					rdc.HOLOLENS_RAW_SPATIAL_PKL = rdc_dict[const.HOLOLENS_RAW_SPATIAL_PKL]

				if const.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL in rdc_dict:
					rdc.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL = rdc_dict[const.HOLOLENS_RAW_IMU_ACCELEROMETER_PKL]

				if const.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL in rdc_dict:
					rdc.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL = rdc_dict[const.HOLOLENS_RAW_IMU_MAGNETOMETER_PKL]

				if const.HOLOLENS_RAW_IMU_GYROSCOPE_PKL in rdc_dict:
					rdc.HOLOLENS_RAW_IMU_GYROSCOPE_PKL = rdc_dict[const.HOLOLENS_RAW_IMU_GYROSCOPE_PKL]

				if const.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL in rdc_dict:
					rdc.HOLOLENS_RAW_DEPTH_POSE_PKL = rdc_dict[const.HOLOLENS_RAW_DEPTH_POSE_PKL]

				if const.HOLOLENS_RAW_PV_POSE_PKL in rdc_dict:
					rdc.HOLOLENS_RAW_PV_POSE_PKL = rdc_dict[const.HOLOLENS_RAW_PV_POSE_PKL]

				if const.HOLOLENS_SYNC_SPATIAL_PKL in rdc_dict:
					rdc.HOLOLENS_SYNC_SPATIAL_PKL = rdc_dict[const.HOLOLENS_SYNC_SPATIAL_PKL]

				if const.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL in rdc_dict:
					rdc.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL = rdc_dict[const.HOLOLENS_SYNC_IMU_MAGNETOMETER_PKL]

				if const.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL in rdc_dict:
					rdc.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL = rdc_dict[const.HOLOLENS_SYNC_IMU_GYROSCOPE_PKL]

				if const.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL in rdc_dict:
					rdc.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL = rdc_dict[const.HOLOLENS_SYNC_IMU_ACCELEROMETER_PKL]

				if const.HOLOLENS_SYNC_DEPTH_POSE_PKL in rdc_dict:
					rdc.HOLOLENS_SYNC_DEPTH_POSE_PKL = rdc_dict[const.HOLOLENS_SYNC_DEPTH_POSE_PKL]

				if const.HOLOLENS_SYNC_PV_POSE_PKL in rdc_dict:
					rdc.HOLOLENS_SYNC_PV_POSE_PKL = rdc_dict[const.HOLOLENS_SYNC_PV_POSE_PKL]

				if const.HOLOLENS_SYNC_PV_VIDEO in rdc_dict:
					rdc.HOLOLENS_SYNC_PV_VIDEO = rdc_dict[const.HOLOLENS_SYNC_PV_VIDEO]
		
		return rdc
