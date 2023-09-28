import json
import sys
import os.path as osp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.error_tag import ErrorTag
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService


# colors = ["lightgreen", "darkgreen"]  # start and end colors
# n_bins = 100  # Number of bins
# cmap_name = "custom1"
# colormap = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


initialize_paths()


def generate_errors_heatmap():
	# Read and parse the JSON data from a file (Assuming the data is saved in 'data.json')
	with open('processed_files/v2/activity_error_categories.json', 'r') as f:
		data = json.load(f)
	
	# Convert the nested dictionary to a Pandas DataFrame
	df = pd.DataFrame.from_dict(data, orient='index')
	df_transposed = df.T
	
	# Generate the heat map using Seaborn
	plt.figure(figsize=(11, 8))
	
	# Capture the heatmap object
	heatmap = sns.heatmap(df_transposed, annot=True, cmap="Reds", fmt='g', linewidths=0.5)
	plt.title("Error Count by Recipe", fontsize=10)  # Adjusting the title font size as well
	
	# Adjust the font size of annotations
	for text in heatmap.texts:
		text.set_size(10)
	
	ax = plt.gca()
	
	# Decrease font size for x-axis and y-axis labels
	ax.tick_params(axis='x', labelsize=10)  # Adjust the value 10 as needed
	ax.tick_params(axis='y', labelsize=10)  # Adjust the value 10 as needed
	
	for _, spine in ax.spines.items():
		spine.set_visible(True)
	
	plt.tight_layout()
	plt.savefig('processed_files/v2/assets/error_heatmap.jpeg')
	plt.show()


def fetch_activity_error_categories_split():
	user_recordings = dict(db_service.fetch_all_recorded_recordings())
	activity_error_categories = {}
	for recording_id, user_recording_dict in user_recordings.items():
		recording = Recording.from_dict(user_recording_dict)
		if recording.activity_id not in activity_id_to_activity_name_map:
			print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
			print(f"-----------------------------------------------------")
			continue
		
		activity_name = activity_id_to_activity_name_map[recording.activity_id]
		if not activity_name in activity_error_categories:
			activity_error_categories[activity_name] = {}
			for error_tag in ErrorTag.mistake_tag_list:
				activity_error_categories[activity_name][error_tag] = 0
		
		if recording.is_error:
			recipe_errors = recording.errors
			if recipe_errors is not None:
				for recipe_error in recipe_errors:
					activity_error_categories[activity_name][recipe_error.tag] += 1
			for recipe_step in recording.steps:
				step_errors = recipe_step.errors
				if step_errors is not None:
					for step_error in step_errors:
						activity_error_categories[activity_name][step_error.tag] += 1
	with open(f"{processed_files_directory}/v{version}/activity_error_categories.json",
	          'w') as activity_error_categories_file:
		json_data = json.dumps(activity_error_categories, indent=4)
		activity_error_categories_file.write(json_data)


if __name__ == '__main__':
	version = 2
	
	db_service = FirebaseService()
	processed_files_directory = "./processed_files"
	
	activities_dict = db_service.fetch_activities()
	activities = [Activity.from_dict(activity) for activity in activities_dict if activity is not None]
	activity_id_to_activity_name_map = {activity.id: activity.name for activity in activities}
	activity_name_to_activity_id_map = {activity.name: activity.id for activity in activities}
	activity_id_to_activity_map = {activity.id: activity for activity in activities}
	
	fetch_activity_error_categories_split()
	generate_errors_heatmap()
