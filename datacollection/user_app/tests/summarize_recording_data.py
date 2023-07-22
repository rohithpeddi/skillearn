import os

from datacollection.user_app.backend.app.post_processing.recording_data_summarization_service import \
	RecordingDataSummarizationService


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
	for recording_id in os.listdir(data_directory):
		summarize_recording_data(recording_id, data_directory)
		

if __name__ == "__main__":
	data_parent_directory = ""
	summarize_all_recordings(data_parent_directory)
	
