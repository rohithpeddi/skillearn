import json
import os
import sys
import os.path as osp
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from datacollection.user_app.backend.app.models.activity import Activity
from datacollection.user_app.backend.app.models.error_tag import ErrorTag
from datacollection.user_app.backend.app.models.recording_annotation import RecordingAnnotation
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
	with open(f'{processed_files_directory}/v{version}/activity_error_categories.json', 'r') as f:
		data = json.load(f)
	
	# Convert the nested dictionary to a Pandas DataFrame
	df = pd.DataFrame.from_dict(data, orient='index')
	df_transposed = df.T
	
	# Adjust the figure size here to decrease the height
	plt.figure(figsize=(9, 4))  # The second value here determines the height
	
	# Capture the heatmap object
	heatmap = sns.heatmap(df_transposed, annot=True, cmap="Reds", fmt='g', linewidths=0.5)
	plt.title("Error Count by Recipe", fontsize=10)  # Adjusting the title font size as well
	
	# Adjust the font size of annotations
	for text in heatmap.texts:
		text.set_size(9)
	
	ax = plt.gca()
	
	# Decrease font size for x-axis and y-axis labels
	ax.tick_params(axis='x', labelsize=10)  # Adjust the value 10 as needed
	ax.tick_params(axis='y', labelsize=10)  # Adjust the value 10 as needed
	
	# Rotate x-axis labels
	plt.xticks(rotation=45, ha='right')  # 'ha' stands for horizontal alignment
	
	# Optionally, adjust the bottom parameter to increase spacing between the axis and the labels
	plt.subplots_adjust(bottom=0.2)
	
	for _, spine in ax.spines.items():
		spine.set_visible(True)
	
	plt.tight_layout()
	versioned_files_directory = f"{processed_files_directory}/v{version}/assets"
	os.makedirs(versioned_files_directory, exist_ok=True)
	plt.savefig(f'{versioned_files_directory}/ErrorRecipeCount.png')
	plt.show()


def fetch_activity_error_categories_split():
	activity_error_categories = {}
	for recording_annotation in recording_annotations:
		print(f"Processing Recording Annotation for recording id: {recording_annotation.recording_id}")
		activity_id = recording_annotation.activity_id
		activity_name = activity_id_to_activity_name_map[activity_id]
		activity_name = activity_name.replace(" ", "")[:15]
		recording_step_annotations = recording_annotation.step_annotations
		
		for recording_step_annotation in recording_step_annotations:
			step_errors = recording_step_annotation.errors
			if len(step_errors) > 0:
				for step_error in step_errors:
					if not activity_name in activity_error_categories:
						activity_error_categories[activity_name] = {}
						for error_tag in ErrorTag.mistake_tag_list:
							activity_error_categories[activity_name][error_tag] = 0
					activity_error_categories[activity_name][step_error.tag] += 1
	
	version_directory_path = f"{processed_files_directory}/v{version}"
	os.makedirs(version_directory_path, exist_ok=True)
	with open(
			f"{version_directory_path}/activity_error_categories.json", 'w'
	) as activity_error_categories_file:
		json_data = json.dumps(activity_error_categories, indent=4)
		activity_error_categories_file.write(json_data)


if __name__ == '__main__':
	version = 5
	
	db_service = FirebaseService()
	processed_files_directory = "./processed_files"
	
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
	
	fetch_activity_error_categories_split()
	generate_errors_heatmap()
