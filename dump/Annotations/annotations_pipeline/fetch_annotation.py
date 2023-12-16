import json
import os
import os.path as osp
import sys
import yaml


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


def load_yaml_file(file_path):
	with open(file_path, 'r') as file:
		try:
			data = yaml.safe_load(file)
			return data
		except yaml.YAMLError as e:
			print(f"Error while parsing YAML file: {e}")


initialize_paths()

from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.models.annotation import Annotation
from datacollection.user_app.backend.app.models.annotation_assignment import AnnotationAssignment


def fetch_user_id_for_activity(activity_id, annotation_assignment_list):
	for annotation_assignment in annotation_assignment_list:
		if activity_id in annotation_assignment.activities:
			return annotation_assignment.user_id


def fetch_recording_annotation(recording_id):
	recording = Recording.from_dict(db_service.fetch_recording(recording_id))
	annotation_assignments_dict = db_service.fetch_annotation_assignment()
	annotation_assignments_list = [AnnotationAssignment.from_dict(annotation_assignment_dict) for
	                               annotation_assignment_dict in annotation_assignments_dict if
	                               annotation_assignment_dict is not None]
	
	user_id = fetch_user_id_for_activity(recording.activity_id, annotation_assignments_list)
	annotation = Annotation.from_dict(db_service.fetch_annotation(str(recording.id) + "_" + str(user_id)))
	
	annotation_json = annotation.annotation_json
	step_annotations = annotation_json[0]["annotations"][0]["result"]
	
	for step_annotation in step_annotations:
		start_time = step_annotation["value"]["start"]
		end_time = step_annotation["value"]["end"]
		labels = step_annotation["value"]["labels"]
		
		print(f"Start time: {start_time}, End time: {end_time}, Labels: {labels}")


if __name__ == '__main__':
	db_service = FirebaseService()
	fetch_recording_annotation("10_16")
