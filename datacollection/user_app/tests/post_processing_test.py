import os

from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.post_processing.directory_post_processing_service import \
    DirectoryPostProcessingService
from datacollection.user_app.backend.app.post_processing.recording_post_processing_service import RecordingPostProcessingService

# if __name__ == '__main__':
#     rec_id = '18_1'
#     rec_instance = Recording(id=rec_id, activity_id=9, is_error=False, steps=[])
#     data_dir = "../../../../data"
#     data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_dir)
#     post_processing_service = RecordingPostProcessingService(rec_instance, data_dir)
#
#     post_processing_service.process_and_push_data_to_nas()

if __name__ == '__main__':
    data_directory = "../../../../../data"
    data_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_directory)
    directory_post_processing_service = DirectoryPostProcessingService(data_directory)
    
    directory_post_processing_service.push_gopro_to_360p_directory()

