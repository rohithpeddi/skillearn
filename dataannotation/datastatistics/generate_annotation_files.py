import json
import os
import os.path as osp
import sys
import yaml

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.error_tag import ErrorTag


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


def generate_step_annotation_csv():
	annotation_csv_path = "annotation_csvs/step_annotations.csv"
	os.makedirs(os.path.dirname(annotation_csv_path), exist_ok=True)
	step_idx_description_global_map = {}
	with open(annotation_csv_path, "w") as f:
		for recording_annotation in recording_annotations:
			recording_id = recording_annotation.recording_id
			for step_annotation in recording_annotation.step_annotations:
				step_id = step_annotation.step_id
				step_description = step_annotation.description
				step_start_time = step_annotation.start_time
				step_end_time = step_annotation.end_time
				has_errors = len(step_annotation.errors) > 0
				step_annotation_str = f"{recording_id},{step_id},{step_start_time},{step_end_time},{step_description},{has_errors}"
				f.write(step_annotation_str)
				f.write("\n")
				if step_id not in step_idx_description_global_map:
					step_idx_description_global_map[step_id] = step_description
	step_idx_description_annotation_csv_path = "annotation_csvs/step_idx_description.csv"
	os.makedirs(os.path.dirname(step_idx_description_annotation_csv_path), exist_ok=True)
	with open(step_idx_description_annotation_csv_path, "w") as f:
		for step_idx, step_description in sorted(step_idx_description_global_map.items(), key=lambda x: int(x[0])):
			f.write(f"{step_idx},{step_description}\n")


def fetch_average_segments_by_recipe():
	average_segment_length = {}
	total_segments = {}
	for recording_annotation in recording_annotations:
		for step_annotation in recording_annotation.step_annotations:
			if step_annotation.start_time is None or step_annotation.start_time == -1:
				continue
			if recording_annotation.activity_id in average_segment_length:
				average_segment_length[
					recording_annotation.activity_id] += step_annotation.end_time - step_annotation.start_time
				total_segments[recording_annotation.activity_id] += 1
			else:
				average_segment_length[
					recording_annotation.activity_id] = step_annotation.end_time - step_annotation.start_time
				total_segments[recording_annotation.activity_id] = 1
	
	average_segment_csv_path = "annotation_csvs/average_segment_length.csv"
	os.makedirs(os.path.dirname(average_segment_csv_path), exist_ok=True)
	with open(average_segment_csv_path, "w") as f:
		sum_average_segment_length = 0
		num_segments = 0
		for activity_id, total_segment in sorted(total_segments.items(), key=lambda x: int(x[0])):
			average_segment_length[activity_id] /= total_segment
			f.write(
				f"{activity_id},{activity_id_to_activity_name_map[activity_id]},{average_segment_length[activity_id]}\n")
			sum_average_segment_length += average_segment_length[activity_id]
			num_segments += total_segment
		f.write("\n=============================================================================\n")
		f.write(f"Average,{sum_average_segment_length / len(total_segments)},{num_segments}")
		f.write("\n=============================================================================")


def generate_error_category_map():
	error_idx_category_map = {}
	error_category_idx_map = {}
	error_category_idx = 0
	for error_tag in ErrorTag.mistake_tag_list:
		error_category_idx_map[error_tag] = error_category_idx
		error_idx_category_map[error_category_idx] = error_tag
		error_category_idx += 1
	error_category_idx_csv_path = "annotation_csvs/error_category_idx.csv"
	os.makedirs(os.path.dirname(error_category_idx_csv_path), exist_ok=True)
	with open(error_category_idx_csv_path, "w") as f:
		for error_idx, error_category in error_idx_category_map.items():
			f.write(f"{error_idx},{error_category}\n")
	return error_idx_category_map, error_category_idx_map


def generate_error_annotations_csv():
	error_idx_category_map, error_category_idx_map = generate_error_category_map()
	error_annotation_csv_path = "annotation_csvs/error_annotations.csv"
	os.makedirs(os.path.dirname(error_annotation_csv_path), exist_ok=True)
	with open(error_annotation_csv_path, "w") as f:
		for recording_annotation in recording_annotations:
			recording_id = recording_annotation.recording_id
			for step_annotation in recording_annotation.step_annotations:
				step_id = step_annotation.step_id
				step_description = step_annotation.description
				step_start_time = None if step_annotation.start_time == -1 else step_annotation.start_time
				step_end_time = None if step_annotation.end_time == -1 else step_annotation.end_time
				has_errors = len(step_annotation.errors) > 0
				step_annotation_str = f"{recording_id},{step_id},{step_start_time},{step_end_time},{step_description},{has_errors},"
				for error in step_annotation.errors:
					error_category_idx = error_category_idx_map[error.tag]
					error_annotation_str = f"{error_category_idx},{error.description}"
					step_annotation_str += error_annotation_str
				f.write(step_annotation_str)
				f.write("\n")


if __name__ == '__main__':
	db_service = FirebaseService()
	
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(recording_annotations, key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1])))
	
	activities_dict = db_service.fetch_activities()
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	
	generate_step_annotation_csv()
	fetch_average_segments_by_recipe()
	generate_error_annotations_csv()
