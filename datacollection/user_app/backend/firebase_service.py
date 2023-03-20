# This file contains all files related to firebase
import time

import pyrebase
from datacollection.user_app.backend.constants import *
from datacollection.user_app.backend.models.activity import Activity
from datacollection.user_app.backend.models.user import User

firebaseConfig = {
	"apiKey": "AIzaSyCzBlh4hXDXJqIBZEkcF0kXh70K6-RuEsc",
	"authDomain": "ego-proc-mistakes.firebaseapp.com",
	"projectId": "ego-proc-mistakes",
	"storageBucket": "ego-proc-mistakes.appspot.com",
	"messagingSenderId": "310348437552",
	"appId": "1:310348437552:web:77b182eafb9f4eff0af5f5",
	"databaseURL": "https://ego-proc-mistakes-default-rtdb.firebaseio.com",
}

firebase = pyrebase.initialize_app(firebaseConfig)


class FirebaseService:
	
	# 1. Have this db connection constant
	def __init__(self):
		self.db = firebase.database()
	
	# ---------------------- BEGIN USER ----------------------
	def update_user_details(self, user: User):
		self.db.child(DB_USERS).child(user.id).set(user.to_dict())
	
	def get_user_details(self, user: User):
		return self.db.child(DB_USERS).child(user.id).get().val()
	
	# ---------------------- END USER ----------------------
	
	# ---------------------- BEGIN ACTIVITY ----------------------
	def update_activity_details(self, activity: Activity):
		self.db.child(DB_ACTIVITIES).child(activity.id).set(activity.to_dict())
	
	def get_activity_details(self, activity: Activity):
		return self.db.child(DB_ACTIVITIES).child(activity.id).get().val()
	
	# ---------------------- END ACTIVITY ----------------------
	
	# # 2. Function to push recipe details as a child to the database
	# def add_activity_info_details(self, recipe_name, recipe_step_dict):
	# 	self.db.child(INFO).child(ACTIVITIES).child(recipe_name).set(recipe_step_dict)
	#
	# def add_info_details(self, info_child, info_dict):
	# 	self.db.child(INFO).child(info_child).set(info_dict)
	#
	# # 3. Function to get info as a child from the database
	# def get_details(self, child_name):
	# 	return self.db.child(child_name).get().val()
	#
	# # 4. Function to push update statuses and time stamps after each step is done
	# def update_recording_step_details(self, is_start: bool, recording_instance: Recording):
	# 	self.db.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 		.child(recording_instance.activity) \
	# 		.child(recording_instance.place_id) \
	# 		.child(recording_instance.person_id) \
	# 		.child(recording_instance.rec_number) \
	# 		.child(STEPS) \
	# 		.child(recording_instance.current_step_id) \
	# 		.child(STEP_START_TIME if is_start else STEP_END_TIME) \
	# 		.set(int(time.time() * 1e9))
	#
	# # 5. Function to get latest updated data_bak with step completion status
	# def get_updated_recording_details(self, recording_instance: Recording):
	# 	recording_response = self.db.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 		.child(recording_instance.activity) \
	# 		.child(recording_instance.place_id) \
	# 		.child(recording_instance.person_id) \
	# 		.child(recording_instance.rec_number).get()
	#
	# 	return recording_response.val()
	#
	# # 6. Update recording details of the recipe
	# def update_activity_recording_details(self, is_start: bool, recording_instance: Recording):
	# 	self.db.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 		.child(recording_instance.activity) \
	# 		.child(recording_instance.place_id) \
	# 		.child(recording_instance.person_id) \
	# 		.child(recording_instance.rec_number) \
	# 		.child(RECIPE_RECORDING_START_TIME if is_start else RECIPE_RECORDING_END_TIME) \
	# 		.set(int(time.time() * 1e9))
	# 	if is_start:
	# 		self.db.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 			.child(recording_instance.activity) \
	# 			.child(recording_instance.place_id) \
	# 			.child(recording_instance.person_id) \
	# 			.child(recording_instance.rec_number) \
	# 			.child(UPLOAD_STATUS).set(PENDING)
	#
	# 		self.db.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 			.child(recording_instance.activity) \
	# 			.child(recording_instance.place_id) \
	# 			.child(recording_instance.person_id) \
	# 			.child(recording_instance.rec_number) \
	# 			.child(DEVICE_IP).set(recording_instance.device_ip)
	#
	# # 7. Function to push update statuses and time stamps after each step is done
	# def delete_recording_step_details(self, recording_instance: Recording):
	# 	self.db.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 		.child(recording_instance.activity) \
	# 		.child(recording_instance.place_id) \
	# 		.child(recording_instance.person_id) \
	# 		.child(recording_instance.rec_number) \
	# 		.child(STEPS) \
	# 		.child(recording_instance.current_step_id) \
	# 		.remove()
	#
	# # 8. Update Recipe Upload Details in Firebase - Should be called from box_util
	# def update_activity_uploading_details(self, recording_instance: Recording, status):
	# 	self.db.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 		.child(recording_instance.activity) \
	# 		.child(recording_instance.place_id) \
	# 		.child(recording_instance.person_id) \
	# 		.child(recording_instance.rec_number) \
	# 		.child(UPLOAD_STATUS).set(status)
	#
	# # 9. Method to update the status of the upload queue
	# def update_upload_queue(self, recording_instance: Recording, component, status):
	# 	self.db.child(UPLOAD_QUEUE) \
	# 		.child(ERROR_RECORDINGS if recording_instance.is_mistake else STANDARD_RECORDINGS) \
	# 		.child(recording_instance.activity) \
	# 		.child(recording_instance.place_id) \
	# 		.child(recording_instance.person_id) \
	# 		.child(recording_instance.rec_number) \
	# 		.child(component).set(status)
