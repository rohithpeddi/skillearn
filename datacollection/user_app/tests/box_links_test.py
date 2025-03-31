from datacollection.user_app.backend.app.post_processing.recording_data_summarization_service import \
    RecordingDataSummarizationService
from datacollection.user_app.backend.app.services.box_service import BoxService, BoxServiceV2
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def make_shareable_box_links():
    box_service.make_data_shareable()


def get_shareable_box_links():
    box_service.get_hierarchical_links()


def update_file_download_links():
    logger.info("Updating file download links")
    box_root_folder_id = box_service.root_folder_id
    box_root_folder = box_service.client.folder(folder_id=box_root_folder_id)
    
    required_recording_ids = ['1_10', '1_19', '2_38', '2_8', '2_28', '4_35', '4_30', '4_22', '5_27', '5_15', '5_44',
                              '5_37', '7_38', '7_19', '7_135', '8_11', '8_31', '9_13', '9_15', '9_22', '10_16',
                              '12_51', '12_19', '13_5', '15_46', '15_2', '15_33', '17_8', '18_24', '20_17', '22_26',
                              '22_4', '23_5', '25_41', '26_19', '26_39', '27_49', '27_18', '28_28', '28_26', '29_35']
    
    # Activity folders are the first level of folders in the root folder
    activity_folder_list = box_root_folder.get_items()
    for activity_folder in activity_folder_list:
        logger.info(activity_folder.name)
    
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
            if recording_id not in required_recording_ids:
                logger.info(f"[{recording_id}] Skipping recording since it is not in required recording ids")
                continue
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
    box_service = BoxServiceV2()
    get_shareable_box_links()
    # make_shareable_box_links()
    # update_file_download_links()
