import os

from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.post_processing.directory_post_processing_service import \
	DirectoryPostProcessingService
from datacollection.user_app.backend.app.post_processing.recording_post_processing_service import \
	RecordingPostProcessingService


# if __name__ == '__main__':
#     rec_id = '18_1'
#     rec_instance = Recording(id=rec_id, activity_id=9, is_error=False, steps=[])
#     data_dir = "../../../../data"
#     data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_dir)
#     post_processing_service = RecordingPostProcessingService(rec_instance, data_dir)
#
#     post_processing_service.process_and_push_data_to_nas()

def create_directory_if_not_exists(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)


if __name__ == '__main__':
	data_parent_directory = "../../../../data"
	data_parent_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_parent_directory)
	
	gopro_parent_directory = os.path.join(data_parent_directory, 'gopro')
	gopro_360p_parent_directory = os.path.join(data_parent_directory, 'gopro_360p')
	create_directory_if_not_exists(gopro_360p_parent_directory)

	hololens_parent_directory = os.path.join(data_parent_directory, 'hololens')
	
	directory_post_processing_service = DirectoryPostProcessingService(data_parent_directory)
	# directory_post_processing_service.push_data_to_NAS()
	directory_post_processing_service.push_gopro_to_360p_directory(gopro_parent_directory, gopro_360p_parent_directory)
