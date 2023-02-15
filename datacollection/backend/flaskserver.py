import os
import signal
import json

from flask import Flask, request, jsonify
import logging

from datacollection.error.backend.Recording import Recording
from datacollection.error.backend.async_recipe_recording import create_async_subprocess
from datacollection.error.backend.firebase_service import FirebaseService
from datacollection.error.backend.hololens_service import HololensService
from datacollection.error.backend.util import activity_info_text_to_database
from constants import *

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This message will get logged on to a file')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)


def get_recording_instance(recording_details, is_step):
	recording_instance = Recording(
		recording_details.get(ACTIVITY),
		recording_details.get(PLACE_ID),
		recording_details.get(PERSON_ID),
		recording_details.get(RECORDING_NUMBER),
		True if recording_details.get(IS_ERROR) == "True" else False
	)
	if is_step:
		recording_instance.set_current_step_id(recording_details.get(STEP_ID))
	else:
		recording_instance.set_device_ip(recording_details.get(DEVICE_IP))

	return recording_instance


@app.route("/info", methods=['GET'])
def info():
	info_json = db_service.get_details(INFO)
	response = jsonify(info_json)
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response


@app.route("/record/activity/start", methods=['POST'])
def start_activity_recording():
	recording_details = request.values
	# 1. Start Async Service of Hololens data_bak capture and get PID of the process
	recording_instance = get_recording_instance(recording_details=recording_details, is_step=False)
	try:
		child_subprocess_pid = create_async_subprocess(recording_instance, ACTIVITY_RECORD_ASYNC_OPERATION)
		logger.log(logging.INFO, "Started new asynchronous subprocess with PID - {}".format(child_subprocess_pid))
		response = {STATUS: SUCCESS, SUBPROCESS_ID: child_subprocess_pid}
		response = jsonify(response)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/record/activity/stop", methods=['POST'])
def stop_activity_recording():
	recording_details = request.values
	# 1. Interrupt the process with PID
	recording_subprocess_id = int(recording_details.get(SUBPROCESS_ID))
	try:
		# 2. In the interrupt process add the logic to update Firebase regarding the end of the recording
		# os.system('pkill -TERM -P {pid}'.format(pid=recording_subprocess_id))
		logger.log(logging.INFO, "Received signal to stop subprocess with PID - {}".format(recording_subprocess_id))
		os.kill(recording_subprocess_id, signal.SIGINT)
		response = {STATUS: SUCCESS}
		response = jsonify(response)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/record/step/start", methods=['POST'])
def start_step_recording():
	recording_details = request.values
	# 1. Update start timestamp of the RKPT chain in Firebase
	recording_instance = get_recording_instance(recording_details=recording_details, is_step=True)
	try:
		db_service.update_recording_step_details(is_start=True, recording_instance=recording_instance)
		logging.log(logging.INFO, "Updated step starting details")
		response = {STATUS: SUCCESS}
		response = jsonify(response)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/record/step/stop", methods=['POST'])
def stop_step_recording():
	recording_details = request.values
	# 1. Update start timestamp of the RKPT chain in Firebase
	recording_instance = get_recording_instance(recording_details=recording_details, is_step=True)
	try:
		db_service.update_recording_step_details(is_start=False, recording_instance=recording_instance)
		logging.log(logging.INFO, "Updated step ending details")
		response = {STATUS: SUCCESS}
		response = jsonify(response)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/record/status", methods=['GET'])
def get_recording_status():
	recording_details = request.values
	recording_instance = get_recording_instance(recording_details=recording_details, is_step=False)
	try:
		recording_status = db_service.get_updated_recording_details(recording_instance)
		logging.log(logging.INFO, "Fetched recording status details")
		response = {STATUS: SUCCESS, RECORDING_STATUS: recording_status}
		response = jsonify(response)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/upload", methods=['POST'])
def upload():
	recording_details = request.values
	recording_instance = get_recording_instance(recording_details=recording_details, is_step=False)
	try:
		child_subprocess_pid = create_async_subprocess(recording_instance, UPLOAD_ASYNC_OPERATION)
		logger.log(logging.INFO, "Started new asynchronous subprocess with PID - {}".format(child_subprocess_pid))
		response = {STATUS: SUCCESS, SUBPROCESS_ID: child_subprocess_pid}
		response = jsonify(response)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/upload/status", methods=['POST'])
def upload_status():
	status_json = db_service.get_details(UPLOAD_QUEUE)
	response = jsonify(status_json)
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response


@app.route("/delete", methods=['POST'])
def delete():
	recording_details = request.values
	recording_instance = get_recording_instance(recording_details=recording_details, is_step=True)
	try:
		db_service.delete_recording_step_details(recording_instance=recording_instance)
		logging.log(logging.INFO, "Deleted step details")
		response = {STATUS: SUCCESS}
		response = jsonify(response)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	except Exception as e:
		return "An error occurred: " + str(e), 500


if __name__ == "__main__":
	db_service = FirebaseService()
	# infoTextToDatabase(dbService, "info_files/activity_details.txt")

	# process_id = create_async_subprocess()
	# print("Started new asynchronous subprocess with PID", process_id)
	# time.sleep(10)
	# os.kill(process_id, signal.SIGINT)

	# This app runs on port 5000
	# app.run(threaded=True, host='0.0.0.0', debug=True)
	app.run(threaded=True, host='0.0.0.0', port=5000)
