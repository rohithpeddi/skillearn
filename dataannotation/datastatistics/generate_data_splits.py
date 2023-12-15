import json
import os
import os.path as osp
import shutil

from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


# def prepare_video_directory(recording_map, recording_type, split_type, base_path='/data/rohith/'):
# 	os.makedirs(base_path, exist_ok=True)
# 	base_videos_path = osp.join(base_path, split_type, recording_type)
# 	os.makedirs(base_videos_path, exist_ok=True)
# 	train_videos_path = osp.join(base_videos_path, 'train')
# 	os.makedirs(train_videos_path, exist_ok=True)
# 	val_videos_path = osp.join(base_videos_path, 'val')
# 	os.makedirs(val_videos_path, exist_ok=True)
# 	test_videos_path = osp.join(base_videos_path, 'test')
# 	os.makedirs(test_videos_path, exist_ok=True)
# 	for activity, recording_list in recording_map.items():
# 		print(f"Copying {activity} videos to {recording_type} directory")
# 		train_set, val_set, test_set = recording_list[0][0], recording_list[0][1], recording_list[0][2]
# 		for recording_set, recording_set_path in zip([train_set, val_set, test_set],
# 		                                             [train_videos_path, val_videos_path, test_videos_path]):
# 			os.makedirs(osp.join(recording_set_path, f"{activity}"), exist_ok=True)
# 			for train_recording_num in recording_set:
# 				recording_id = f'{activity}_{train_recording_num}'
# 				train_recording_path = osp.join(recording_set_path, f"{activity}", f"{recording_id}.mp4")
# 				raw_recording_path = osp.join(raw_videos_path, f"{recording_id}_360p.mp4")
# 				shutil.copy(raw_recording_path, train_recording_path)


def prepare_data_splits_for_splits(
		split_type,
		activity_id,
		recording_num_list,
		complete_step_annotations
):
	total_recordings = len(recording_num_list)
	train_recordings = int(0.6 * total_recordings)
	val_recordings = int(0.2 * total_recordings)
	test_recordings = int(0.2 * total_recordings)
	
	train_set, val_set, test_set = set(), set(), set()
	if split_type == "recordings":
		train_set = set(recording_num_list[:train_recordings])
		val_set = set(recording_num_list[train_recordings:train_recordings + val_recordings])
		test_set = set(recording_num_list[train_recordings + val_recordings:])
	elif split_type == "person":
		test_person_list = [1, 2]
		train_person_list = [3, 4, 5, 6]
		val_person_list = [7, 8]
		for recording_num in recording_num_list:
			recording_id = f'{activity_id}_{recording_num}'
			person_id = int(complete_step_annotations[recording_id]['person_id'])
			if person_id in train_person_list:
				train_set.add(recording_num)
			elif person_id in val_person_list:
				val_set.add(recording_num)
			elif person_id in test_person_list:
				test_set.add(recording_num)
	elif split_type == "environment":
		train_environment_list = [1, 2, 5]
		val_environment_list = [6, 7]
		test_environment_list = [3, 8, 9, 10, 11]
		for recording_num in recording_num_list:
			recording_id = f'{activity_id}_{recording_num}'
			environment = int(complete_step_annotations[recording_id]['environment'])
			if environment in train_environment_list:
				train_set.add(recording_num)
			elif environment in val_environment_list:
				val_set.add(recording_num)
			elif environment in test_environment_list:
				test_set.add(recording_num)
	elif split_type == "recipes":
		train_recipe_list = [1, 4, 7, 5, 13, 15, 18, 20, 22, 23, 27]
		val_recipe_list = [2, 9, 12, 17, 26, 29]
		test_recipe_list = [3, 8, 10, 16, 21, 25, 28]
		
		if activity_id in train_recipe_list:
			train_set = set(recording_num_list)
		elif activity_id in val_recipe_list:
			val_set = set(recording_num_list)
		elif activity_id in test_recipe_list:
			test_set = set(recording_num_list)
	
	train_list = []
	val_list = []
	test_list = []
	
	for recording_num in train_set:
		train_list.append(f"{activity_id}_{recording_num}")
	for recording_num in val_set:
		val_list.append(f"{activity_id}_{recording_num}")
	for recording_num in test_set:
		test_list.append(f"{activity_id}_{recording_num}")
	
	return train_list, val_list, test_list


