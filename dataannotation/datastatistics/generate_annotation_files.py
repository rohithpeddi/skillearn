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


def generate_error_category_maps():
	error_idx_category_map = {}
	error_category_idx_map = {}
	error_category_idx = 0
	for error_tag in ErrorTag.mistake_tag_list:
		error_category_idx_map[error_tag] = error_category_idx
		error_idx_category_map[error_category_idx] = error_tag
		error_category_idx += 1
	return error_idx_category_map, error_category_idx_map


####################################################################################################################
# ---------------------------------------------- CSV FILES --------------------------------------------------------#
####################################################################################################################
def generate_activity_step_idx_csv():
	activity_idx_step_idx_annotation_csv_path = f"annotation_csvs/v{version}/activity_idx_step_idx.csv"
	os.makedirs(os.path.dirname(activity_idx_step_idx_annotation_csv_path), exist_ok=True)
	with open(activity_idx_step_idx_annotation_csv_path, "w", newline='') as activity_idx_step_idx_annotation_csv_file:
		writer = csv.writer(activity_idx_step_idx_annotation_csv_file, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow(["activity_idx", "activity_name", "step_indices"])
		for activity_idx, step_idx_list in sorted(activity_idx_step_idx_global_map.items(), key=lambda x: int(x[0])):
			writer.writerow(
				[
					f"{activity_idx}", f"{activity_id_to_activity_name_map[activity_idx]}",
					f"{','.join([str(step_idx) for step_idx in step_idx_list])}"
				]
			)


def generate_step_idx_description_csv():
	step_idx_description_annotation_csv_path = f"annotation_csvs/v{version}/step_idx_description.csv"
	os.makedirs(os.path.dirname(step_idx_description_annotation_csv_path), exist_ok=True)
	with open(step_idx_description_annotation_csv_path, "w", newline='') as step_idx_description_annotation_csv_file:
		writer = csv.writer(step_idx_description_annotation_csv_file, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow(["step_idx", "step_description"])
		for step_idx, step_description in sorted(step_idx_description_global_map.items(), key=lambda x: int(x[0])):
			writer.writerow([f"{step_idx}", f"{step_description}"])


def generate_step_annotation_csv():
	annotation_csv_path = f"annotation_csvs/v{version}/step_annotations.csv"
	os.makedirs(os.path.dirname(annotation_csv_path), exist_ok=True)
	with open(annotation_csv_path, "w", newline='') as step_annotation_csv_file:
		writer = csv.writer(step_annotation_csv_file, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow([
			"recording_id", "step_id", "start_time", "end_time", "description", "has_errors"
		])
		for recording_annotation in recording_annotations:
			recording_id = recording_annotation.recording_id
			for step_annotation in recording_annotation.step_annotations:
				step_id = step_annotation.step_id
				
				step_description = step_annotation.description
				step_start_time = step_annotation.start_time
				step_end_time = step_annotation.end_time
				has_errors = len(step_annotation.errors) > 0
				step_annotation_str = [
					f"{recording_id}", f"{step_id}", f"{step_start_time}", f"{step_end_time}",
					f"{step_description}", f"{has_errors}"
				]
				writer.writerow(step_annotation_str)


def generate_error_category_csv():
	error_idx_category_map, error_category_idx_map = generate_error_category_maps()
	error_category_idx_csv_path = f"annotation_csvs/v{version}/error_category_idx.csv"
	os.makedirs(os.path.dirname(error_category_idx_csv_path), exist_ok=True)
	with open(error_category_idx_csv_path, "w", newline='') as error_category_idx_csv_file:
		writer = csv.writer(error_category_idx_csv_file, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow(["error_category_idx", "error_category"])
		for error_idx, error_category in error_idx_category_map.items():
			writer.writerow([f"{error_idx}", f"{error_category}"])
	return error_idx_category_map, error_category_idx_map


def generate_activity_step_description_csv():
	activity_step_description_csv_path = f"annotation_csvs/v{version}/activity_step_description.csv"
	os.makedirs(os.path.dirname(activity_step_description_csv_path), exist_ok=True)
	
	with open(activity_step_description_csv_path, "w", newline='') as activity_step_description_csv_file:
		writer = csv.writer(activity_step_description_csv_file, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow(["activity_idx", "activity_name", "step_index", "step_description"])
		for activity_idx, step_idx_list in sorted(activity_idx_step_idx_global_map.items(), key=lambda x: int(x[0])):
			for step_idx in step_idx_list:
				writer.writerow(
					[
						f"{activity_idx}", f"{activity_id_to_activity_name_map[activity_idx]}",
						f"{step_idx}", f"{step_idx_description_global_map[step_idx]}"
					]
				)


def generate_error_annotations_csv():
	error_annotation_csv_path = f"annotation_csvs/v{version}/error_annotations.csv"
	os.makedirs(os.path.dirname(error_annotation_csv_path), exist_ok=True)
	with open(error_annotation_csv_path, "w", newline='') as error_annotation_csv_file:
		writer = csv.writer(error_annotation_csv_file, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow([
			"recording_id", "step_id", "start_time", "end_time", "description", "has_errors",
			ErrorTag.PREPARATION_ERROR, "error_description",
			ErrorTag.MEASUREMENT_ERROR, "error_description",
			ErrorTag.ORDER_ERROR, "error_description",
			ErrorTag.TIMING_ERROR, "error_description",
			ErrorTag.TECHNIQUE_ERROR, "error_description",
			ErrorTag.TEMPERATURE_ERROR, "error_description",
			ErrorTag.MISSING_STEP, "error_description",
			ErrorTag.OTHER, "error_description"
		])
		for recording_annotation in recording_annotations:
			recording_id = recording_annotation.recording_id
			for step_annotation in recording_annotation.step_annotations:
				step_id = step_annotation.step_id
				step_description = step_annotation.description
				step_start_time = None if step_annotation.start_time == -1 else step_annotation.start_time
				step_end_time = None if step_annotation.end_time == -1 else step_annotation.end_time
				has_errors = len(step_annotation.errors) > 0
				error_annotation_row = [
					f"{recording_id}", f"{step_id}", f"{step_start_time}", f"{step_end_time}",
					f"{step_description}", f"{has_errors}"
				]
				error_category_description_map = {}
				for error in step_annotation.errors:
					if error.tag not in error_category_description_map:
						error_category_description_map[error.tag] = [error.description]
					else:
						error_category_description_map[error.tag].append(error.description)
				error_description_row = []
				for error_category in ErrorTag.mistake_tag_list:
					if error_category in error_category_description_map:
						error_description_row += ["1", f"{error.description}"]
					else:
						error_description_row += ["0", "None"]
				error_annotation_row += error_description_row
				writer.writerow(error_annotation_row)


def generate_recording_id_step_idx_csv():
	recording_id_step_idx_csv_path = f"annotation_csvs/v{version}/recording_id_step_idx.csv"
	os.makedirs(os.path.dirname(recording_id_step_idx_csv_path), exist_ok=True)
	try:
		with open(recording_id_step_idx_csv_path, "w", newline='') as recording_id_step_idx_csv_file:
			writer = csv.writer(recording_id_step_idx_csv_file, quoting=csv.QUOTE_NONNUMERIC)
			writer.writerow(["recording_id", "activity_id", "step_indices"])
			for recording_id, step_idx_list in sorted(recording_id_step_idx_map.items(), key=lambda x: int(x[0])):
				activity_id = recording_id.split("_")[0]
				step_indices = ','.join([str(step_idx) for step_idx in step_idx_list])
				writer.writerow(
					[
						f"{recording_id}", f"{activity_id}", f"{step_indices}"
					]
				)
	except Exception as e:
		print(e)


####################################################################################################################
# ---------------------------------------------- JSON FILES --------------------------------------------------------#
####################################################################################################################

def generate_activity_step_idx_json():
	activity_idx_step_idx_annotation_json_path = f"annotation_jsons/v{version}/activity_idx_step_idx.json"
	os.makedirs(os.path.dirname(activity_idx_step_idx_annotation_json_path), exist_ok=True)
	with open(activity_idx_step_idx_annotation_json_path, "w",
	          newline='') as activity_idx_step_idx_annotation_json_file:
		json.dump(activity_idx_step_idx_global_map, activity_idx_step_idx_annotation_json_file, indent=4)


def generate_step_idx_description_json():
	step_idx_description_annotation_json_path = f"annotation_jsons/v{version}/step_idx_description.json"
	os.makedirs(os.path.dirname(step_idx_description_annotation_json_path), exist_ok=True)
	with open(step_idx_description_annotation_json_path, "w", newline='') as step_idx_description_annotation_json_file:
		json.dump(step_idx_description_global_map, step_idx_description_annotation_json_file, indent=4)


def generate_step_annotation_json():
	step_annotation_json_path = f"annotation_jsons/v{version}/step_annotations.json"
	os.makedirs(os.path.dirname(step_annotation_json_path), exist_ok=True)
	
	recording_annotation_dict_map = {}
	for recording_annotation in recording_annotations:
		recording_annotation_dict = {}
		recording_id = recording_annotation.recording_id
		
		recording_annotation_dict["recording_id"] = recording_id
		step_annotation_dict_list = []
		for step_annotation in recording_annotation.step_annotations:
			step_annotation_dict = {}
			step_id = step_annotation.step_id
			
			step_description = step_annotation.description
			step_start_time = step_annotation.start_time
			step_end_time = step_annotation.end_time
			has_errors = len(step_annotation.errors) > 0
			
			step_annotation_dict["step_id"] = step_id
			step_annotation_dict["start_time"] = step_start_time
			step_annotation_dict["end_time"] = step_end_time
			step_annotation_dict["description"] = step_description
			step_annotation_dict["has_errors"] = has_errors
			
			step_annotation_dict_list.append(step_annotation_dict)
		
		recording_annotation_dict["steps"] = step_annotation_dict_list
		recording_annotation_dict_map[recording_id] = recording_annotation_dict
	
	with open(step_annotation_json_path, "w") as step_annotation_json_file:
		json.dump(recording_annotation_dict_map, step_annotation_json_file, indent=4)


def generate_complete_step_annotation_json():
	step_annotation_json_path = f"annotation_jsons/v{version}/complete_step_annotations.json"
	os.makedirs(os.path.dirname(step_annotation_json_path), exist_ok=True)
	
	recording_annotation_dict_map = {}
	for recording_annotation in recording_annotations:
		recording_annotation_dict = {}
		recording_id = recording_annotation.recording_id
		
		recording_annotation_dict["recording_id"] = recording_id
		recording_annotation_dict["activity_id"] = recording_annotation.activity_id
		recording_annotation_dict["activity_name"] = activity_id_to_activity_name_map[recording_annotation.activity_id]
		recording_annotation_dict["person_id"] = recording_id_to_recording_map[recording_id].recorded_by
		recording_annotation_dict["environment"] = recording_id_to_recording_map[recording_id].environment
		step_annotation_dict_list = []
		for step_annotation in recording_annotation.step_annotations:
			step_annotation_dict = {}
			step_id = step_annotation.step_id
			
			step_description = step_annotation.description
			step_start_time = step_annotation.start_time
			step_end_time = step_annotation.end_time
			has_errors = len(step_annotation.errors) > 0
			
			step_annotation_dict["step_id"] = step_id
			step_annotation_dict["start_time"] = step_start_time
			step_annotation_dict["end_time"] = step_end_time
			step_annotation_dict["description"] = step_description
			step_annotation_dict["has_errors"] = has_errors
			
			step_annotation_dict_list.append(step_annotation_dict)
		
		recording_annotation_dict["steps"] = step_annotation_dict_list
		recording_annotation_dict_map[recording_id] = recording_annotation_dict
	
	with open(step_annotation_json_path, "w") as step_annotation_json_file:
		json.dump(recording_annotation_dict_map, step_annotation_json_file, indent=4)


def generate_error_category_json():
	error_idx_category_map, error_category_idx_map = generate_error_category_maps()
	error_category_idx_json_path = f"annotation_jsons/v{version}/error_category_idx.json"
	os.makedirs(os.path.dirname(error_category_idx_json_path), exist_ok=True)
	with open(error_category_idx_json_path, "w", newline='') as error_category_idx_json_file:
		json.dump(error_category_idx_map, error_category_idx_json_file, indent=4)
	return error_idx_category_map, error_category_idx_map


def generate_error_annotations_json():
	error_annotation_json_path = f"annotation_jsons/v{version}/error_annotations.json"
	os.makedirs(os.path.dirname(error_annotation_json_path), exist_ok=True)
	recording_annotation_dict_list = []
	for recording_annotation in recording_annotations:
		recording_annotation_dict = recording_annotation.to_dict()
		recording_annotation_dict_list.append(recording_annotation_dict)
	with open(error_annotation_json_path, "w") as error_annotation_json_file:
		json.dump(recording_annotation_dict_list, error_annotation_json_file, indent=4)


def generate_recording_id_step_idx_json():
	recording_id_step_idx_json_path = f"annotation_jsons/v{version}/recording_id_step_idx.json"
	os.makedirs(os.path.dirname(recording_id_step_idx_json_path), exist_ok=True)
	try:
		with open(recording_id_step_idx_json_path, "w", newline='') as recording_id_step_idx_json_file:
			json.dump(recording_id_step_idx_map, recording_id_step_idx_json_file, indent=4)
	except Exception as e:
		print(e)


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
	
	average_segment_csv_path = f"annotation_csvs/v{version}/average_segment_length.csv"
	os.makedirs(os.path.dirname(average_segment_csv_path), exist_ok=True)
	with open(average_segment_csv_path, "w", newline='') as average_segment_length_csv_file:
		writer = csv.writer(average_segment_length_csv_file, quoting=csv.QUOTE_NONNUMERIC)
		sum_average_segment_length = 0
		num_segments = 0
		writer.writerow(["activity_id", "activity_name", "average_segment_length"])
		for activity_id, total_segment in sorted(total_segments.items(), key=lambda x: int(x[0])):
			average_segment_length[activity_id] /= total_segment
			writer.writerow(
				[
					f"{activity_id}", f"{activity_id_to_activity_name_map[activity_id]}",
					f"{average_segment_length[activity_id]}"
				]
			)
			sum_average_segment_length += average_segment_length[activity_id]
			num_segments += total_segment
		writer.writerow(["\n=============================================================================\n"])
		writer.writerow(["Average", f"{sum_average_segment_length / len(total_segments)}", f"{num_segments}"])
		writer.writerow(["\n=============================================================================\n"])


def generate_all_files():
	print("------------------------------------------------------------------------")
	print(f"Generating annotation csvs for version: {version}")
	generate_activity_step_idx_csv()
	generate_step_idx_description_csv()
	generate_step_annotation_csv()
	generate_error_category_csv()
	generate_activity_step_description_csv()
	generate_error_annotations_csv()
	generate_recording_id_step_idx_csv()
	
	generate_activity_step_idx_json()
	generate_step_idx_description_json()
	generate_step_annotation_json()
	generate_complete_step_annotation_json()
	generate_error_category_json()
	generate_error_annotations_json()
	generate_recording_id_step_idx_json()


if __name__ == '__main__':
	version = 5
	db_service = FirebaseService()
	
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(
		recording_annotations,
		key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1]))
	)
	
	recording_list_dict = dict(db_service.fetch_all_recorded_recordings())
	recordings = [
		Recording.from_dict(recording_dict) for recording_id, recording_dict in recording_list_dict.items() if
		recording_dict is not None
	]
	
	recording_id_to_recording_map = {recording.id: recording for recording in recordings}
	
	activities_dict = db_service.fetch_activities()
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	activity_name_to_activity_id_map = {activity.name.replace(" ", "").lower(): activity.id for activity in activities}
	
	activity_idx_step_idx_global_map = {}
	step_idx_description_global_map = {}
	for recording_annotation in recording_annotations:
		recording_id = recording_annotation.recording_id
		if recording_annotation.activity_id not in activity_idx_step_idx_global_map:
			activity_idx_step_idx_global_map[recording_annotation.activity_id] = []
		for step_annotation in recording_annotation.step_annotations:
			step_id = step_annotation.step_id
			activity_idx_step_idx_global_map[recording_annotation.activity_id].append(step_id)
			step_description = step_annotation.description
			if step_id not in step_idx_description_global_map:
				step_idx_description_global_map[step_id] = step_description
	
	recording_id_step_idx_map = {}
	for recording_annotation in recording_annotations:
		recording_id = recording_annotation.recording_id
		if recording_id not in recording_id_step_idx_map:
			recording_id_step_idx_map[recording_id] = []
		for step_annotation in recording_annotation.step_annotations:
			step_id = step_annotation.step_id
			recording_id_step_idx_map[recording_id].append(step_id)
	
	generate_all_files()
