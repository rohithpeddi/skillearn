import logging
import os.path

from boxsdk import Client, CCGAuth

from datacollection.backend.Recording import Recording
from datacollection.backend.firebase_service import FirebaseService
from datacollection.backend.constants import *

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('Created Hololens service file')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Folder structure in BOX
# - <Re_Pl_P_R_0>
# 	- Raw
# 		- Depth Ahat
# 			- Ab
# 			- Depth
# 			- Pose
# 		- PV
# 			- RGB
# 			- Pose
# 		- Spatial
# 		- GoPro.mp4
# 	- Synchronized
# 		- Depth
# 			- Ab
# 			- Depth
# 			- Pose
# 		- PV
# 			- RGB
# 			- Pose
# 		- Spatial
# 		- GoPro.mp4
# 		- GoPro_360.mp4
# 		- Hololens_360.mp4
# 		- Hololens_audio.mp4
# 		- <PretrainedFeatures>


class BoxService:

	def __init__(self):
		self.user_id = '23441227496'
		self.root_folder_id = '192253529318'
		self.client_id = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b'
		self.client_secret = 'TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'
		self.ccg_credentials = 'krr2b0dmxvnqn83ikpe6ufs58jg9t82b TTsVwLrnv9EzmKJv67yrCyUM09wJSriK'

		self.client = Client(CCGAuth(client_id=self.client_id,
									 client_secret=self.client_secret,
									 user=self.user_id))

		self.components = ["lf", "ll", "pv", "rf", "rr", "ab", "depth"]
		self.recordings_base_dir = "../"
		self.set_delete = True

	def upload_data(self, recording_instance: Recording, db_service: FirebaseService):
		# 1. Construct folder names for each component and update their status as "Pending" in Firebase
		recording_type = ERROR_RECORDINGS if recording_instance.is_error else STANDARD_RECORDINGS
		recording_folder = "{}_{}_{}_{}".format(recording_instance.activity, recording_instance.place_id,
												recording_instance.person_id, recording_instance.rec_number)

		recording_path = os.path.join(self.recordings_base_dir, recording_type)
		recording_folder_path = os.path.join(recording_path, recording_folder)

		# 	------------------------------------------------------------------------------------------------

		# 1. Create box sub-folder based on recording type.
		rt_folders_in_box = self.client.folder(self.root_folder_id).get_items()
		create_recording_type_sub_folder = True

		box_recording_type_sub_folder_id = None
		for rt_folder_in_box in rt_folders_in_box:
			if rt_folder_in_box.name == recording_type:
				create_recording_type_sub_folder = False
				box_recording_type_sub_folder_id = rt_folder_in_box.object_id
				logger.log(logging.INFO, "{} sub folder is available, re using it".format(recording_type))

		if create_recording_type_sub_folder:
			box_recording_type_sub_folder_id = (
				self.client.folder(self.root_folder_id).create_subfolder(recording_type)).object_id
			logger.log(logging.INFO, "Created {} sub folder".format(recording_type))

		# 	------------------------------------------------------------------------------------------------

		# 2. Create sub-folder with the name of the "Activity"
		rt_folders_in_box = self.client.folder(box_recording_type_sub_folder_id).get_items()
		create_activity_sub_folder = True

		box_activity_sub_folder_id = None
		for rt_folder_in_box in rt_folders_in_box:
			if rt_folder_in_box.name == recording_instance.activity:
				create_activity_sub_folder = False
				box_activity_sub_folder_id = rt_folder_in_box.object_id
				logger.log(logging.INFO, "{} sub folder is available, re using it".format(recording_instance.activity))

		if create_activity_sub_folder:
			box_activity_sub_folder_id = (
				self.client.folder(box_recording_type_sub_folder_id).create_subfolder(
					recording_instance.activity)).object_id
			logger.log(logging.INFO, "Created {} sub folder".format(recording_instance.activity))

		# 	------------------------------------------------------------------------------------------------

		# 3. Create sub-folder with the name of the "Place"
		rt_folders_in_box = self.client.folder(box_activity_sub_folder_id).get_items()
		create_place_sub_folder = True

		box_place_sub_folder_id = None
		for rt_folder_in_box in rt_folders_in_box:
			if rt_folder_in_box.name == recording_instance.place_id:
				create_place_sub_folder = False
				box_place_sub_folder_id = rt_folder_in_box.object_id
				logger.log(logging.INFO,
						   "{}-{} sub folder is available, re using it".format(PLACE, recording_instance.place_id))

		if create_place_sub_folder:
			box_place_sub_folder_id = (
				self.client.folder(box_activity_sub_folder_id).create_subfolder(
					recording_instance.place_id)).object_id
			logger.log(logging.INFO, "Created {}-{} sub folder".format(PLACE, recording_instance.place_id))

		for component in self.components:
			db_service.update_upload_queue(recording_instance, component, PENDING)

		# 	------------------------------------------------------------------------------------------------

		# 4. Create sub-folder with the name of the "Person"
		rt_folders_in_box = self.client.folder(box_place_sub_folder_id).get_items()
		create_person_sub_folder = True

		box_person_sub_folder_id = None
		for rt_folder_in_box in rt_folders_in_box:
			if rt_folder_in_box.name == recording_instance.person_id:
				create_person_sub_folder = False
				box_person_sub_folder_id = rt_folder_in_box.object_id
				logger.log(logging.INFO,
						   "{}-{} sub folder is available, re using it".format(PERSON, recording_instance.person_id))

		if create_person_sub_folder:
			box_person_sub_folder_id = (
				self.client.folder(box_place_sub_folder_id).create_subfolder(
					recording_instance.person_id)).object_id
			logger.log(logging.INFO, "Created {}-{} sub folder".format(PERSON, recording_instance.person_id))

		# 	------------------------------------------------------------------------------------------------

		# 5. Create sub-folder with the name of the "Recording Number"
		rt_folders_in_box = self.client.folder(box_person_sub_folder_id).get_items()
		create_rec_num_sub_folder = True

		box_rec_num_sub_folder_id = None
		for rt_folder_in_box in rt_folders_in_box:
			if rt_folder_in_box.name == recording_instance.rec_number:
				create_rec_num_sub_folder = False
				box_rec_num_sub_folder_id = rt_folder_in_box.object_id
				logger.log(logging.INFO,
						   "{}-{} sub folder is available, re using it".format(RECORDING_NUMBER,
																			   recording_instance.rec_number))

		if create_rec_num_sub_folder:
			box_rec_num_sub_folder_id = (
				self.client.folder(box_person_sub_folder_id).create_subfolder(
					recording_instance.rec_number)).object_id
			logger.log(logging.INFO, "Created {}-{} sub folder".format(RECORDING_NUMBER, recording_instance.rec_number))

		# 	------------------------------------------------------------------------------------------------

		db_service.update_activity_uploading_details(recording_instance, UPLOADING)

		for component in self.components:
			db_service.update_upload_queue(recording_instance, component, PENDING)

		# 6. Loop through each folder and perform the upload call into BOX
		for component in self.components:
			rt_folders_in_box = self.client.folder(box_rec_num_sub_folder_id).get_items()
			create_component_sub_folder = True

			box_component_sub_folder_id = None
			for rt_folder_in_box in rt_folders_in_box:
				if rt_folder_in_box.name == component:
					create_component_sub_folder = False
					box_component_sub_folder_id = rt_folder_in_box.object_id
					logger.log(logging.INFO, "{} sub folder is available, re using it".format(component))

			if create_component_sub_folder:
				box_component_sub_folder_id = (
					self.client.folder(box_rec_num_sub_folder_id).create_subfolder(component)).object_id
				logger.log(logging.INFO, "Created {} sub folder".format(component))

			component_recording_dir = os.path.join(recording_folder_path, component)
			db_service.update_upload_queue(recording_instance, component, UPLOADING)
			for file_name in os.listdir(component_recording_dir):
				file_path = os.path.join(component_recording_dir, file_name)
				self.client.folder(box_component_sub_folder_id).upload(file_path)
				logger.log(logging.INFO, "Uploaded {} sub folder".format(file_name))

			db_service.update_upload_queue(recording_instance, component, UPLOADED)

		# 7. Delete all the files and recordings
		db_service.update_activity_uploading_details(recording_instance, UPLOADED)
		logger.log(logging.INFO, "Uploaded all files for {}".format(recording_folder))


if __name__ == '__main__':
	box_service = BoxService()

	db_service = FirebaseService()
	recording_instance = Recording("Coffee", "5", "1", "1", False)

	box_service.upload_data(recording_instance, db_service)
