# This file contains all files related to firebase
import time

import pyrebase
from datacollection.user_app.backend.constants import Firebase_Constants as const
from datacollection.user_app.backend.models.activity import Activity
from datacollection.user_app.backend.models.recording import Recording
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
	
	# ---------------------- BEGIN ENVIRONMENT ----------------------
	def fetch_current_environment(self):
		return self.db.child(const.CURRENT_ENVIRONMENT).get().val()
	
	# ---------------------- END ENVIRONMENT ----------------------
	
	# ---------------------- BEGIN USER ----------------------
	def fetch_users(self):
		return self.db.child(const.USERS).get().val()
	
	def update_user(self, user: User):
		self.db.child(const.USERS).child(user.id).set(user.to_dict())
	
	def fetch_user(self, user_id: int):
		return self.db.child(const.USERS).child(user_id).get().val()
	
	# ---------------------- END USER ----------------------
	
	# ---------------------- BEGIN ACTIVITY ----------------------
	
	def fetch_activities(self):
		return self.db.child(const.ACTIVITIES).get().val()
	
	def update_activity(self, activity: Activity):
		self.db.child(const.ACTIVITIES).child(activity.id).set(activity.to_dict())
	
	# ---------------------- END ACTIVITY ----------------------
	
	# ---------------------- BEGIN RECORDING ----------------------
	
	def update_recording(self, recording: Recording):
		self.db.child(const.RECORDINGS).child(recording.id).set(recording.to_dict())
	
	def fetch_user_recordings(self, user_id):
		return self.db.child(const.RECORDINGS).order_by_child(const.RECORDED_BY).equal_to(user_id).get().val()
	
	def fetch_all_activity_recordings(self, activity_id):
		return self.db.child(const.RECORDINGS).order_by_child(const.ACTIVITY_ID).equal_to(activity_id).get().val()
	
	def fetch_recording(self, recording_id):
		return self.db.child(const.RECORDINGS).child(recording_id).get().val()


# ---------------------- END RECORDING ----------------------


if __name__ == "__main__":
	db_service = FirebaseService()
	db_service.fetch_users()