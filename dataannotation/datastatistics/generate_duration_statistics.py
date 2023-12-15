import json
import os
import sys
import os.path as osp
import matplotlib.pyplot as plt
import numpy as np
from moviepy.video.io.VideoFileClip import VideoFileClip
from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


initialize_paths()


def check_is_error_recording(recording_annotation):
	is_error_boolean = recording_annotation.is_error
	
	is_error = False
	for step_annotation in recording_annotation.step_annotations:
		if len(step_annotation.errors) > 0:
			is_error = True
			break
	
	error_text = f"Error in recording {recording_annotation.recording_id} - {is_error}, {is_error_boolean}"
	assert is_error == is_error_boolean, f"Error in recording {error_text}"
	return is_error


def fetch_recipe_error_normal_division_statistics():
	recipe_error_normal_division_statistics = {}
	total_normal_recordings = 0
	total_error_recordings = 0
	total_normal_duration = 0.
	total_error_duration = 0.
	
	for recording_annotation in recording_annotations:
		recording_id = recording_annotation.recording_id
		activity_id = recording_annotation.activity_id
		activity_name = activity_id_to_activity_name_map[activity_id]
		video_file_name = f"{recording_id}_360p.mp4"
		
		if not os.path.exists(os.path.join(video_files_directory, video_file_name)):
			print(f"Recording {recording_id} does not have a video. Error...")
			print(f"-----------------------------------------------------")
			continue
		else:
			video_clip = VideoFileClip(os.path.join(video_files_directory, video_file_name))
			recording_video_duration = round(video_clip.duration / 3600, 2)
			video_clip.close()
			
			if activity_name not in recipe_error_normal_division_statistics:
				recipe_error_normal_division_statistics[activity_name] = {}
			
			is_error_recording = check_is_error_recording(recording_annotation)
			if not is_error_recording:
				total_normal_recordings += 1
				total_normal_duration += recording_video_duration
				if "normal" not in recipe_error_normal_division_statistics[activity_name]:
					recipe_error_normal_division_statistics[activity_name]["normal"] = 0
					recipe_error_normal_division_statistics[activity_name]["normal_duration"] = 0
				recipe_error_normal_division_statistics[activity_name]["normal"] += 1
				recipe_error_normal_division_statistics[activity_name]["normal_duration"] += recording_video_duration
			else:
				total_error_recordings += 1
				total_error_duration += recording_video_duration
				if "error" not in recipe_error_normal_division_statistics[activity_name]:
					recipe_error_normal_division_statistics[activity_name]["error"] = 0
					recipe_error_normal_division_statistics[activity_name]["error_duration"] = 0
				recipe_error_normal_division_statistics[activity_name]["error"] += 1
				recipe_error_normal_division_statistics[activity_name]["error_duration"] += recording_video_duration
	
	recipe_error_normal_division_statistics["total_normal_recordings"] = total_normal_recordings
	recipe_error_normal_division_statistics["total_error_recordings"] = total_error_recordings
	recipe_error_normal_division_statistics["total_normal_duration"] = total_normal_duration
	recipe_error_normal_division_statistics["total_error_duration"] = total_error_duration
	recipe_error_normal_division_statistics["total_duration"] = total_normal_duration + total_error_duration
	recipe_error_normal_division_statistics["total_recordings"] = total_normal_recordings + total_error_recordings
	
	with (open(f"{processed_files_directory}/v{version}/recipe_error_normal_division_statistics.json", 'w')
	      as recipe_error_normal_division_statistics_file):
		json_data = json.dumps(recipe_error_normal_division_statistics, indent=4)
		recipe_error_normal_division_statistics_file.write(json_data)
	
	print(f"Total normal recordings: {total_normal_recordings}")
	print(f"Total error recordings: {total_error_recordings}")
	print(f"Total normal duration: {total_normal_duration}")
	print(f"Total error duration: {total_error_duration}")
	print(f"Total duration: {total_normal_duration + total_error_duration}")


