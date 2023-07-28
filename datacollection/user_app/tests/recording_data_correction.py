import os
import yaml

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService

from datacollection.user_app.backend.app.utils.logger_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def create_directories(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)


class RecordingDataCorrection:
	
	def __init__(self):
		self.db_versions_dir = ""
		self.current_version = 3
		self.db_service = FirebaseService()
		
		self.activity_list = self.db_service.fetch_activities()
		self.activities = [Activity.from_dict(activity) for activity in self.activity_list if activity is not None]
	
	def update_recordings_db(self, version):
		if version is None:
			version = self.current_version
		
		db_version_path = f"../backend/info_files/db_versions/v_{version}"
		for activity in self.activities:
			activity_version_path = os.path.join(db_version_path, f"{activity.name}.yaml")
			with open(activity_version_path, 'r') as activity_recordings_yaml_file:
				activity_recordings_data = yaml.safe_load(activity_recordings_yaml_file)
			
			logger.info(f"Updating activity recordings for activity: {activity}")
			for activity_recording in activity_recordings_data:
				recording = Recording.from_dict(activity_recording)
				logger.info(f"Updating recording: {recording.id}")
				self.db_service.update_recording(recording)
				logger.info(f"Recording: {recording.id} updated")


if __name__ == '__main__':
	recording_data_correction = RecordingDataCorrection()
	recording_data_correction.update_recordings_db(version=3)
