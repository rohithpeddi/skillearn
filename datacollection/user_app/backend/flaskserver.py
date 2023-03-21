from typing import List

from datacollection.user_app.backend.models.recording import Recording
from datacollection.user_app.backend.models.user import User
from logger_config import logger
from flask import Flask, request, jsonify

from datacollection.user_app.backend.firebase_service import FirebaseService
from datacollection.user_app.backend.constants import FlaskServer_constants as const

app = Flask(__name__)


# --------------------------------------------------------------------------------------------
# -------------------------------------- LOGIN -----------------------------------------

@app.route('/login', methods=['POST'])
def login():
	username = request.json.get('username')
	password = request.json.get('password')
	
	if not username or not password:
		logger.error("Invalid username or password")
		response = jsonify({"error": "Invalid username or password"}), 400
	elif password == "darpa":
		users = db_service.fetch_users()
		for user in users:
			if user and user[const.USERNAME] == username:
				response = jsonify({"user_id": user[const.ID]})
				break
	else:
		response = jsonify({"error": "Invalid username or password"}), 401
	
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response


# --------------------------------------------------------------------------------------------
# -------------------------------------- ENVIRONMENT -----------------------------------------

@app.route('/environment', methods=['GET'])
def fetch_environment():
	environment = db_service.fetch_current_environment()
	return jsonify(environment)


# --------------------------------------------------------------------------------------------
# -------------------------------------- PREFERENCES -----------------------------------------

# 1. Fetch all activity information
@app.route('/activities', methods=['GET'])
def fetch_activities():
	activities = db_service.fetch_activities()
	return jsonify(activities)


# 2. Fetch all user related information
# Contains - the following information
# a. User ID
# b. Username
# c. User Activity Preferences
# d. User Recording Schedules
@app.route('/users/<int:user_id>/info', methods=['GET'])
def fetch_user_info(user_id):
	user_info = db_service.fetch_user(user_id=user_id)
	return jsonify(user_info)


# 3. End point to build all the user schedules based on preference selection
@app.route('/users/<int:user_id>/preferences', methods=['POST'])
def update_activity_preferences(user_id):
	activity_preferences: List[int] = request.values
	try:
		user_info = db_service.fetch_user(user_id)
		user = User.from_dict(user_info)
		user.update_preferences(activity_preferences)
		user.build_all_environment_schedules()
		
		db_service.update_user(user)
		
		return jsonify(user.to_dict())
	except Exception as e:
		return "An error occurred: " + str(e), 500


# --------------------------------------------------------------------------------------------
# -------------------------------------- RECORDING -----------------------------------------

# 1. First fetches user info which have all information about all schedules
# 2. Fetch an unassigned recording information for an activity
@app.route('/activities/<int:activity_id>/unassigned/recordings', methods=['GET'])
def fetch_unassigned_activity_recording(activity_id):
	activity_recordings = db_service.fetch_activity_recordings(activity_id)[const.ACTIVITY_RECORDINGS]
	unassigned_recordings = []
	for activity_recording in activity_recordings:
		if activity_recording[const.RECORDED_BY] is not None:
			unassigned_recordings.append(activity_recording)
	return jsonify(unassigned_recordings)


# 3. Fetch all the recordings by a user
@app.route('/users/<int:user_id>/recordings', methods=['GET'])
def fetch_user_recordings(user_id):
	recordings = db_service.fetch_recordings()
	user_recordings = []
	for idx, (activity_id, activity_recording_info) in enumerate(recordings.items()):
		activity_recordings = activity_recording_info[const.ACTIVITY_RECORDINGS]
		for activity_recording in activity_recordings:
			if const.RECORDED_BY in activity_recording and activity_recording[const.RECORDED_BY] is not None and \
					activity_recording[const.RECORDED_BY] == user_id:
				user_recordings.append(activity_recording)
	return jsonify(user_recordings)


# 4. Update activity recording
# Use this for intermediate update steps of recording instances
@app.route('/recordings/<int:recording_id>', methods=['POST'])
def update_recording(recording_id):
	recording_dict = request.values
	try:
		recording = Recording.from_dict(recording_dict)
		assert recording.id == recording_id
		db_service.update_recording(recording)
	except Exception as e:
		return "An error occurred: " + str(e), 500


# 5. Use this when recording is finished
@app.route('/recordings/<int:recording_id>/user/<int:user_id>', methods=['POST'])
def update_recording_finished(recording_id, user_id):
	recording_dict = request.values
	try:
		recording = Recording.from_dict(recording_dict)
		assert recording.id == recording_id
		db_service.update_recording(recording)
		
		user = User.from_dict(db_service.fetch_user(user_id))
		user.update_recording(recording.environment, recording.activity_id)
		
		db_service.update_user(user)
	except Exception as e:
		return "An error occurred: " + str(e), 500


# --------------------------------------------------------------------------------------------
# -------------------------------------- COMMON -----------------------------------------

@app.after_request
def add_cors_headers(response):
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response


# IMPORTANT - After every schedule change the current environment parameter in Firebase Directly
if __name__ == "__main__":
	db_service = FirebaseService()
	app.run(threaded=True, host='0.0.0.0', port=5000)
