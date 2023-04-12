import os

from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.post_processing.post_processing_service import PostProcessingService

if __name__ == '__main__':
    rec_id = '18_1'
    rec_instance = Recording(id=rec_id, activity_id=9, is_error=False, steps=[])
    data_dir = "../../../../data"
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_dir)
    post_processing_service = PostProcessingService(rec_instance, data_dir)

    post_processing_service.process_and_push_data_to_nas()

