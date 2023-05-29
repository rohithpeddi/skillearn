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
		self.environment_id_to_environment_map = {environment.get_id(): environment for environment in self.environments}
	
	def process_environment_recordings(self, is_missing_gopro=False):

		if is_missing_gopro:
			with open('missing_gopro.txt', 'r') as missing_gopro_text:
				missing_gopro_list = missing_gopro_text.read().splitlines()

		for environment_id in range(1, 10):
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
			
			with open('recording_info_missing.txt', 'a') as recording_info_text:
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
						recording_info_text.write(f"\t\t{activity_name} - {recording.id} - {recording.recording_info.start_time}\n")
				recording_info_text.write("\n\n")
			
			print("Finished processing environment: ", environment_id)


if __name__ == '__main__':
	firebase_utils = FirebaseUtils()
	firebase_utils.process_environment_recordings(is_missing_gopro=True)
