import os

from boxsdk import Client, CCGAuth

from datacollection.user_app.backend.app.models.annotation import Annotation
from ..models.activity import Activity
from ..services.firebase_service import FirebaseService
from ..models.recording import Recording
from ..utils.constants import Box_Constants as const
from ..utils.logger_config import get_logger

logger = get_logger(__name__)

# Folder structure in BOX
# - Activity
# - <Recording_ID>
# 	- Raw
# 		- Depth Ahat
# 			- Ab
# 			- Depth
# 			- Pose
# 		- PV
# 			- Frames
# 			- Pose
# 		- Microphone
# 		- Spatial
# 	- Synchronized
# 		- Depth Ahat
# 			- Ab
# 			- Depth
# 			- Pose
# 		- PV
# 			- Frames
# 			- Pose
# 		- Spatial
# 	- GoPro
# 		- GoPro.mp4
# 	    - 360p
# 	- Pretrained Features
# 	- Annotations


class BoxService:
	
	def __init__(self):
		self.user_id = '23441227496'
		self.root_folder_id = '202193575471'
		self.client_id = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b'
		self.client_secret = 'TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'
		self.ccg_credentials = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'
		
		ccg_auth = CCGAuth(client_id=self.client_id, client_secret=self.client_secret, user=self.user_id)
		self.client = Client(ccg_auth)
		
		self.db_service = FirebaseService()
		self.activities = [Activity.from_dict(activity_dict) for activity_dict in self.db_service.fetch_activities() if activity_dict is not None]
		self._create_activity_id_name_map()
	
	def _create_activity_id_name_map(self):
		self.activity_id_name_map = {}
		for activity in self.activities:
			self.activity_id_name_map[activity.id] = activity.name
	
	def _fetch_folder_id(self, folder_name: str, parent_folder_id: str) -> (bool, str):
		folders = self.client.folder(folder_id=parent_folder_id).get_items(limit=1000)
		for folder in folders:
			if folder.name == folder_name:
				return True, folder.object_id
		return False, None
	
	def _fetch_activity_folder(self, activity_name):
		is_activity_present, activity_folder_id = self._fetch_folder_id(activity_name, self.root_folder_id)
		if not is_activity_present:
			activity_folder_id = (
				self.client.folder(folder_id=self.root_folder_id).create_subfolder(activity_name)).object_id
		return activity_folder_id
	
	def _fetch_subfolder(self, parent_folder_id, subfolder_name):
		is_subfolder_present, subfolder_id = self._fetch_folder_id(subfolder_name, parent_folder_id)
		if not is_subfolder_present:
			subfolder_id = (
				self.client.folder(folder_id=parent_folder_id).create_subfolder(subfolder_name)).object_id
		return subfolder_id
	
	def _create_folder_structure(self, recording: Recording):
		activity_name = self.activity_id_name_map[recording.activity_id]
		activity_folder_id = self._fetch_activity_folder(activity_name)
		
		# Create Recording folder
		recording_folder_id = self._fetch_subfolder(activity_folder_id, recording.id)
		
		# Create Raw folder structure
		raw_folder_id = self._fetch_subfolder(recording_folder_id, const.RAW)
		raw_pv_folder_id = self._fetch_subfolder(raw_folder_id, const.PV)
		raw_depth_ahat_folder_id = self._fetch_subfolder(raw_folder_id, const.DEPTH_AHAT)
		raw_microphone_folder_id = self._fetch_subfolder(raw_folder_id, const.MICROPHONE)
		raw_spatial_folder_id = self._fetch_subfolder(raw_folder_id, const.SPATIAL)
		
		# Create Synchronized folder structure
		synchronized_folder_id = self._fetch_subfolder(recording_folder_id, const.SYNCHRONIZED)
		sync_depth_ahat_folder_id = self._fetch_subfolder(synchronized_folder_id, const.DEPTH_AHAT)
		sync_pv_folder_id = self._fetch_subfolder(synchronized_folder_id, const.PV)
		sync_microphone_folder_id = self._fetch_subfolder(synchronized_folder_id, const.MICROPHONE)
		sync_spatial_folder_id = self._fetch_subfolder(synchronized_folder_id, const.SPATIAL)
		
		# Create GoPro folder
		gopro_folder_id = self._fetch_subfolder(recording_folder_id, const.GOPRO)
		
		# Create Pretrained feature folder
		pretrained_feature_folder_id = self._fetch_subfolder(recording_folder_id, const.PRETRAINED_FEATURES)
		
		# Create Annotations folder
		annotations_folder_id = self._fetch_subfolder(recording_folder_id, const.ANNOTATIONS)
	
	def _upload_files_in_path(self, box_folder_id, folder_path):
		box_folder = self.client.folder(folder_id=box_folder_id)
		box_files = {item.name: item for item in box_folder.get_items(item_type='file')}
		
		for file_name in os.listdir(folder_path):
			if file_name not in box_files:
				file_path = os.path.join(folder_path, file_name)
				box_folder.upload(file_path)
	
	def _upload_folders_and_subfolders(self, parent_box_folder_id, parent_local_folder, folders):
		for folder in folders:
			box_folder_id = self._fetch_subfolder(parent_box_folder_id, folder)
			local_folder_path = os.path.join(parent_local_folder, folder)
			self._upload_files_in_path(box_folder_id, local_folder_path)
	
	def upload_from_NAS(self, recording, recording_folder_path):
		activity_folder_id = self._fetch_activity_folder(self.activity_id_name_map[recording.activity_id])
		recording_folder_id = self._fetch_subfolder(activity_folder_id, recording.id)
		
		raw_folder_id = self._fetch_subfolder(recording_folder_id, const.RAW)
		raw_folder_path = os.path.join(recording_folder_path, const.RAW)
		self._upload_folders_and_subfolders(raw_folder_id, raw_folder_path,
		                                    [const.PV, const.DEPTH_AHAT, const.MICROPHONE, const.SPATIAL])
		
		synchronized_folder_id = self._fetch_subfolder(recording_folder_id, const.SYNCHRONIZED)
		sync_folder_path = os.path.join(recording_folder_path, const.SYNCHRONIZED)
		self._upload_folders_and_subfolders(synchronized_folder_id, sync_folder_path,
		                                    [const.PV, const.DEPTH_AHAT, const.MICROPHONE, const.SPATIAL])
		
		gopro_folder_id = self._fetch_subfolder(recording_folder_id, const.GOPRO)
		gopro_path = os.path.join(recording_folder_path, const.GOPRO)
		self._upload_files_in_path(gopro_folder_id, gopro_path)
		
	def upload_go_pro_360_video(self, recording, file_path):
		logger.info(f'Uploading GoPro 360 video for recording {recording.id}')
		activity_folder_id = self._fetch_activity_folder(self.activity_id_name_map[recording.activity_id])
		recording_folder_id = self._fetch_subfolder(activity_folder_id, recording.id)
		gopro_folder_id = self._fetch_subfolder(recording_folder_id, const.GOPRO)
		self.client.folder(folder_id=gopro_folder_id).upload(file_path)
		logger.info(f'Uploaded GoPro 360 video for recording {recording.id}')
	
	def upload_pretrained_features(self, recording, file_path):
		activity_folder_id = self._fetch_activity_folder(self.activity_id_name_map[recording.activity_id])
		recording_folder_id = self._fetch_subfolder(activity_folder_id, recording.id)
		pretrained_feature_folder_id = self._fetch_subfolder(recording_folder_id, const.PRETRAINED_FEATURES)
		self.client.folder(folder_id=pretrained_feature_folder_id).upload(file_path)
		
	def upload_annotation(self, annotation: Annotation, backup_annotation_file_path):
		recording_id = annotation.recording_id
		activity_id = recording_id.split('_')[0]
		activity_folder_id = self._fetch_activity_folder(self.activity_id_name_map[activity_id])
		recording_folder_id = self._fetch_subfolder(activity_folder_id, recording_id)
		annotations_folder_id = self._fetch_subfolder(recording_folder_id, const.ANNOTATIONS)
		self.client.folder(folder_id=annotations_folder_id).upload(backup_annotation_file_path)


if __name__ == '__main__':
	box_service = BoxService()
