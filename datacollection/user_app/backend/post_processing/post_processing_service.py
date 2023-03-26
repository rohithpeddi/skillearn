# TODO:
# 1. Each method takes a list of directories as input
# 2. Performs the necessary function as described by the method name
class PostProcessingService:
	
	def __init__(self):
		pass
	
	def synchronize_data(self):
		pass
	
	def generate_audio(self):
		pass
	
	def generate_video(self):
		pass
	
	def generate_muxed_audio_video(self):
		pass
	
	def change_video_resolution(self):
		pass
	
	def verify_depth(self):
		pass
	
	def verify_spatial(self):
		pass
	
	def push_to_box(self):
		# 1. Zip frames and push master data to BOX
		# 2. Zip frames and push synchronized data to BOX
		# 3. Place all the MRC/GoPro High resolution videos into BOX
		# 4. Convert all videos to 360p videos and push to BOX
		pass


# if __name__ == '__main__':
# 	ip_address = '192.168.0.117'
# 	hl2_service = PostProcessingService()
# 	recording_instance = Recording("Coffee", "PL1", "P1", "R2", False)
# 	recording_instance.set_device_ip(ip_address)
