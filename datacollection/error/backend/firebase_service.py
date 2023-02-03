# This file contains all files related to firebase
import time

import pyrebase

from datacollection.error.backend.Recording import Recording
from datacollection.error.backend.constants import *

firebaseConfig = {
	"apiKey": "AIzaSyCZNC9vFeIwcRv_gId4i9pnGFoEDL3MZ8s",
	"authDomain": "ptg-error-detection.firebaseapp.com",
	"projectId": "ptg-error-detection",
	"storageBucket": "ptg-error-detection.appspot.com",
	"messagingSenderId": "1098480552367",
	"appId": "1:1098480552367:web:0d101c6e5d789fe902875a",
	"measurementId": "G-9X1953GC6E",
	"databaseURL": "https://ptg-error-detection-default-rtdb.firebaseio.com/",
}

firebase = pyrebase.initialize_app(firebaseConfig)


class FirebaseService:

	# 1. Have this db connection constant
	def __init__(self):
		self.db = firebase.database()

	# 2. Function to push recipe details as a child to the database
	def add_activity_details(self, recipe_name, recipe_step_dict):
		self.db.child(INFO).child(recipe_name).set(recipe_step_dict)

	# 3. Function to get info as a child from the database
	def get_details(self, child_name):
		return self.db.child(child_name).get().val()

	# 4. Function to push update statuses and time stamps after each step is done
	def update_recording_step_details(self, is_start: bool, recording_instance: Recording):
		self.db.child(STANDARD_RECORDINGS) \
			.child(recording_instance.activity) \
			.child(recording_instance.place_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number) \
			.child(STEPS) \
			.child(recording_instance.current_step_id) \
			.child(STEP_START_TIME if is_start else STEP_END_TIME) \
			.set(int(time.time() * 1e9))

	# 5. Function to get latest updated data with step completion status
	def get_updated_recording_details(self, recording_instance: Recording):
		recording_response = self.db.child(STANDARD_RECORDINGS) \
			.child(recording_instance.activity) \
			.child(recording_instance.place_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number).get().val()
		return recording_response

	# 6. Update recording details of the recipe
	def update_activity_recording_details(self, is_start: bool, recording_instance: Recording):

		if recording_instance.is_error:
			db_parent_path = self.db.child(ERROR_RECORDINGS) \
				.child(recording_instance.activity) \
				.child(recording_instance.place_id) \
				.child(recording_instance.person_id) \
				.child(recording_instance.rec_number)
		else:
			db_parent_path = self.db.child(STANDARD_RECORDINGS) \
				.child(recording_instance.activity) \
				.child(recording_instance.place_id) \
				.child(recording_instance.person_id) \
				.child(recording_instance.rec_number)

		db_parent_path.child(RECIPE_RECORDING_START_TIME if is_start else RECIPE_RECORDING_END_TIME).set(
			int(time.time() * 1e9))
		db_parent_path.child(DEVICE_IP).set(recording_instance.device_ip)
		if is_start:
			db_parent_path.child(UPLOAD_STATUS).set(PENDING)

	# 7. Function to push update statuses and time stamps after each step is done
	def delete_recording_step_details(self, recording_instance: Recording):
		self.db.child(STANDARD_RECORDINGS) \
			.child(recording_instance.activity) \
			.child(recording_instance.place_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number) \
			.child(STEPS) \
			.child(recording_instance.current_step_id) \
			.remove()

	# 8. Update Recipe Upload Details in Firebase - Should be called from box_util
	def update_activity_uploading_details(self, recording_instance: Recording):
		self.db.child(STANDARD_RECORDINGS) \
			.child(recording_instance.activity) \
			.child(recording_instance.place_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number) \
			.child(UPLOAD_STATUS).set(PENDING)
