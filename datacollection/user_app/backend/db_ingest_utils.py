import os
import yaml

from datacollection.user_app.backend.firebase_service import FirebaseService
from datacollection.user_app.backend.constants import *
from datacollection.user_app.backend.models.activity import Activity
from datacollection.user_app.backend.models.user import User


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
		users_yaml_file_path = os.path.join(self.data_directory, USERS_YAML_FILE_NAME)
		with open(users_yaml_file_path, 'r') as users_yaml_file:
			users_data = yaml.safe_load(users_yaml_file)
			
		for user_data in users_data:
			user = User.from_dict(user_data)
			self.db_service.update_user_details(user)


class ActivitiesIngestion(FirebaseIngestion):
	
	def __init__(self, data_directory):
		super().__init__(data_directory)
	
	def ingest(self):
		activities_yaml_file_path = os.path.join(self.data_directory, ACTIVITIES_YAML_FILE_NAME)
		with open(activities_yaml_file_path, 'r') as activities_yaml_file:
			activities_data = yaml.safe_load(activities_yaml_file)
		
		for activity_data in activities_data:
			activity = Activity.from_yaml_dict(activity_data)
			self.db_service.update_activity_details(activity)


class ActivityRecordingsIngestion(FirebaseIngestion):
	
	def __init__(self, data_directory):
		super().__init__(data_directory)


if __name__ == "__main__":
	current_directory = os.getcwd()
	info_directory = os.path.join(current_directory, "info_files")
	
	user_ingestion = UserIngestion(info_directory)
	user_ingestion.ingest()
	activities_ingestion = ActivitiesIngestion(info_directory)
	activities_ingestion.ingest()
	# activity_recordings_ingestion = ActivityRecordingsIngestion(info_directory)
