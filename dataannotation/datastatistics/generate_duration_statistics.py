import json
import json
import os
import sys
import os.path as osp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from moviepy.video.io.VideoFileClip import VideoFileClip

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.error_tag import ErrorTag
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


initialize_paths()


def fetch_recipe_error_normal_division_statistics():
	user_recordings = dict(db_service.fetch_all_selected_recordings())
	recipe_error_normal_division_statistics = {}
	total_normal_recordings = 0
	total_error_recordings = 0
	total_normal_duration = 0.
	total_error_duration = 0.
	for recording_id, user_recording_dict in user_recordings.items():
		recording = Recording.from_dict(user_recording_dict)
		if recording.activity_id not in activity_id_to_activity_name_map:
			print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
			print(f"-----------------------------------------------------")
			continue
		
		if os.path.exists(os.path.join(video_files_directory, recording.id + "_360p.mp4")):
			video_clip = VideoFileClip(os.path.join(video_files_directory, recording.id + "_360p.mp4"))
			recording_video_duration = round(video_clip.duration / 3600, 2)
			video_clip.close()
		elif os.path.exists(os.path.join(video_files_directory, recording.id + "_360p.MP4")):
			print(f"Recording {recording.id} has a capital MP4 extension.")
		else:
			print(f"Recording {recording.id} does not have a video. Skipping...")
			print(f"-----------------------------------------------------")
			continue
		
		if not activity_id_to_activity_name_map[
			       recording.activity_id] in recipe_error_normal_division_statistics:
			recipe_error_normal_division_statistics[
				activity_id_to_activity_name_map[recording.activity_id]] = {}
		
		if not recording.is_error:
			total_normal_recordings += 1
			total_normal_duration += recording_video_duration
			if not "normal" in recipe_error_normal_division_statistics[
				activity_id_to_activity_name_map[recording.activity_id]]:
				recipe_error_normal_division_statistics[
					activity_id_to_activity_name_map[recording.activity_id]]["normal"] = 0
				recipe_error_normal_division_statistics[
					activity_id_to_activity_name_map[recording.activity_id]]["normal_duration"] = 0
			recipe_error_normal_division_statistics[activity_id_to_activity_name_map[recording.activity_id]][
				"normal"] += 1
			recipe_error_normal_division_statistics[
				activity_id_to_activity_name_map[recording.activity_id]][
				"normal_duration"] += recording_video_duration
		else:
			total_error_recordings += 1
			total_error_duration += recording_video_duration
			if not "error" in recipe_error_normal_division_statistics[
				activity_id_to_activity_name_map[recording.activity_id]]:
				recipe_error_normal_division_statistics[
					activity_id_to_activity_name_map[recording.activity_id]]["error"] = 0
				recipe_error_normal_division_statistics[
					activity_id_to_activity_name_map[recording.activity_id]]["error_duration"] = 0
			recipe_error_normal_division_statistics[activity_id_to_activity_name_map[recording.activity_id]][
				"error"] += 1
			recipe_error_normal_division_statistics[activity_id_to_activity_name_map[recording.activity_id]][
				"error_duration"] += recording_video_duration
	
	recipe_error_normal_division_statistics["total_normal_recordings"] = total_normal_recordings
	recipe_error_normal_division_statistics["total_error_recordings"] = total_error_recordings
	recipe_error_normal_division_statistics["total_normal_duration"] = total_normal_duration
	recipe_error_normal_division_statistics["total_error_duration"] = total_error_duration
	recipe_error_normal_division_statistics["total_duration"] = total_normal_duration + total_error_duration
	recipe_error_normal_division_statistics["total_recordings"] = total_normal_recordings + total_error_recordings
	
	with open(f"{processed_files_directory}/v{version}/recipe_error_normal_division_statistics.json",
	          'w') as recipe_error_normal_division_statistics_file:
		json_data = json.dumps(recipe_error_normal_division_statistics, indent=4)
		recipe_error_normal_division_statistics_file.write(json_data)
	
	print(f"Total normal recordings: {total_normal_recordings}")
	print(f"Total error recordings: {total_error_recordings}")
	print(f"Total normal duration: {total_normal_duration}")
	print(f"Total error duration: {total_error_duration}")
	print(f"Total duration: {total_normal_duration + total_error_duration}")


if __name__ == '__main__':
	version = 2
	
	db_service = FirebaseService()
	processed_files_directory = "./processed_files"
	video_files_directory = "D:\\DATA\\COLLECTED\\PTG\\COMPLETE\\error_dataset\\data_2d\\resolution_360p"
	
	activities_dict = db_service.fetch_activities()
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	activity_name_to_activity_id_map = {activity.name: activity.id for activity in activities}
	activity_id_to_activity_map = {activity.id: activity for activity in activities}
	
	fetch_recipe_error_normal_division_statistics()
