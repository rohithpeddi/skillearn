import os.path as osp
import sys
import yaml


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


def load_yaml_file(file_path):
	with open(file_path, 'r') as file:
		try:
			data = yaml.safe_load(file)
			return data
		except yaml.YAMLError as e:
			print(f"Error while parsing YAML file: {e}")


initialize_paths()

from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.models.recording import Recording
from dataannotation.datacleaning.models.environment import Environment
from datacollection.user_app.backend.app.models.activity import Activity


class FirebaseUtils:
	
	def __init__(self):
		self.db_service = FirebaseService()
		
		self.environments_info_list = load_yaml_file(
			'../../datacollection/user_app/backend/info_files/environments.yaml')
		self.activities_dict = self.db_service.fetch_activities()
		self.activities = [Activity.from_dict(activity) for activity in self.activities_dict if activity is not None]
		self.activity_id_to_activity_name_map = {activity.id: activity.name for activity in self.activities}
		
		self.environments = [Environment.from_dict(environment) for environment in self.environments_info_list]
		self.environment_id_to_environment_map = {environment.get_id(): environment for environment in
		                                          self.environments}
	
	def process_environment_recordings(self, is_missing_gopro=False):
		
		if is_missing_gopro:
			with open('missing_gopro.txt', 'r') as missing_gopro_text:
				missing_gopro_list = missing_gopro_text.read().splitlines()
		
		for environment_id in range(1, 12):
			print(f"Processing environment {environment_id}...")
			environment_recordings = dict(self.db_service.fetch_environment_recordings(environment_id))
			
			if environment_id not in self.environment_id_to_environment_map:
				print(f"Environment {environment_id} not found!")
				continue
			
			environment = self.environment_id_to_environment_map[environment_id]
			
			user_recordings = {}
			for recording_id, recording_dict in environment_recordings.items():
				recording = Recording.from_dict(recording_dict)
				user_recordings.setdefault(recording.selected_by, []).append(recording)
			
			with open('recording_info_selected.txt', 'a') as recording_info_text:
				recording_info_text.write(
					f"------------------------------------------------------------------------ \n")
				recording_info_text.write(f"Environment {environment_id}:\n")
				recording_info_text.write(
					f"------------------------------------------------------------------------ \n")
				for user_id, recordings in user_recordings.items():
					if user_id < 0 or user_id >= 9:
						continue
					
					username = environment.get_user_environment(user_id).get_username()
					environment_name = environment.get_user_environment(user_id).get_environment_name()
					
					if is_missing_gopro:
						if all(recording.id not in missing_gopro_list for recording in recordings):
							continue
					
					recording_info_text.write(f"\tUser {user_id}: {username} recorded at {environment_name}\n")
					for recording in recordings:
						if is_missing_gopro:
							if recording.id not in missing_gopro_list:
								continue
						
						if recording.activity_id not in self.activity_id_to_activity_name_map:
							continue
						activity_name = self.activity_id_to_activity_name_map[recording.activity_id]
						recording_info_text.write(
							f"\t\t{activity_name} - {recording.id} - {recording.recording_info.start_time}\n")
				recording_info_text.write("\n\n")
			
			print("Finished processing environment: ", environment_id)
	
	def tackle_recording_repetition(self, recording_id, recording_one_environment, recording_one_selected_by,
	                                recording_two_environment, recording_two_selected_by):
		recording = self.db_service.fetch_recording(recording_id)
		
		activity_id, recording_num = recording_id.split('_')
		first_recording_num = int(recording_num)
		second_recording_num = first_recording_num + 100
		
		first_recording = Recording.from_dict(recording)
		first_recording.id = activity_id + '_' + str(first_recording_num)
		first_recording.selected_by = recording_one_selected_by
		first_recording.environment = recording_one_environment
		first_recording.recorded_by = recording_one_selected_by
		
		second_recording = Recording.from_dict(recording)
		second_recording.id = activity_id + '_' + str(second_recording_num)
		second_recording.selected_by = recording_two_selected_by
		second_recording.environment = recording_two_environment
		second_recording.recorded_by = recording_two_selected_by
		
		self.db_service.update_recording(first_recording)
		self.db_service.update_recording(second_recording)
	
	def change_user_recordings_environment(self, user_id, old_environment_id, new_environment_id):
		user_recordings = dict(self.db_service.fetch_user_recordings(user_id))
		user_environment_recordings = []
		for recording_id, recording_dict in user_recordings.items():
			recording = Recording.from_dict(recording_dict)
			if recording.environment == old_environment_id:
				user_environment_recordings.append(recording)
		
		for recording in user_environment_recordings:
			recording.environment = new_environment_id
			self.db_service.update_recording(recording)
			
	def fetch_all_recordings(self):
		activities_dict_list = self.db_service.fetch_activities()
		activities = [Activity.from_dict(activity_dict) for activity_dict in activities_dict_list if activity_dict is not None]
		
		for activity in activities:
			activity_recordings_dict = dict(self.db_service.fetch_all_activity_recordings(activity.id))
			activity_recordings = [Recording.from_dict(recording_dict) for recording_dict in activity_recordings_dict.values()]
			
			with open("activity_recordings.txt", "a") as activity_recordings_file:
				activity_recordings_file.write(f"------------------------------------------------------------------------ \n")
				activity_recordings_file.write(f"Activity {activity.id} - {activity.name}:\n")
				activity_recordings_file.write(f"------------------------------------------------------------------------ \n")
				for recording in activity_recordings:
					if recording.selected_by == -1:
						continue
					activity_recordings_file.write(f"\t{recording.id} recorded at {recording.environment} by {recording.selected_by} on {recording.recording_info.start_time}\n")
				activity_recordings_file.write("\n\n")


