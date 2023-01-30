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

firebase=pyrebase.initialize_app(firebaseConfig)

class FirebaseDatabaseService:

	# 1. Have this db connection constant
	def __init__(self):
		self.db = firebase.database()

	# 2. Function to push recipe details as a child to the database
	def addRecipeDetails(self, recipe_name, recipe_step_dict):
		self.db.child(INFO).child(recipe_name).set(recipe_step_dict)

	# 3. Function to get info as a child from the database
	def getDetails(self, child_name):
		return  self.db.child(child_name).get()

	# 4. Function to push update statuses and time stamps after each step is done
	def updateRecordingStepDetails(self, is_start:bool, recording_instance: Recording):
		self.db.child(RECORDINGS) \
			.child(recording_instance.recipe) \
			.child(recording_instance.kitchen_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number) \
			.child(STEPS) \
			.child(recording_instance.current_step_id) \
			.child(STEP_START_TIME if is_start else STEP_END_TIME) \
			.set(int(time.time() * 1e9))


	# 5. Function to get latest updated data with step completion status
	def getUpdatedRecordingDetails(self, recording_instance: Recording):
		recording_response = self.db.child(RECORDINGS) \
				.child(recording_instance.recipe) \
				.child(recording_instance.kitchen_id) \
				.child(recording_instance.person_id) \
				.child(recording_instance.rec_number).get()
		return recording_response

	# 6. Update recording details of the recipe
	def updateRecipeRecordingDetails(self, is_start: bool, recording_instance: Recording):
		self.db.child(RECORDINGS) \
			.child(recording_instance.recipe) \
			.child(recording_instance.kitchen_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number) \
			.child(RECIPE_RECORDING_START_TIME if is_start else RECIPE_RECORDING_END_TIME).set(int(time.time() * 1e9))

		if is_start:
			self.db.child(RECORDINGS) \
				.child(recording_instance.recipe) \
				.child(recording_instance.kitchen_id) \
				.child(recording_instance.person_id) \
				.child(recording_instance.rec_number) \
				.child(UPLOADING_STATUS).set(UPLOADED)


	# 7. Function to push update statuses and time stamps after each step is done
	def deleteRecordingStepDetails(self, recording_instance: Recording):
		self.db.child(RECORDINGS) \
			.child(recording_instance.recipe) \
			.child(recording_instance.kitchen_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number) \
			.child(STEPS) \
			.child(recording_instance.current_step_id)\
			.remove()

	# 8. Update Recipe Upload Details in Firebase - Should be called from box_util
	def updateRecipeUploadingDetails(self, recording_instance: Recording):
		self.db.child(RECORDINGS) \
			.child(recording_instance.recipe) \
			.child(recording_instance.kitchen_id) \
			.child(recording_instance.person_id) \
			.child(recording_instance.rec_number)\
			.child(UPLOADING_STATUS).set(PENDING)