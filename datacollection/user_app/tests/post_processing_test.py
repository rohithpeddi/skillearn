import os

from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.services.synchronization_service import SynchronizationServiceV2
from datacollection.user_app.backend.app.utils.constants import Synchronization_Constants as const

if __name__ == '__main__':
	data_parent_directory = "/run/user/12345/gvfs/sftp:host=10.176.140.2/NetBackup/PTG"
	
	box_service = BoxService()
	db_service = FirebaseService()
	
	for data_recording_directory_name in os.listdir(data_parent_directory):
		data_recording_directory_path = os.path.join(data_parent_directory, data_recording_directory_name)
		if os.path.isdir(data_recording_directory_path):
			recording = Recording.from_dict(db_service.fetch_recording(data_recording_directory_name))
			print("-------------------------------------***************************-------------------------------------")
			# print("=====================================")
			# print(f"Synchronizing {recording.id}")
			# print("=====================================")
			# synchronization_service = SynchronizationServiceV2(data_parent_directory, recording, const.BASE_STREAM, const.SYNCHRONIZATION_STREAMS)
			# synchronization_service.sync_streams()
			
			print("-------------------------------------")
			print(f"Uploading {recording.id}")
			print("-------------------------------------")
			box_service.upload_from_nas(recording, data_parent_directory)
			
		
		