import json
import os
import random
import signal

from flask import Flask, request, jsonify
from flask_cors import CORS

from datacollection.user_app.backend.constants import FlaskServer_constants as const
from datacollection.user_app.backend.services.firebase_service import FirebaseService
from datacollection.user_app.backend.models.activity import Activity
from datacollection.user_app.backend.models.mistake_tag import MistakeTag
from datacollection.user_app.backend.models.recording import Recording
from datacollection.user_app.backend.models.recording_info import RecordingInfo
from datacollection.user_app.backend.models.user import User
from datacollection.user_app.backend.services import async_service
from logger_config import logger

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})


# --------------------------------------------------------------------------------------------
# -------------------------------------- LOGIN -----------------------------------------

@app.route('/login', methods=['POST'])
def login():
	username = request.json.get('username')
	password = request.json.get('password')
	
	if not username or not password:
		logger.error("Invalid username or password")
		response = jsonify({"error": "Invalid username or password"})
	elif password == "darpa":
		users = db_service.fetch_users()
		for user in users:
			if user and user[const.USERNAME] == username:
				response = jsonify(user)
				break
	else:
		response = jsonify({"error": "Invalid username or password"})
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
	return jsonify([activity for activity in activities if activity is not None])


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
@app.route('/users/<int:user_id>/preferences/<category>', methods=['POST'])
def update_activity_preferences(user_id, category):
	try:
		request_data = request.data.decode('utf-8')
		request_data_dict = json.loads(request_data)
		
		activity_preferences = request_data_dict[const.SELECTED_ACTIVITIES]
		
		user_info = db_service.fetch_user(user_id)
		user = User.from_dict(user_info)
		
		activities = db_service.fetch_activities()
		activities = [Activity.from_dict(activity) for activity in activities if activity is not None]
		
		# Pop all the activities in user activity_preferences which are of the category selected
		user_activity_preferences = user.activity_preferences
		for activity in activities:
			if activity.category == category and activity.id in user_activity_preferences:
				user_activity_preferences.discard(activity.id)
		
		# Add the new activities to user activity_preferences
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

@app.route('/mistake_tags', methods=['GET'])
def fetch_mistake_tags():
	mistake_tags = MistakeTag.get_step_mistake_tag_list()
	return jsonify(mistake_tags)


@app.route('/users/<int:user_id>/activities/<int:activity_id>/recordings/<label>', methods=['GET'])
def fetch_activity_recording(user_id, activity_id, label):
	activity_recordings = db_service.fetch_all_activity_recordings(activity_id)
	is_mistake = (label == const.MISTAKE)
	
	response = {}
	recordings = []
	for (recording_id, recording_dict) in activity_recordings.items():
		recording = Recording.from_dict(recording_dict)
		if recording.is_mistake == is_mistake:
			recordings.append(recording)
	
	# 1. If any of the recordings are prepared by the user and recorded by the user, then return that recording
	selected_unrecorded_recordings = []
	unassigned_recordings = []
	for recording in recordings:
		if hasattr(recording, const.RECORDED_BY) and recording.recorded_by != const.DUMMY_USER_ID:
			continue
		elif not hasattr(recording, const.RECORDED_BY) or recording.recorded_by == const.DUMMY_USER_ID:
			if recording.selected_by == user_id and recording.is_prepared:
				response[const.SELECTION_TYPE] = const.PREPARED
				response[const.RECORDING_CONTENT] = recording.to_dict()
				return jsonify(response)
			elif recording.selected_by == user_id and not recording.is_prepared:
				selected_unrecorded_recordings.append(recording)
			else:
				unassigned_recordings.append(recording)
	
	# 2. Return a recording from the selected_unrecorded_recordings
	if len(selected_unrecorded_recordings) > 0:
		response[const.SELECTION_TYPE] = const.SELECTED_PREVIOUSLY
		response[const.RECORDING_CONTENT] = random.choice(selected_unrecorded_recordings).to_dict()
		return jsonify(response)
	
	# 3. Return a recording from the unassigned_recordings
	if len(unassigned_recordings) > 0:
		response[const.SELECTION_TYPE] = const.NEWLY_SELECTED
		response[const.RECORDING_CONTENT] = random.choice(unassigned_recordings).to_dict()
		return jsonify(response)


@app.route('/users/<int:user_id>/environment/<int:environment_id>/select/recordings/<recording_id>', methods=['POST'])
def select_recording(user_id, environment_id, recording_id):
	recording_dict = db_service.fetch_recording(recording_id)
	recording = Recording.from_dict(recording_dict)
	
	if recording.selected_by != const.DUMMY_USER_ID:
		if recording.selected_by != user_id:
			return "Recording already selected", 500
		else:
			return jsonify(recording.to_dict())
	
	recording.selected_by = user_id
	recording.environment = environment_id
	db_service.update_recording(recording)
	return jsonify(recording.to_dict())


