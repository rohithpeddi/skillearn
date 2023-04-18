import os

from .recording_post_processing_service import RecordingPostProcessingService
from ..models.recording import Recording
from ..utils.logger_config import get_logger

logger = get_logger(__name__)


class DirectoryPostProcessingService:
	
	def __init__(self, data_parent_directory=os.path.join(os.getcwd(), os.path.join('../../../../../', 'data'))):
		self.data_parent_directory = data_parent_directory
		
		self.hololens_parent_directory = os.path.join(self.data_parent_directory, 'hololens')
		self.gopro_parent_directory = os.path.join(self.data_parent_directory, 'gopro')
	
	def push_gopro_to_360p_directory(self, input_directory_path, output_directory_path):
		logger.info(f'Started changing video resolution and uploading to box for {input_directory_path}')
		
		# 1. List all the files in the directory
		gopro_videos = os.listdir(input_directory_path)
		
		# 2. Convert each video to 360p
		for input_video_name in gopro_videos:
			logger.info(f'Started changing video resolution and uploading to box for {input_video_name}')
			activity_id = int(input_video_name.split("_")[0])
			recording_instance = Recording(id=input_video_name, activity_id=activity_id, is_error=False, steps=[])
			input_video_file_path = os.path.join(input_directory_path, input_video_name)
			
			output_video_name = input_video_name.replace('.MP4', '_360p.mp4')
			output_video_file_path = os.path.join(output_directory_path, output_video_name)
			
			recording_post_processing_service = RecordingPostProcessingService(recording_instance)
			recording_post_processing_service.push_go_pro_360_to_box(input_video_file_path, output_video_file_path)
			
			logger.info(f'Finished changing video resolution and uploading to box for {input_video_name}')
			
		logger.info(f'Finished changing video resolution and uploading to box for {input_directory_path}')
		
		