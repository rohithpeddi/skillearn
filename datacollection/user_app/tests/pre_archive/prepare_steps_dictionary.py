from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def prepare_step_idx_dictionary():
	idx_counter = 0
	base_recording_ids = [
		"18_3", "12_2", "15_2", "28_2", "8_3", "16_1", "20_9", "4_2", "10_6", "25_1", "26_4", "3_2",
		"9_2", "1_7", "22_4", "2_3", "17_3", "5_2", "27_4", "29_6", "13_5", "23_1", "7_1", "21_8"
	]
	
	idx_step_dictionary = {}
	step_idx_dictionary = {}
	for recording_id in base_recording_ids:
		recording = Recording.from_dict(db_service.fetch_recording(recording_id))
		recordings_steps = recording.steps
		for step in recordings_steps:
			if step.description not in step_idx_dictionary:
				step_idx_dictionary[step.description] = idx_counter
				idx_step_dictionary[idx_counter] = step.description
				idx_counter += 1
	
	print(idx_step_dictionary)
	db_service.update_step_dictionary(idx_step_dictionary)


if __name__ == "__main__":
	db_service = FirebaseService()
	prepare_step_idx_dictionary()
