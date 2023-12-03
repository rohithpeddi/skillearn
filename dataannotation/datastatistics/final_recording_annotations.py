import csv
import json
import os
import os.path as osp
import sys
import yaml

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.error_tag import ErrorTag
from datacollection.user_app.backend.app.models.recording import Recording


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


initialize_paths()

from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation


def store_versioned_annotation_files(version):
	db_service = FirebaseService()
	activities_dict = db_service.fetch_activities()
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(
		recording_annotations,
		key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1]))
	)
	activity_id_recording_annotations_map = {}
	for recording_annotation in recording_annotations:
		if recording_annotation.activity_id not in activity_id_recording_annotations_map:
			activity_id_recording_annotations_map[recording_annotation.activity_id] = []
		activity_id_recording_annotations_map[recording_annotation.activity_id].append(recording_annotation)
	
	version_annotation_directory_path = f"versioned_annotations/v{version}"
	if not osp.exists(version_annotation_directory_path):
		os.makedirs(version_annotation_directory_path)
	
	for activity_id, activity_recording_annotations in activity_id_recording_annotations_map.items():
		activity_name = activity_id_to_activity_name_map[activity_id]
		activity_name = activity_name.replace(" ", "").lower()
		
		activity_annotation_file_path = osp.join(version_annotation_directory_path, f"{activity_id}_{activity_name}.yaml")
		with open(activity_annotation_file_path, "w") as activity_annotation_file:
			yaml.dump([recording_annotation.to_dict() for recording_annotation in activity_recording_annotations],
			          activity_annotation_file)


if __name__ == "__main__":
	store_versioned_annotation_files(version=1)