def generate_statistics_chart():
	# Assuming the data structure is as follows:
	# Each tuple contains: (Category Name, Normal Recordings Count, Error Recordings Count, Normal Recordings Duration, Error Recordings Duration)
	activity_division_statistics = json.load(
		open(f"{processed_files_directory}/v{version}/recipe_error_normal_division_statistics.json", 'r')
	)
	
	activity_names = []
	normal_counts = []
	error_counts = []
	normal_durations = []
	error_durations = []
	for activity_name, activity_statistics in activity_division_statistics.items():
		if type(activity_statistics) is not dict:
			continue
		
		activity_names.append(activity_name)
		normal_counts.append(activity_statistics["normal"])
		error_counts.append(activity_statistics["error"])
		normal_durations.append(activity_statistics["normal_duration"])
		error_durations.append(activity_statistics["error_duration"])

	# Setting the positions and width for the bars
	pos = np.arange(len(activity_names))
	bar_width = 0.35
	
	# Let's use a larger figure size to prevent cutting off text.
	plt.figure(figsize=(15, 8))
	
	# Using a more contrasting color scheme
	colors_normal = 'turquoise'
	colors_error = 'teal'
	colors_normal_duration = 'lightcoral'
	colors_error_duration = 'darkred'
	
	# Plotting with the new colors
	fig, ax1 = plt.subplots(figsize=(15, 8))  # Making the figure larger
	
	# Bars for recordings count with new colors
	bar1 = ax1.bar(pos, normal_counts, bar_width, label='Normal Recordings', color=colors_normal)
	bar2 = ax1.bar(pos, error_counts, bar_width, bottom=normal_counts, label='Error Recordings', color=colors_error)
	
	# Set the y axis label
	ax1.set_ylabel('Recordings Count', color='teal')
	ax1.tick_params(axis='y', labelcolor='teal')
	
	# Creating a twin axis for durations
	ax2 = ax1.twinx()
	
	# Bars for recordings duration with new colors
	bar3 = ax2.bar(pos+bar_width, normal_durations, bar_width, label='Normal Recordings Duration(Hr)', alpha=0.5,
	        color=colors_normal_duration)
	bar4 = ax2.bar(pos + bar_width , error_durations, bar_width,bottom=normal_durations, label='Error Recordings Duration(Hr)', alpha=0.5,
	        color=colors_error_duration)
	
	# Set the y axis label
	ax2.set_ylabel('Recordings Duration(Hr)', color='darkred')
	ax2.tick_params(axis='y', labelcolor='darkred')
	
	# Setting the x axis with category names and rotating them to fit
	ax1.set_xticks(pos)
	ax1.set_xticklabels(activity_names, rotation=45, ha='right')
	
	# Adding a legend
	fig.legend(loc='center', bbox_to_anchor=(0.5, 1.1), ncol=4)
	ax1.legend(handles=[bar1, bar2], loc='upper left')
	ax2.legend(handles=[bar3, bar4], loc='upper right')
	
	# Resizable figure
	fig.tight_layout()
	
	# Show the plot
	versioned_files_directory = f"{processed_files_directory}/v{version}/assets"
	os.makedirs(versioned_files_directory, exist_ok=True)
	plt.savefig(f'{versioned_files_directory}/division_statistics.jpeg')
	plt.show()


if __name__ == '__main__':
	version = 5
	
	db_service = FirebaseService()
	processed_files_directory = "./processed_files"
	video_files_directory = "D:\\DATA\\COLLECTED\\PTG\\COMPLETE\\error_dataset\\data_2d\\resolution_360p"
	
	activities_dict = db_service.fetch_activities()
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	activity_name_to_activity_id_map = {activity.name: activity.id for activity in activities}
	activity_id_to_activity_map = {activity.id: activity for activity in activities}
	
	recording_annotation_list_dict = dict(db_service.fetch_recording_annotations())
	recording_annotations = [
		RecordingAnnotation.from_dict(recording_annotation_dict) for recording_id, recording_annotation_dict in
		recording_annotation_list_dict.items() if recording_annotation_dict is not None
	]
	recording_annotations = sorted(
		recording_annotations,
		key=lambda x: (int(x.activity_id), int(x.recording_id.split("_")[1]))
	)
	
	# fetch_recipe_error_normal_division_statistics()
	generate_statistics_chart()
