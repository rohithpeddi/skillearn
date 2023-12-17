from datacollection.user_app.backend.app.post_processing.recording_data_summarization_service import \
	RecordingDataSummarizationService
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def make_shareable_box_links():
	box_service.make_data_shareable()


def update_file_download_links():
	logger.info("Updating file download links")
	box_root_folder_id = box_service.root_folder_id
	box_root_folder = box_service.client.folder(folder_id=box_root_folder_id)
	
	# Activity folders are the first level of folders in the root folder
	for activity_folder in box_root_folder.get_items():
		logger.info(f"=========================================================================")
		logger.info(f"Updating file download links for activity folder {activity_folder.name}")
		# Recording folders are the second level of folders in the activity folder
		for recording_folder in activity_folder.get_items():
			logger.info(f"-------------------------------------------------------------------------")
			logger.info(f"Updating file download links for recording folder {recording_folder.name}")
			# Recording Specific folders are the third level of folders in the recording folder
			# Fetching download summary for each recording id
			recording_id = recording_folder.name
			try:
				recording_data_summarization_service = RecordingDataSummarizationService(
					recording_id, None, None
				)
				recording_data_summarization_service.update_recording_summary_download_links(recording_folder)
			except Exception as e:
				logger.error(f"[{recording_id}] Error while updating file download links for recording {e}")
				continue
	
	logger.info("Finished updating file download links")


if __name__ == '__main__':
	box_service = BoxService()
	# make_shareable_box_links()
	update_file_download_links()