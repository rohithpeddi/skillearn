from typing import List

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
		users = db_service.get_users()
		for user in users:
			if user and user[const.USERNAME] == username:
				response = jsonify({"user_id": user[const.ID]})
				break
	else:
		response = jsonify({"error": "Invalid username or password"}), 401
	
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response


@app.route('/environment', methods=['GET'])
def fetch_environment():
	environment = db_service.fetch_current_environment()
	return jsonify(environment)


# --------------------------------------------------------------------------------------------
# -------------------------------------- PREFERENCES -----------------------------------------

# 1. Fetch all activity information
@app.route('/activities', methods=['GET'])
def fetch_activities():
	activities = db_service.get_activities()
	return jsonify(activities)


# 2. Fetch all user related information
# Contains - the following information
# a. User ID
# b. Username
# c. User Activity Preferences
# d. User Recording Schedules
@app.route('/users/<int:user_id>/info', methods=['GET'])
def fetch_user_info(user_id):
	user_info = db_service.fetch_user_info(user_id=user_id)
	return jsonify(user_info)


# 3. End point to build all the user schedules based on preference selection
@app.route('/users/<int:user_id>/preferences', methods=['POST'])
def update_activity_preferences(user_id):
	activity_preferences: List[int] = request.values
	try:
		user_info = db_service.fetch_user_info(user_id)
		user = User.from_dict(user_info)
		user.update_preferences(activity_preferences)
		user.build_all_environment_schedules()
		
		db_service.update_user_details(user)
		
		return jsonify(user.to_dict())
	except Exception as e:
		return "An error occurred: " + str(e), 500


# --------------------------------------------------------------------------------------------
# -------------------------------------- RECORDING -----------------------------------------

# 1. First fetches user info which have all information about all schedules


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
