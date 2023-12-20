import os
import shutil
import time

from concurrent.futures import ThreadPoolExecutor

import pysftp

from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.post_processing.compress_data_service import CompressDataService
from datacollection.user_app.backend.app.post_processing.nas_unzipping_service import multithreading_unzip
from datacollection.user_app.backend.app.post_processing.video_conversion_service import VideoConversionService
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.services.synchronization_service import SynchronizationServiceV2
from datacollection.user_app.backend.app.utils.constants import Synchronization_Constants as const
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def process_directory(
		data_parent_directory,
		data_recording_directory_name,
		db_service,
		box_service,
		temp_local_data_directory
):
	data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
	if os.path.isdir(data_recording_directory_path):
		recording = fetch_recording(db_service, data_recording_directory_name)
		# logger.info(f"[{recording.id}] BEGIN SYNCHRONIZATION")
		# try:
		#     sync_streams(data_parent_directory, recording)
		#     temp_directories = create_temp_directories(recording, temp_local_data_directory)
		#     zip_raw_files(temp_directories, recording.id)
		#     zip_sync_files(temp_directories, recording.id)
		# except Exception as e:
		#     logger.error(f"[{recording.id}] Error while synchronizing streams {e}")
		
		try:
			upload_to_box(box_service, recording, temp_local_data_directory)
		# logger.info(f"[{recording.id}] END SYNCHRONIZATION")
		except Exception as e:
			logger.error(f"[{recording.id}] Error while uploading to box {e}")


def fetch_recording(db_service, data_recording_directory_name):
	recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
	return recording


def sync_streams(data_parent_directory, recording):
	synchronization_service = SynchronizationServiceV2(
		data_parent_directory,
		recording,
		const.BASE_STREAM,
		const.SYNCHRONIZATION_STREAMS
	)
	synchronization_service.sync_streams()


def create_temp_directories(recording, temp_local_data_directory):
	local_raw_data_directory = os.path.join(temp_local_data_directory, recording.id, const.RAW)
	local_sync_data_directory = os.path.join(temp_local_data_directory, recording.id, const.SYNC)
	directories = {
		'local_raw': local_raw_data_directory,
		'local_sync': local_sync_data_directory
	}
	for directory in directories.values():
		if not os.path.exists(directory):
			os.makedirs(directory)
	return directories


def zip_raw_files(directories, recording_id):
	compress_data(directories['local_raw'], recording_id, const.DEPTH_AHAT, const.DEPTH_ZIP, const.DEPTH, "Depth")
	compress_data(directories['local_raw'], recording_id, const.DEPTH_AHAT, const.AB_ZIP, const.AB, "Active Brightness")
	compress_data(directories['local_raw'], recording_id, const.BASE_STREAM, const.FRAMES_ZIP, const.FRAMES,
	              "pv frames")


def zip_sync_files(directories, recording_id):
	compress_data(directories['local_sync'], recording_id, const.DEPTH_AHAT, const.DEPTH_ZIP, const.DEPTH, "Depth")
	compress_data(directories['local_sync'], recording_id, const.DEPTH_AHAT, const.AB_ZIP, const.AB,
	              "Active Brightness")
	compress_data(directories['local_sync'], recording_id, const.BASE_STREAM, const.FRAMES_ZIP, const.FRAMES,
	              "pv frames")


def compress_data(directory, recording_id, parent_directory, zip_file, directory_name, log_msg):
	local_parent_directory = os.path.join(directory, parent_directory)
	local_zip_file_path = os.path.join(local_parent_directory, zip_file)
	if not os.path.exists(local_zip_file_path):
		logger.info(f"[{recording_id}] Compressing {log_msg} data")
		start_compress_time = time.time()
		CompressDataService.compress_dir(local_parent_directory, directory_name)
		total_compress_time = time.strftime(
			"%H:%M:%S",
			time.gmtime(time.time() - start_compress_time)
		)
		logger.info(f"[{recording_id}] Done compressing {log_msg} data : {total_compress_time}")
	else:
		logger.info(f"[{recording_id}] Skipping compressing {log_msg} data")


def upload_to_box(box_service, recording, temp_local_data_directory):
	logger.info(f"[{recording.id}] BEGIN UPLOADING TO BOX")
	box_service.upload_from_nas(recording, temp_local_data_directory)
	logger.info(f"[{recording.id}] END UPLOADING TO BOX")


def begin_post_processing():
	data_parent_directory = "/home/ptg/CODE/data/hololens"
	temp_local_data_directory = "/home/ptg/CODE/data/hololens"
	
	db_service = FirebaseService()
	box_service = BoxService()
	max_workers = 10
	
	logger.info(f"Preparing to synchronize using ThreadPoolExecutor with max_workers = {max_workers}")
	# Create a ThreadPoolExecutor with a suitable number of threads (e.g., 4)
	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		for data_recording_directory_name in data_recording_directories:
			executor.submit(
				process_directory,
				data_parent_directory,
				data_recording_directory_name,
				db_service,
				box_service,
				temp_local_data_directory
			)


if __name__ == '__main__':
	begin_post_processing()
# multithreading_video_conversion()
# begin_unzipping()
