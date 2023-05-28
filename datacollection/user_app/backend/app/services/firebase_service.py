# This file contains all files related to firebase
import time

import pyrebase
from ..utils.constants import Firebase_Constants as const
from ..models.activity import Activity
from ..models.recording import Recording
from ..models.user import User
from ..utils.logger_config import get_logger

logger = get_logger(__name__)

firebase = None

if const.DEPLOYMENT == const.DEVELOPMENT:
	firebaseDevConfig = {
		"apiKey": "AIzaSyCzBlh4hXDXJqIBZEkcF0kXh70K6-RuEsc",
		"authDomain": "ego-proc-mistakes.firebaseapp.com",
		"projectId": "ego-proc-mistakes",
		"storageBucket": "ego-proc-mistakes.appspot.com",
		"messagingSenderId": "310348437552",
		"appId": "1:310348437552:web:77b182eafb9f4eff0af5f5",
		"databaseURL": "https://ego-proc-mistakes-default-rtdb.firebaseio.com",
	}
	
	firebase = pyrebase.initialize_app(firebaseDevConfig)
elif const.DEPLOYMENT == const.PRODUCTION:
	firebaseProdConfig = {
		"apiKey": "AIzaSyBN101vsa7m1bgoaBMhgC0POAU8TVQhU0o",
		"authDomain": "ego-proc-errors.firebaseapp.com",
		"projectId": "ego-proc-errors",
		"storageBucket": "ego-proc-errors.appspot.com",
		"messagingSenderId": "676090535211",
		"appId": "1:676090535211:web:5ffd195bd98f51820bb96e",
		"databaseURL": "https://ego-proc-errors-default-rtdb.firebaseio.com",
		"measurementId": "G-QM9RPQ6M5D"
	}
	
	firebase = pyrebase.initialize_app(firebaseProdConfig)

logger.info("----------------------------------------------------------------------")
logger.info("Setting up Firebase Service...in " + const.DEPLOYMENT + " mode ")
logger.info("----------------------------------------------------------------------")


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
		logger.info(f"Updated user in the firebase - {user.__str__()}")
	
	def fetch_user(self, user_id: int):
		return self.db.child(const.USERS).child(user_id).get().val()
	
	def remove_all_users(self):
		self.db.child(const.USERS).remove()
	
	# ---------------------- END USER ----------------------
	
	# ---------------------- BEGIN ACTIVITY ----------------------
	
	def fetch_activities(self):
		return self.db.child(const.ACTIVITIES).get().val()
	
	def update_activity(self, activity: Activity):
		self.db.child(const.ACTIVITIES).child(activity.id).set(activity.to_dict())
		logger.info(f"Updated activity in the firebase - {activity.__str__()}")
	
	def remove_all_activities(self):
		self.db.child(const.ACTIVITIES).remove()
	
	# ---------------------- END ACTIVITY ----------------------
	
	# ---------------------- BEGIN RECORDING ----------------------
	
	def update_recording(self, recording: Recording):
		self.db.child(const.RECORDINGS).child(recording.id).set(recording.to_dict())
		logger.info(f"Updated recording in the firebase - {recording.__str__()}")
	
	def fetch_user_recordings(self, user_id):
		return self.db.child(const.RECORDINGS).order_by_child(const.RECORDED_BY).equal_to(user_id).get().val()
	
	def fetch_all_activity_recordings(self, activity_id):
		return self.db.child(const.RECORDINGS).order_by_child(const.ACTIVITY_ID).equal_to(activity_id).get().val()
	
	def fetch_recording(self, recording_id):
		return self.db.child(const.RECORDINGS).child(recording_id).get().val()
	
	def remove_all_recordings(self):
		self.db.child(const.RECORDINGS).remove()
		
	def fetch_environment_recordings(self, environment):
		return self.db.child(const.RECORDINGS).order_by_child(const.ENVIRONMENT).equal_to(environment).get().val()


# ---------------------- END RECORDING ----------------------


if __name__ == "__main__":
	db_service = FirebaseService()
