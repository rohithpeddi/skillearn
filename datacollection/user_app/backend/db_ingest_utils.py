import os
import yaml

from datacollection.user_app.backend.firebase_service import FirebaseService
from datacollection.user_app.backend.constants import *
from datacollection.user_app.backend.models.activity import Activity
from datacollection.user_app.backend.models.recording import Recording
from datacollection.user_app.backend.models.recording_ingestion_helper import RecordingIngestionHelper
from datacollection.user_app.backend.models.user import User

from datacollection.user_app.backend.constants import DatabaseIngestion_Constants as const


class FirebaseIngestion:
	
	def __init__(self, data_directory):
		self.db_service = FirebaseService()
		self.data_directory = data_directory
	
	def ingest(self):
		pass


class UserIngestion(FirebaseIngestion):
	
	def __init__(self, data_directory):
		super().__init__(data_directory)
	
	def ingest(self):
		users_yaml_file_path = os.path.join(self.data_directory, const.USERS_YAML_FILE_NAME)
		with open(users_yaml_file_path, 'r') as users_yaml_file:
			users_data = yaml.safe_load(users_yaml_file)
		
		for user_data in users_data:
			user = User.from_dict(user_data)
			self.db_service.update_user(user)


class ActivitiesIngestion(FirebaseIngestion):
	
	def __init__(self, data_directory):
		super().__init__(data_directory)
	
	def ingest(self):
		activities_yaml_file_path = os.path.join(self.data_directory, const.ACTIVITIES_YAML_FILE_NAME)
		with open(activities_yaml_file_path, 'r') as activities_yaml_file:
			activities_data = yaml.safe_load(activities_yaml_file)
		
		for activity_data in activities_data:
			activity = Activity.from_yaml_dict(activity_data)
			self.db_service.update_activity(activity)


class ActivityRecordingsIngestion(FirebaseIngestion):
	
	def __init__(self, data_directory):
		super().__init__(data_directory)
		self.recordings_directory = os.path.join(self.data_directory, const.RECORDINGS)
	
	def ingest(self):
		activities = self.db_service.fetch_activities()
		
		def fetch_activity(name):
			for _activity in activities:
				if _activity is None:
					continue
				processed_activity_name = (_activity[const.NAME].lower()).replace(" ", "")
				if name in processed_activity_name:
					return _activity
			return None
		
		for activity_recordings_file_name in os.listdir(self.recordings_directory):
			activity_name = activity_recordings_file_name
			activity_dict = fetch_activity(activity_name)
			activity = Activity.from_dict(activity_dict)
			
			activity_recordings_yaml_file_path = os.path.join(self.recordings_directory, activity_recordings_file_name)
			with open(activity_recordings_yaml_file_path, 'r') as activity_recordings_yaml_file:
				activity_recordings_data = yaml.safe_load(activity_recordings_yaml_file)
			
			for activity_recording in activity_recordings_data:
				recording_helper = RecordingIngestionHelper.from_dict(activity_recording)
				
				# 1. Create Recording instance from the given data
				processed_recording_id = f'{activity.id}_{recording_helper.recording_id}'
				is_mistake = False
				mistakes = None
				if recording_helper.mistakes is not None:
					mistakes = recording_helper.mistakes
					is_mistake = len(recording_helper.mistakes) > 0
				
				recording = Recording(
					id=processed_recording_id,
					activity_id=activity.id,
					is_mistake=is_mistake,
					steps=recording_helper.steps,
					mistakes=mistakes
				)
				
				# 2. Push it to the database as a child of activity with corresponding activity_id
				self.db_service.update_recording(recording)


if __name__ == "__main__":
	current_directory = os.getcwd()
	info_directory = os.path.join(current_directory, "info_files")
	
	# user_ingestion = UserIngestion(info_directory)
	# user_ingestion.ingest()
	# activities_ingestion = ActivitiesIngestion(info_directory)
	# activities_ingestion.ingest()
	activity_recordings_ingestion = ActivityRecordingsIngestion(info_directory)
	activity_recordings_ingestion.ingest()
