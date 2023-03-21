from typing import Optional
from datacollection.user_app.backend.constants import Recording_Constants as const


class RecordingInfo:
	
	def __init__(
			self,
			rgb: bool,
			audio: Optional[bool] = None,
			info_3d: Optional[bool] = None
	):
		self.rgb = rgb
		self.audio = audio
		self.info_3d = info_3d
		
		if self.audio is not None:
			self.is_rgb_audio_synchronized = False
		
		if self.info_3d is not None:
			self.is_rgb_info_3d_synchronized = False
		
		if self.audio is not None and self.info_3d is not None:
			self.are_all_synchronized = False
			
			if self.is_rgb_audio_synchronized and self.are_all_synchronized:
				self.are_all_synchronized = True
	
	def update_are_all_synchronized(self):
		self.are_all_synchronized = self.is_rgb_audio_synchronized and self.are_all_synchronized
	
	def update_rgb_info_3d_synchronization_info(self, is_rgb_info_3d_synchronized):
		self.is_rgb_info_3d_synchronized = is_rgb_info_3d_synchronized
		self.update_are_all_synchronized()
	
	def update_rgb_audio_synchronization_info(self, is_rgb_audio_synchronized):
		self.is_rgb_audio_synchronized = is_rgb_audio_synchronized
		self.update_are_all_synchronized()
	
	def to_dict(self):
		recording_info_dict = {
			const.RGB: self.rgb
		}
		
		if self.audio is not None:
			recording_info_dict[const.AUDIO] = self.audio
			recording_info_dict[const.IS_RGB_AUDIO_SYNCHRONIZED] = self.is_rgb_audio_synchronized
			
		if self.info_3d is not None:
			recording_info_dict[const.INFO_3D] = self.info_3d
			recording_info_dict[const.IS_RGB_INFO_3D_SYNCHRONIZED] = self.is_rgb_info_3d_synchronized
			
		if self.audio is not None and self.info_3d is not None:
			recording_info_dict[const.ARE_ALL_SYNCHRONIZED] = self.are_all_synchronized
			
		return recording_info_dict
	
	@classmethod
	def from_dict(cls, recording_info_dict):
		recording_info = RecordingInfo(recording_info_dict[const.RGB], recording_info_dict[const.AUDIO],
		                               recording_info_dict[const.INFO_3D])
		
		if const.IS_RGB_AUDIO_SYNCHRONIZED in recording_info_dict:
			recording_info.is_rgb_audio_synchronized = recording_info_dict[const.IS_RGB_AUDIO_SYNCHRONIZED]
		
		if const.IS_RGB_INFO_3D_SYNCHRONIZED in recording_info_dict:
			recording_info.is_rgb_info_3d_synchronized = recording_info_dict[const.IS_RGB_INFO_3D_SYNCHRONIZED]
		
		if const.ARE_ALL_SYNCHRONIZED in recording_info_dict:
			recording_info.are_all_synchronized = recording_info_dict[const.ARE_ALL_SYNCHRONIZED]
