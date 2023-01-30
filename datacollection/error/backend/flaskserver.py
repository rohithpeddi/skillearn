import os
import signal

from flask import Flask, request, jsonify
import logging

from datacollection.error.backend.Recording import Recording
from datacollection.error.backend.async_recipe_recording import create_async_subprocess
from datacollection.error.backend.firebase_service import FirebaseDatabaseService
from datacollection.error.backend.util import infoTextToDatabase
from constants import *

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This message will get logged on to a file')
logger=logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

def getRecordingInstance(recording_details, is_step):
	recording_instance = Recording(
		recording_details[RECIPE],
		recording_details[KITCHEN_ID],
		recording_details[PERSON_ID],
		recording_details[RECORDING_NUMBER]
	)

	if is_step:
		recording_instance.setCurrentStepId(recording_details[STEP_ID])

	return recording_instance

@app.route("/info")
def info():
	infoJson = dbService.getDetails("info")
	return jsonify(infoJson)

@app.route("/record/recipe/start", methods=['POST'])
def startRecipeRecording():
	recording_details = request.json
	# 1. Start Async Service of Hololens data capture and get PID of the process
	recording_instance = getRecordingInstance(recording_details=recording_details, is_step=False)
	try:
		child_subprocess_pid = create_async_subprocess(recording_instance)
		logger.log(logging.INFO, "Started new asynchronous subprocess with PID - {}".format(child_subprocess_pid))
		response = {STATUS: SUCCESS, SUBPROCESS_ID: child_subprocess_pid}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/record/recipe/stop", methods=['POST'])
def stopRecipeRecording():
	recording_details = request.json
	# 1. Interrupt the process with PID
	recording_subprocess_id = recording_details[SUBPROCESS_ID]
	try:
		# 2. In the interrupt process add the logic to update Firebase regarding the end of the recording
		os.kill(recording_subprocess_id, signal.SIGINT)
		response = {STATUS: SUCCESS}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/record/step/start", methods=['POST'])
def startStepRecording():
	recording_details = request.json
	# 1. Update start timestamp of the RKPT chain in Firebase
	recording_instance = getRecordingInstance(recording_details=recording_details, is_step=True)
	try:
		dbService.updateRecordingStepDetails(is_start=True, recording_instance=recording_instance)
		logging.log(logging.INFO, "Updated step starting details")
		response = {STATUS: SUCCESS}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500

@app.route("/record/step/stop", methods=['POST'])
def stopStepRecording():
	recording_details = request.json
	# 1. Update start timestamp of the RKPT chain in Firebase
	recording_instance = getRecordingInstance(recording_details=recording_details, is_step=True)
	try:
		dbService.updateRecordingStepDetails(is_start=False, recording_instance=recording_instance)
		logging.log(logging.INFO, "Updated step ending details")
		response = {STATUS: SUCCESS}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/record/status", methods=['GET'])
def getRecordingStatus():
	recording_details = request.json
	recording_instance = getRecordingInstance(recording_details=recording_details, is_step=False)
	try:
		recording_status = dbService.getUpdatedRecordingDetails(recording_instance)
		logging.log(logging.INFO, "Fetched recording status details")
		response = {STATUS: SUCCESS, RECORDING_STATUS: recording_status}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500


@app.route("/upload", methods=['POST'])
def upload():
	recording_details = request.json
	recording_instance = getRecordingInstance(recording_details=recording_details, is_step=False)
	# TODO : Add Box Logic
	# TODO: Can be included as an async process also
	# TODO: Should also update Firebase DB after uploading is done.
	pass

@app.route("/delete", methods=['POST'])
def delete():
	recording_details = request.json
	recording_instance = getRecordingInstance(recording_details=recording_details, is_step=True)
	try:
		dbService.deleteRecordingStepDetails(recording_instance=recording_instance)
		logging.log(logging.INFO, "Deleted step details")
		response = {STATUS: SUCCESS}
		return jsonify(response)
	except Exception as e:
		return "An error occurred: " + str(e), 500



if __name__=="__main__":
	dbService = FirebaseDatabaseService()
	infoTextToDatabase(dbService, "recipe_details.txt")

	# process_id = create_async_subprocess()
	# print("Started new asynchronous subprocess with PID", process_id)
	# time.sleep(10)
	# os.kill(process_id, signal.SIGINT)

	# This app runs on port 5000
	# app.run(threaded=True, host='0.0.0.0', debug=True)
	app.run(threaded=True, host='0.0.0.0')

