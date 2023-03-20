from typing import Optional


class RecordingInfo:
	
	def __init__(
			self,
			rgb=bool,
			audio=Optional[bool],
			info_3d=Optional[bool]
	):
		self.rgb = rgb
		self.audio = audio
		self.info_3d = info_3d
		
		if self.audio:
			self.is_rgb_audio_synchronized = False
			
		if info_3d:
			self.is_rgb_info_3d_synchronized = False
		
		self.are_all_synchronized = False
