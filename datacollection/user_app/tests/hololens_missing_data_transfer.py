from concurrent.futures import ThreadPoolExecutor

from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging
from hololens_missing_data_identifiers import check_recording_ids_difference_box_nas
setup_logging()
logger = get_logger(__name__)


def process_directory(
		data_recording_directory_name,
		db_service,
		box_service,
		data_parent_directory
):
	recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
	try:
		upload_to_box(box_service, recording, data_parent_directory)
	except Exception as e:
		logger.error(f"[{recording.id}] Error while uploading to box {e}")


def upload_to_box(box_service, recording, data_parent_directory):
	logger.info(f"[{recording.id}] BEGIN UPLOADING TO BOX")
	box_service.upload_from_nas(recording, data_parent_directory)
	logger.info(f"[{recording.id}] END UPLOADING TO BOX")


def begin_post_processing():
	data_parent_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"
	
	db_service = FirebaseService()
	box_service = BoxService()
	max_workers = 10
	
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(
		recording_annotations,
		key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1]))
	)
	
	# data_recording_directories = []
	# for recording_annotation in recording_annotations:
	# 	data_recording_directories.append(recording_annotation.recording_id)

	data_recording_directories = check_recording_ids_difference_box_nas()
	
	logger.info(f"Preparing to upload to box from NAS using ThreadPoolExecutor with max_workers = {max_workers}")
	# Create a ThreadPoolExecutor with a suitable number of threads (e.g., 4)
	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		for data_recording_directory_name in data_recording_directories:
			executor.submit(
				process_directory,
				data_recording_directory_name,
				db_service,
				box_service,
				data_parent_directory
			)


if __name__ == '__main__':
	begin_post_processing()
