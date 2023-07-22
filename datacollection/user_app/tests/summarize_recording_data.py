import os

from datacollection.user_app.backend.app.post_processing.recording_data_summarization_service import \
	RecordingDataSummarizationService
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging
from datacollection.user_app.backend.app.utils.constants import Recording_Constants as const

setup_logging()
logger = get_logger(__name__)


def check_if_spatial_is_valid(recording_id):
	invalid_spatial_recordings = [
		"20_17", "13_5", "12_19", "2_8", "15_33", "23_5", "4_22", "8_31", "27_49", "29_35",
		"1_10", "4_35", "18_24", "26_39", "10_16", "28_28", "2_38", "5_3", "9_13", "25_41",
		"7_38", "17_8", "28_26", "22_26", "5_44", "26_19", "27_18", "7_19", "5_27", "22_4",
		"5_15", "9_15", "7_135", "15_2", "12_51", "2_28", "15_46", "8_11", "9_22", "1_19", "4_30", "5_37"]
	if recording_id in invalid_spatial_recordings:
		return False
	return True


def summarize_recording_data(recording_id, data_directory):
	is_spatial_enabled = check_if_spatial_is_valid(recording_id)
	recording_data_directory = os.path.join(data_directory, recording_id)
	recording_summarization_service = RecordingDataSummarizationService(
		recording_id,
		recording_data_directory,
		is_spatial_enabled
	)


def summarize_all_recordings(data_directory):
	logger.info("Removing all recording summaries from the database")
	db_service.remove_all_recording_summaries()
	logger.info("Finished removing all recording summaries from the database")
	
	recording_directories = os.listdir(data_directory)
	
	def sort_key(file_name):
		parts = file_name.split("_")
		return int(parts[0]), int(parts[1])
	
	sorted_recording_directories = sorted(recording_directories, key=sort_key)
	
	for recording_id in sorted_recording_directories:
		logger.info(f"Summarizing recording {recording_id}")
		summarize_recording_data(recording_id, data_directory)
		logger.info(f"Finished summarizing recording {recording_id}")


if __name__ == "__main__":
	db_service = FirebaseService()
	box_service = BoxService()
	data_parent_directory = ""
	summarize_all_recordings(data_parent_directory)
