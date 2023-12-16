import csv
import json
import os
import os.path as osp
import sys
import yaml

from datacollection.user_app.backend.app.models.activity import Activity


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
	
	version_annotation_directory_path = f"versioned_recording_annotations/v{version}"
	if not osp.exists(version_annotation_directory_path):
		os.makedirs(version_annotation_directory_path)
	
	for activity_id, activity_recording_annotations in activity_id_recording_annotations_map.items():
		activity_name = activity_id_to_activity_name_map[activity_id]
		activity_name = activity_name.replace(" ", "").lower()
		print("------------------------------------------------------------------------")
		print(f"Storing activity annotation: {activity_id}_{activity_name}")
		activity_annotation_directory_path = osp.join(version_annotation_directory_path,
		                                              f"{activity_id}_{activity_name}")
		if not osp.exists(activity_annotation_directory_path):
			os.makedirs(activity_annotation_directory_path)
		
		for activity_recording_annotation in activity_recording_annotations:
			print(f"Storing recording annotation: {activity_recording_annotation.recording_id}")
			activity_recording_annotation_file_path = osp.join(activity_annotation_directory_path,
			                                                   f"{activity_recording_annotation.recording_id}.yaml")
			with open(activity_recording_annotation_file_path, "w") as activity_recording_annotation_file:
				yaml.dump(activity_recording_annotation.to_dict(), activity_recording_annotation_file)
		print("------------------------------------------------------------------------")


def update_versioned_annotations(version=3):
	db_service = FirebaseService()
	activities_dict = db_service.fetch_activities()
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	
	activities_directory_path = f"versioned_recording_annotations/v{version}"
	activities_list = os.listdir(activities_directory_path)
	
	for activity_directory in activities_list:
		activity_id = int(activity_directory.split("_")[0])
		print("------------------------------------------------------------------------")
		print(f"Updating activity: {activity_id}-{activity_id_to_activity_name_map[activity_id]}")
		
		activity_directory_path = osp.join(activities_directory_path, activity_directory)
		for recording_annotation_file_name in os.listdir(activity_directory_path):
			recording_id = recording_annotation_file_name[:-5]
			print(f"Updating recording: {recording_id}")
			recording_annotation_file_path = osp.join(activity_directory_path, recording_annotation_file_name)
			with open(recording_annotation_file_path, "r") as recording_annotation_file:
				recording_annotation = yaml.safe_load(recording_annotation_file)
			recording_annotation = RecordingAnnotation.from_dict(recording_annotation)
			db_service.update_recording_annotation(recording_annotation)


if __name__ == "__main__":
	# store_versioned_annotation_files(version=1)
	update_versioned_annotations(version=2)