if __name__ == '__main__':
	firebase_utils = FirebaseUtils()
	# firebase_utils.fetch_all_recordings()
	firebase_utils.process_environment_recordings(is_missing_gopro=False)
# firebase_utils.change_user_recordings_environment(
# 	user_id=8,
# 	old_environment_id=2,
# 	new_environment_id=2
# )

# firebase_utils.tackle_recording_repetition(
# 	recording_id='1_43',
# 	recording_one_environment=1,
# 	recording_one_selected_by=7,
# 	recording_two_environment=1,
# 	recording_two_selected_by=7
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='7_35',
# 	recording_one_environment=1,
# 	recording_one_selected_by=1,
# 	recording_two_environment=1,
# 	recording_two_selected_by=1
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='9_8',
# 	recording_one_environment=9,
# 	recording_one_selected_by=7,
# 	recording_two_environment=2,
# 	recording_two_selected_by=7
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='12_19',
# 	recording_one_environment=6,
# 	recording_one_selected_by=3,
# 	recording_two_environment=6,
# 	recording_two_selected_by=5
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='18_1',
# 	recording_one_environment=1,
# 	recording_one_selected_by=8,
# 	recording_two_environment=6,
# 	recording_two_selected_by=8
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='21_3',
# 	recording_one_environment=1,
# 	recording_one_selected_by=1,
# 	recording_two_environment=1,
# 	recording_two_selected_by=1
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='25_9',
# 	recording_one_environment=6,
# 	recording_one_selected_by=2,
# 	recording_two_environment=7,
# 	recording_two_selected_by=5
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='26_36',
# 	recording_one_environment=7,
# 	recording_one_selected_by=6,
# 	recording_two_environment=6,
# 	recording_two_selected_by=2
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='29_29',
# 	recording_one_environment=7,
# 	recording_one_selected_by=8,
# 	recording_two_environment=7,
# 	recording_two_selected_by=1
# )
#
# firebase_utils.tackle_recording_repetition(
# 	recording_id='1_36',
# 	recording_one_environment=1,
# 	recording_one_selected_by=3,
# 	recording_two_environment=1,
# 	recording_two_selected_by=3
# )
