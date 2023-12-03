import json
import os
import os.path as osp
import shutil


def prepare_video_directory(recording_map, recording_type, split_type, base_path='/data/rohith/'):
	os.makedirs(base_path, exist_ok=True)
	base_videos_path = osp.join(base_path, split_type, recording_type)
	os.makedirs(base_videos_path, exist_ok=True)
	train_videos_path = osp.join(base_videos_path, 'train')
	os.makedirs(train_videos_path, exist_ok=True)
	val_videos_path = osp.join(base_videos_path, 'val')
	os.makedirs(val_videos_path, exist_ok=True)
	test_videos_path = osp.join(base_videos_path, 'test')
	os.makedirs(test_videos_path, exist_ok=True)
	for activity, recording_list in recording_map.items():
		print(f"Copying {activity} videos to {recording_type} directory")
		train_set, val_set, test_set = recording_list[0][0], recording_list[0][1], recording_list[0][2]
		for recording_set, recording_set_path in zip([train_set, val_set, test_set],
		                                             [train_videos_path, val_videos_path, test_videos_path]):
			os.makedirs(osp.join(recording_set_path, f"{activity}"), exist_ok=True)
			for train_recording_num in recording_set:
				recording_id = f'{activity}_{train_recording_num}'
				train_recording_path = osp.join(recording_set_path, f"{activity}", f"{recording_id}.mp4")
				raw_recording_path = osp.join(raw_videos_path, f"{recording_id}_360p.mp4")
				shutil.copy(raw_recording_path, train_recording_path)


def prepare_data_splits_for_splits(split_type, activity_id, recording_num_list):
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
	
	return train_set, val_set, test_set


def prepare_recording_maps_for_splits(split_type) -> (dict, dict):
	normal_recording_map = dict()
	normal_error_combined_recording_map = dict()
	for activity_id in activity_idx_list:
		if activity_id not in normal_recording_map:
			normal_recording_map[activity_id] = []
		if activity_id not in normal_error_combined_recording_map:
			normal_error_combined_recording_map[activity_id] = []
	
	for activity_id in activity_idx_list:
		recording_num_list = activity_recording_map[activity_id]
		recording_num_list = [int(recording_num) for recording_num in recording_num_list]
		recording_num_list = sorted(recording_num_list)
		
		normal_recording_num_list = []
		error_recording_num_list = []
		for recording_num in recording_num_list:
			if recording_num <= 25 or (100 <= recording_num <= 125):
				normal_recording_num_list.append(recording_num)
			else:
				error_recording_num_list.append(recording_num)
		
		normal_train_set, normal_val_set, normal_test_set = prepare_data_splits_for_splits(split_type, activity_id,
		                                                                                   normal_recording_num_list)
		error_train_set, error_val_set, error_test_set = prepare_data_splits_for_splits(split_type, activity_id,
		                                                                                error_recording_num_list)
		
		normal_recording_map[activity_id].append([normal_train_set, normal_val_set, normal_test_set])
		
		normal_error_train_set = normal_train_set | error_train_set
		normal_error_val_set = normal_val_set | error_val_set
		normal_error_test_set = normal_test_set | error_test_set
		
		normal_error_combined_recording_map[activity_id].append(
			[normal_error_train_set, normal_error_val_set, normal_error_test_set])
	
	return normal_recording_map, normal_error_combined_recording_map


def fetch_lists():
	activity_idx_list = sorted(list(activity_idx_step_idx_map.keys()))
	activity_recording_map = dict()
	for activity_id in activity_idx_list:
		if activity_id not in activity_recording_map:
			activity_recording_map[activity_id] = []
	recording_id_list = sorted(list(step_annotations.keys()))
	for recording_id in recording_id_list:
		activity_id, recording_num = recording_id.split('_')
		activity_recording_map[activity_id].append(recording_num)
	return activity_idx_list, activity_recording_map


if __name__ == '__main__':
	activity_idx_step_idx_path = osp.join('../data/ERROR/activity_idx_step_idx.json')
	step_annotations_json_path = osp.join('../data/ERROR/step_annotations.json')
	step_idx_description_path = osp.join('../data/ERROR/step_idx_description.json')
	complete_step_annotations_json_path = osp.join('../data/ERROR/complete_step_annotations.json')
	
	activity_idx_step_idx_map = json.load(open(activity_idx_step_idx_path, 'r'))
	step_annotations = json.load(open(step_annotations_json_path, 'r'))
	complete_step_annotations = json.load(open(complete_step_annotations_json_path, 'r'))
	step_idx_description = json.load(open(step_idx_description_path, 'r'))
	
	raw_videos_path = osp.join('/home/rxp190007/DATA/error_dataset/data_2d/resolution_360p')
	
	activity_idx_list, activity_recording_map = fetch_lists()
	
	split_type_list = ["recordings", "person", "environment", "recipes"]
	
	for split_type in split_type_list:
		norm_recording_map, norm_error_combined_recording_map = prepare_recording_maps_for_splits(split_type)
		prepare_video_directory(norm_recording_map, "normal", split_type, raw_videos_path)
		prepare_video_directory(norm_error_combined_recording_map, "normal_error", split_type, raw_videos_path)