def prepare_recording_maps_for_splits(
		split_type,
		activity_idx_list,
		activity_recording_map,
		recording_id_recording_annotations_map,
		complete_step_annotations
) -> (dict, dict):
	normal_recording_map = {
		"train": [],
		"val": [],
		"test": []
	}
	combined_recording_map = {
		"train": [],
		"val": [],
		"test": []
	}
	for activity_id in activity_idx_list:
		recording_num_list = activity_recording_map[activity_id]
		recording_num_list = [int(recording_num) for recording_num in recording_num_list]
		recording_num_list = sorted(recording_num_list)
		normal_recording_num_list = []
		error_recording_num_list = []
		for recording_num in recording_num_list:
			recording_id = f'{activity_id}_{recording_num}'
			recording_annotation = recording_id_recording_annotations_map[recording_id]
			if recording_annotation.is_error:
				error_recording_num_list.append(recording_num)
			else:
				normal_recording_num_list.append(recording_num)
		
		normal_train_list, normal_val_list, normal_test_list = prepare_data_splits_for_splits(
			split_type,
			activity_id,
			normal_recording_num_list,
			complete_step_annotations
		)
		
		error_train_list, error_val_list, error_test_list = prepare_data_splits_for_splits(
			split_type,
			activity_id,
			error_recording_num_list,
			complete_step_annotations
		)
		
		normal_recording_map["train"] += normal_train_list
		normal_recording_map["val"] += normal_val_list
		normal_recording_map["test"] += normal_test_list
		
		normal_error_train_list = normal_train_list + error_train_list
		normal_error_val_list = normal_val_list + error_val_list
		normal_error_test_list = normal_test_list + error_test_list
		
		combined_recording_map["train"] += normal_error_train_list
		combined_recording_map["val"] += normal_error_val_list
		combined_recording_map["test"] += normal_error_test_list
	
	return normal_recording_map, combined_recording_map


def main():
	version = 5
	db_service = FirebaseService()
	raw_videos_path = osp.join(osp.curdir, '/home/rxp190007/DATA/error_dataset/data_2d/resolution_360p')
	
	activity_idx_step_idx_map = json.load(open(f"annotation_jsons/v{version}/activity_idx_step_idx.json", 'r'))
	step_annotations = json.load(open(f"annotation_jsons/v{version}/step_annotations.json", 'r'))
	complete_step_annotations = json.load(open(f"annotation_jsons/v{version}/complete_step_annotations.json", 'r'))
	step_idx_description = json.load(open(f"annotation_jsons/v{version}/step_idx_description.json", 'r'))
	
	activity_idx_list = sorted(list(activity_idx_step_idx_map.keys()))
	activity_recording_map = dict()
	for activity_id in activity_idx_list:
		if activity_id not in activity_recording_map:
			activity_recording_map[activity_id] = []
	recording_id_list = sorted(list(step_annotations.keys()))
	for recording_id in recording_id_list:
		activity_id, recording_num = recording_id.split('_')
		activity_recording_map[activity_id].append(recording_num)
	
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(
		recording_annotations,
		key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1]))
	)
	
	recording_id_recording_annotations_map = {}
	for recording_annotation in recording_annotations:
		recording_id_recording_annotations_map[recording_annotation.recording_id] = recording_annotation
	
	split_type_list = ["recordings", "person", "environment", "recipes"]
	for split_type in split_type_list:
		norm_recording_map, norm_error_combined_recording_map = prepare_recording_maps_for_splits(
			split_type,
			activity_idx_list,
			activity_recording_map,
			recording_id_recording_annotations_map,
			complete_step_annotations
		)
		versioned_output_directory = f"data_split_jsons/v{version}"
		os.makedirs(versioned_output_directory, exist_ok=True)
		with open(f"{versioned_output_directory}/{split_type}_data_split_normal.json", 'w') as f:
			json.dump(norm_recording_map, f)
		with open(f"{versioned_output_directory}/{split_type}_data_split_combined.json", 'w') as f:
			json.dump(norm_error_combined_recording_map, f)


if __name__ == '__main__':
	main()
