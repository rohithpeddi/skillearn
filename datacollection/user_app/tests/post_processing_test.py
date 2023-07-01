import os

from concurrent.futures import ThreadPoolExecutor
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.post_processing.nas_unzipping_service import multithreading_unzip
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.services.synchronization_service import SynchronizationServiceV2
from datacollection.user_app.backend.app.utils.constants import Synchronization_Constants as const
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def process_directory(data_parent_directory, data_recording_directory_name, db_service, box_service):
    data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
    if os.path.isdir(data_recording_directory_path):
        recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
        logger.info("=====================================")
        logger.info(f"Synchronizing {recording.id}")
        logger.info("=====================================")
        synchronization_service = SynchronizationServiceV2(
            data_parent_directory,
            recording,
            const.BASE_STREAM,
            const.SYNCHRONIZATION_STREAMS
        )

        synchronization_service.sync_streams()

        logger.info("-------------------------------------")
        logger.info(f"Uploading {recording.id}")
        logger.info("-------------------------------------")
        box_service.upload_from_nas(recording, data_parent_directory)


def begin_post_processing():
    data_parent_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"

    db_service = FirebaseService()
    box_service = BoxService()
    max_workers = 1
    data_recording_directories = os.listdir(data_parent_directory)
    logger.info("Preparing to synchronize using ThreadPoolExecutor with max_workers = 1")
    # Create a ThreadPoolExecutor with a suitable number of threads (e.g., 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for data_recording_directory_name in data_recording_directories:
            executor.submit(
                process_directory,
                data_parent_directory,
                data_recording_directory_name,
                db_service,
                box_service
            )


def begin_unzipping():
    data_parent_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"
    db_service = FirebaseService()
    recording_list = []
    for data_recording_directory_name in os.listdir(data_parent_directory):
        data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
        if os.path.isdir(data_recording_directory_path):
            recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
            recording_list.append(recording)
    recording_list.sort(key=lambda x: x.id)
    multithreading_unzip(recording_list, data_parent_directory)


if __name__ == '__main__':
    begin_post_processing()
    # begin_unzipping()