# 3. Fetch all the recordings by a user
@app.route('/users/<int:user_id>/recordings', methods=['GET'])
def fetch_user_recordings(user_id):
	user_recordings = db_service.fetch_user_recordings(user_id)
	return jsonify([recording.to_dict() for recording in user_recordings])


# 4. Update activity recording
# Use this for intermediate update steps of recording instances
@app.route('/recordings/<recording_id>', methods=['POST'])
def update_recording(recording_id):
	recording_dict = json.loads(request.data)
	try:
		recording = Recording.from_dict(recording_dict)
		assert recording.id == recording_id
		db_service.update_recording(recording)
		return jsonify(recording.to_dict())
	except Exception as e:
		return "An error occurred: " + str(e), 500


# 5. Use this when recording is finished
@app.route('/recordings/<recording_id>/user/<int:user_id>', methods=['POST'])
def update_recording_finished(recording_id, user_id):
	recording_dict = json.loads(request.data)
	try:
		recording = Recording.from_dict(recording_dict)
		assert recording.id == recording_id
		recording.recorded_by = user_id
		db_service.update_recording(recording)
		
		user = User.from_dict(db_service.fetch_user(user_id))
		user.update_recording(recording.environment, recording.activity_id)
		
		db_service.update_user(user)
		return jsonify(recording.to_dict())
	except Exception as e:
		return "An error occurred: " + str(e), 500


# --------------------------------------------------------------------------------------------
# -------------------------------------- STATS -----------------------------------------

@app.route('/users/<int:user_id>/stats', methods=['GET'])
def fetch_stats(user_id):
	# 1. Fetch all the recordings by a user
	recordings = dict(db_service.fetch_user_recordings(user_id))
	
	recording_stats = {const.NUMBER_OF_RECORDINGS: 0, const.NUMBER_OF_MISTAKE_RECORDINGS: 0,
	                   const.NUMBER_OF_CORRECT_RECORDINGS: 0}
	
	user_recordings = []
	for recording_id, recording in recordings.items():
		user_recording = Recording.from_dict(recording)
		user_recordings.append(user_recording)
		recording_stats[const.NUMBER_OF_RECORDINGS] += 1
		if user_recording.is_mistake:
			recording_stats[const.NUMBER_OF_MISTAKE_RECORDINGS] += 1
		else:
			recording_stats[const.NUMBER_OF_CORRECT_RECORDINGS] += 1
	
	user_recording_stats = [recording.to_dict() for recording in user_recordings]
	
	mistake_stats = {}
	for mistake_tag in MistakeTag.get_step_mistake_tag_list():
		mistake_stats[mistake_tag] = 0
	
	for recording in user_recordings:
		if recording.is_mistake:
			for mistake in recording.mistakes:
				if mistake.tag in mistake_stats:
					mistake_stats[mistake.tag] += 1
				else:
					mistake_stats[mistake.tag] = 1
			for step in recording.steps:
				for mistake in step.mistakes:
					if mistake.tag in mistake_stats:
						mistake_stats[mistake.tag] += 1
					else:
						mistake_stats[mistake.tag] = 1
	
	stats = {const.RECORDING_STATS: recording_stats, const.MISTAKE_STATS: mistake_stats, const.USER_RECORDING_STATS: user_recording_stats}
	
	return jsonify(stats)


# --------------------------------------------------------------------------------------------
# -------------------------------------- DATA CAPTURE -----------------------------------------

@app.route("/start/recording/<recording_id>", methods=['POST'])
def start_activity_recording(recording_id):
	# 1. Fetch recording info from the request
	recording_dict = json.loads(request.data)
	try:
		recording = Recording.from_dict(recording_dict)
		child_subprocess_pid = async_service.create_async_subprocess(recording, const.ACTIVITY_RECORDING, db_service=db_service)
		db_service.update_recording(recording)
		logger.info("Started new asynchronous subprocess with PID - {}".format(child_subprocess_pid))
		response = {const.SUBPROCESS_ID: child_subprocess_pid}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/stop/recording/<recording_id>/<int:subprocess_id>", methods=['POST'])
def stop_activity_recording(recording_id, subprocess_id):
	try:
		# 1. Interrupt the process with PID
		# 2. In the interrupt process add the logic to update Firebase regarding the end of the recording
		# os.system('pkill -TERM -P {pid}'.format(pid=recording_subprocess_id))
		logger.info(f'Received signal to stop subprocess with PID - {subprocess_id}')
		os.kill(subprocess_id, signal.SIGINT)
		response = {const.STATUS: const.SUCCESS}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500


# IMPORTANT - After every schedule change the current environment parameter in Firebase Directly
if __name__ == "__main__":
	db_service = FirebaseService()
	app.run(threaded=True, host='0.0.0.0', port=5000)
