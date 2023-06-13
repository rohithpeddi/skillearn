import json
import os
import os.path as osp
import sys
import yaml

from datacollection.user_app.backend.app.services.box_service import BoxService


def add_path(path):
	if path not in sys.path:
		sys.path.insert(0, path)


def initialize_paths():
	this_dir = osp.dirname(__file__)
	
	lib_path = osp.join(this_dir, "../../datacollection")
	add_path(lib_path)


def load_yaml_file(file_path):
	with open(file_path, 'r') as file:
		try:
			data = yaml.safe_load(file)
			return data
		except yaml.YAMLError as e:
			print(f"Error while parsing YAML file: {e}")


initialize_paths()

from datacollection.user_app.backend.app.models.annotation import Annotation
from datacollection.user_app.backend.app.models.annotation_assignment import AnnotationAssignment
from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.services.box_service import BoxService
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.models.activity import Activity
from revChatGPT.V3 import Chatbot
from moviepy.editor import VideoFileClip
from datacollection.user_app.backend.app.models.error_tag import ErrorTag


def create_directory(output_directory):
	if not osp.exists(output_directory):
		os.makedirs(output_directory)


class ErrorStatistics:
	
	def __init__(self):
		self.db_service = FirebaseService()
		self.box_service = BoxService()
		# self.box_service.root_folder_id = '210901008116'
		# self.box_recording_scripts_folder_id = '210901008116'
		
		self.environments_info_list = load_yaml_file(
			'../../datacollection/user_app/backend/info_files/environments.yaml')
		self.activities_dict = self.db_service.fetch_activities()
		self.activities = [Activity.from_dict(activity) for activity in self.activities_dict if activity is not None]
		self.activity_id_to_activity_name_map = {activity.id: activity.name for activity in self.activities}
		self.activity_name_to_activity_id_map = {activity.name: activity.id for activity in self.activities}
		self.activity_id_to_activity_map = {activity.id: activity for activity in self.activities}
		
		self.output_directory = './output_directory'
		create_directory(self.output_directory)
		self.chatgpt_response_directory = "./chatgpt_response"
		create_directory(self.chatgpt_response_directory)
		self.processed_files_directory = "./processed_files"
		create_directory(self.processed_files_directory)
		self.backup_directory = "./backup_directory"
		create_directory(self.backup_directory)
		self.backup_recordings_directory = f"{self.backup_directory}/recordings"
		create_directory(self.backup_recordings_directory)
		
		self.intermediate_directory = "./intermediate_directory"
		create_directory(self.intermediate_directory)
		
		self.annotations_directory = "./annotations"
		create_directory(self.annotations_directory)
		
		annotations = dict(self.db_service.fetch_annotations())
		self.annotations = []
		for annotation_id, annotation_dict in annotations.items():
			annotation = Annotation.from_dict(annotation_dict)
			# assert annotation_id == annotation.id
			self.annotations.append(annotation)
		
		self.recording_id_to_annotation_map = {annotation.recording_id: annotation for annotation in self.annotations}
		
		self.video_files_directory = "D:\\DATA\\COLLECTED\\PTG\\ANNOTATION\\ANNOTATION"
		
		self._create_activity_step_ids_map()
	
	def _create_activity_step_ids_map(self):
		self.activity_id_to_step_id_map = {}
		self.activity_id_to_id_step_map = {}
		user_recordings = dict(self.db_service.fetch_all_selected_recordings())
		for recording_id, user_recording_dict in user_recordings.items():
			recording = Recording.from_dict(user_recording_dict)
			if recording.activity_id not in self.activity_id_to_activity_name_map:
				print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			
			if recording.is_error:
				print(f"Recording {recording.id} is an error recording. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			
			activity_id = recording.activity_id
			if activity_id not in self.activity_id_to_id_step_map:
				print(f'Preparing activity id to step ids map for activity {activity_id}...')
				self.activity_id_to_id_step_map[activity_id] = {}
				self.activity_id_to_step_id_map[activity_id] = {}
				activity_steps = recording.steps
				count = 1
				for step in activity_steps:
					self.activity_id_to_id_step_map[activity_id][count] = step.description
					self.activity_id_to_step_id_map[activity_id][step.description] = count
					count += 1
	
	def fetch_activity_description(self, activity: Activity):
		description = "\n"
		for step in activity.steps:
			description += f"{step.description}\n"
		return description
	
	def fetch_error_script(self, recording: Recording):
		activity_name = self.activity_id_to_activity_name_map[recording.activity_id]
		activity = self.activity_id_to_activity_map[recording.activity_id]
		activity_description = self.fetch_activity_description(activity)
		error_script = f"Recipe: {activity_name}\n"
		error_script += f"-----------------------------------------------------\n"
		error_script += f"Description: {activity_description}\n"
		error_script += f"-----------------------------------------------------\n"
		error_script += f"Errors made:\n"
		recipe_errors = recording.errors
		if recipe_errors is not None:
			for error in recipe_errors:
				error_script += f"{error.tag}: {error.description}\n"
		steps = recording.steps
		for step in steps:
			step_errors = step.errors
			if step_errors is not None:
				for error in step_errors:
					error_script += f"{error.tag}: {error.description} made in {step.description}\n"
		
		with open(f"{self.output_directory}/{activity_name}_{recording.id}.txt", 'a') as file:
			file.write(error_script)
		
		error_script += f"-----------------------------------------------------\n"
		error_script += f"Given the recipe name, description and errors made in the recipe. Can you summarize and list errors in this format:\n"
		error_script += f"Type of error - Very Short description of errors (less than 5 words) - (verb, noun) or (verb, noun, adverb) pairs in sentence\n"
		error_script += f"-----------------------------------------------------\n"
		error_script += f"Example:\n"
		error_script += f"Preparation - Wrong surface used - (Place, plate)\n"
		error_script += f"Technique - Wrong knife used - (Clean, knife)\n"
		error_script += f"Technique - Incorrect rolling technique - (Roll, tightly)\n"
		error_script += f"Missing Step - Discard ends not mentioned - (Discard, ends)\n"
		error_script += f"-----------------------------------------------------\n"
		
		chatbot = Chatbot(api_key="")
		chat_response = chatbot.ask(error_script)
		print(chat_response)
		
		with open(f"{self.chatgpt_response_directory}/{activity_name}_{recording.id}.txt", 'w') as file:
			file.write(chat_response)
	
	def fetch_error_script_for_all_recordings(self):
		user_recordings = dict(self.db_service.fetch_all_selected_recordings())
		for recording_id, user_recording_dict in user_recordings.items():
			recording = Recording.from_dict(user_recording_dict)
			if recording.activity_id not in self.activity_id_to_activity_name_map:
				print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			if not recording.is_error:
				print(f"Recording {recording.id} is not an error recording. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			print(f"-----------------------------------------------------")
			print(f"Processing recording {recording.id}...")
			self.fetch_error_script(recording)
			print(f"Processed recording {recording.id}")
			print(f"-----------------------------------------------------")
	
	def process_chatgpt_response(self):
		processed_output_file = f"{self.processed_files_directory}/processed_chatgpt_response_output.txt"
		with open(processed_output_file, 'a') as processed_output_file:
			for file in os.listdir(self.chatgpt_response_directory):
				if file.endswith(".txt"):
					with open(f"{self.chatgpt_response_directory}/{file}", 'r') as chat_response_file:
						chat_response = chat_response_file.read()
						processed_output_file.write(chat_response)
						processed_output_file.write("\n")
	
	def compile_error_categories(self):
		processed_output_file = f"{self.processed_files_directory}/processed_chatgpt_response_output.txt"
		with open(processed_output_file, 'r') as processed_output_file:
			chat_responses = processed_output_file.readlines()
			error_dictionary = {}
			error_dictionary["Preparation Error"] = set()
			error_dictionary["Technique Error"] = set()
			error_dictionary["Missing Step"] = set()
			error_dictionary["Other"] = set()
			error_dictionary["Timing Error"] = set()
			error_dictionary["Temperature Error"] = set()
			error_dictionary["Measurement Error"] = set()
			error_dictionary["Order Error"] = set()
			for chat_response in chat_responses:
				error_category = chat_response.split("-")[0].strip()
				if error_category is not None and error_category != "" and error_category != "None":
					if len(chat_response.split("-")) < 2:
						print(f"Chat response {chat_response} does not have a short description. Skipping...")
						continue
					is_error_category_present = False
					for error_category_dict in error_dictionary.keys():
						if error_category_dict in error_category or error_category in error_category_dict:
							error_category = error_category_dict
							is_error_category_present = True
							break
					if not is_error_category_present:
						error_category = "Other"
					error_short_description = chat_response.split("-")[1].strip()
					error_dictionary[error_category].add(error_short_description)
			
			def set_default(obj):
				if isinstance(obj, set):
					return list(obj)
				raise TypeError
			
			with open(f"{self.processed_files_directory}/error_categories.json", 'w') as error_categories_file:
				json_data = json.dumps(error_dictionary, indent=4, default=set_default)
				error_categories_file.write(json_data)
	
	def backup_all_recordings(self):
		user_recordings = dict(self.db_service.fetch_all_selected_recordings())
		
		for recording_id, user_recording_dict in user_recordings.items():
			recording = Recording.from_dict(user_recording_dict)
			if recording.activity_id not in self.activity_id_to_activity_name_map:
				print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			print(f"-----------------------------------------------------")
			print(f"Processing recording {recording.id}...")
			backup_recording_file_path = f"{self.backup_recordings_directory}/{recording.id}.json"
			with open(backup_recording_file_path, "w") as backup_recording_file:
				backup_recording_file.write(json.dumps(recording.to_dict(), indent=4))
			
			self.box_service.client.folder(folder_id=self.box_recording_scripts_folder_id).upload(
				backup_recording_file_path)
			print(f"Processed recording {recording.id}")
			print(f"-----------------------------------------------------")
	
	def fetch_recipe_error_normal_division_statistics(self):
		user_recordings = dict(self.db_service.fetch_all_selected_recordings())
		
		recipe_error_normal_division_statistics = {}
		total_normal_recordings = 0
		total_error_recordings = 0
		total_normal_duration = 0.
		total_error_duration = 0.
		for recording_id, user_recording_dict in user_recordings.items():
			recording = Recording.from_dict(user_recording_dict)
			if recording.activity_id not in self.activity_id_to_activity_name_map:
				print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			
			if os.path.exists(os.path.join(self.video_files_directory, recording.id + "_360p.mp4")):
				video_clip = VideoFileClip(os.path.join(self.video_files_directory, recording.id + "_360p.mp4"))
				recording_video_duration = video_clip.duration / 3600
				video_clip.close()
			elif os.path.exists(os.path.join(self.video_files_directory, recording.id + "_360p.MP4")):
				video_clip = VideoFileClip(os.path.join(self.video_files_directory, recording.id + "_360p.MP4"))
				recording_video_duration = video_clip.duration / 3600
				video_clip.close()
			else:
				print(f"Recording {recording.id} does not have a video. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			
			if not self.activity_id_to_activity_name_map[
				       recording.activity_id] in recipe_error_normal_division_statistics:
				recipe_error_normal_division_statistics[
					self.activity_id_to_activity_name_map[recording.activity_id]] = {}
			
			if not recording.is_error:
				total_normal_recordings += 1
				total_normal_duration += recording_video_duration
				if not "normal" in recipe_error_normal_division_statistics[
					self.activity_id_to_activity_name_map[recording.activity_id]]:
					recipe_error_normal_division_statistics[
						self.activity_id_to_activity_name_map[recording.activity_id]]["normal"] = 0
					recipe_error_normal_division_statistics[
						self.activity_id_to_activity_name_map[recording.activity_id]]["normal_duration"] = 0
				recipe_error_normal_division_statistics[self.activity_id_to_activity_name_map[recording.activity_id]][
					"normal"] += 1
				recipe_error_normal_division_statistics[
					self.activity_id_to_activity_name_map[recording.activity_id]][
					"normal_duration"] += recording_video_duration
			else:
				total_error_recordings += 1
				total_error_duration += recording_video_duration
				if not "error" in recipe_error_normal_division_statistics[
					self.activity_id_to_activity_name_map[recording.activity_id]]:
					recipe_error_normal_division_statistics[
						self.activity_id_to_activity_name_map[recording.activity_id]]["error"] = 0
					recipe_error_normal_division_statistics[
						self.activity_id_to_activity_name_map[recording.activity_id]]["error_duration"] = 0
				recipe_error_normal_division_statistics[self.activity_id_to_activity_name_map[recording.activity_id]][
					"error"] += 1
				recipe_error_normal_division_statistics[self.activity_id_to_activity_name_map[recording.activity_id]][
					"error_duration"] += recording_video_duration
		
		with open(f"{self.processed_files_directory}/recipe_error_normal_division_statistics.json",
		          'w') as recipe_error_normal_division_statistics_file:
			json_data = json.dumps(recipe_error_normal_division_statistics, indent=4)
			recipe_error_normal_division_statistics_file.write(json_data)
		
		print(f"Total normal recordings: {total_normal_recordings}")
		print(f"Total error recordings: {total_error_recordings}")
		print(f"Total normal duration: {total_normal_duration}")
		print(f"Total error duration: {total_error_duration}")
	
	def fetch_activity_details(self):
		# 1. Activity name to activity id map
		with open(f"{self.processed_files_directory}/activity_name_to_activity_id_map.json",
		          "r") as activity_name_to_activity_id_map_file:
			json_data = json.dumps(self.activity_name_to_activity_id_map, indent=4)
			activity_name_to_activity_id_map_file.write(json_data)
		
		with open(f"{self.processed_files_directory}/activity_id_to_activity_name_map.json",
		          "r") as activity_id_to_activity_name_map_file:
			json_data = json.dumps(self.activity_id_to_activity_name_map, indent=4)
			activity_id_to_activity_name_map_file.write(json_data)
	
	def fetch_user_id_for_activity(self, activity_id, annotation_assignment_list):
		for annotation_assignment in annotation_assignment_list:
			if activity_id in annotation_assignment.activities:
				return annotation_assignment.user_id
	
	def fetch_recording_annotation(self, recording: Recording):
		# annotation_assignments_dict = self.db_service.fetch_annotation_assignment()
		# annotation_assignments_list = [AnnotationAssignment.from_dict(annotation_assignment_dict) for
		#                                annotation_assignment_dict in annotation_assignments_dict if
		#                                annotation_assignment_dict is not None]
		#
		# user_id = self.fetch_user_id_for_activity(recording.activity_id, annotation_assignments_list)
		# try:
		# 	annotation = Annotation.from_dict(self.db_service.fetch_annotation(str(recording.id) + "_" + str(user_id)))
		# except:
		# 	print(f"Annotation not found for recording {recording.id}")
		# 	return None
		
		annotation = self.recording_id_to_annotation_map[recording.id]
		
		if annotation is None:
			print(f"Annotation not found for recording {recording.id}")
			return None
		
		annotation_json = annotation.annotation_json
		
		if annotation_json is None:
			print(f"Annotation json not found for recording {recording.id}")
			annotation_json_file_name = f"{recording.id}_360p.json"
			annotation_json_file_path = os.path.join(self.intermediate_directory, annotation_json_file_name)
			annotation_json = self.box_service.fetch_latest_annotation_json(recording.id, annotation_json_file_path)
			if annotation_json is None:
				print(f"Annotation json not found for recording {recording.id}")
				return None
			
			annotation.annotation_json = annotation_json
			self.db_service.update_annotation(annotation)
		
		step_annotations = annotation_json[0]["annotations"][0]["result"]
		
		step_annotation_dict_list = []
		generate_csv = True
		if generate_csv:
			for step_annotation in step_annotations:
				start_time = step_annotation["value"]["start"]
				end_time = step_annotation["value"]["end"]
				labels = step_annotation["value"]["labels"]
				step_annotation_dict = {
					"start_time": start_time,
					"end_time": end_time,
					"labels": labels
				}
				
				def fetch_count(activity_step_id):
					if activity_step_id in self.activity_id_to_step_id_map[recording.activity_id]:
						return self.activity_id_to_step_id_map[recording.activity_id][activity_step_id]
					else:
						for key in self.activity_id_to_step_id_map[recording.activity_id]:
							if activity_step_id[1:15] in key:
								return self.activity_id_to_step_id_map[recording.activity_id][key]
				
				if len(labels[0].strip('()').split(':')) >= 3:
					try:
						step_id = labels[0].strip('()').split(':')[3].split(")")[0].strip()
					except:
						step_id = labels[0].strip('()').split(':')[7].strip()
				else:
					step_id = labels[0].strip('()').split(':')[1].strip()
				count = fetch_count(step_id)
				
				step_annotation_dict_list.append(step_annotation_dict)
				activity_name = self.activity_id_to_activity_name_map[recording.activity_id].replace(" ", "")
				annotation_activity_directory = os.path.join(self.annotations_directory, activity_name)
				if not os.path.exists(annotation_activity_directory):
					os.makedirs(annotation_activity_directory)
					
				annotation_file_directory = os.path.join(annotation_activity_directory, "annotations", "normal")
				create_directory(annotation_file_directory)
				annotation_file_path = os.path.join(annotation_file_directory, f"{recording.id}.csv")
				with open(annotation_file_path, "a") as annotation_file:
					annotation_file.write(
						f"{start_time},{end_time},\"{count} {labels[0].strip('()').split(':')[1].strip()}\"\n")
		
		return step_annotations
	
	def fetch_annotations_for_activity(self, activity_id):
		recordings_list = []
		user_recordings = dict(self.db_service.fetch_all_selected_recordings())
		for recording_id, user_recording_dict in user_recordings.items():
			recording = Recording.from_dict(user_recording_dict)
			if recording.activity_id not in self.activity_id_to_activity_name_map:
				print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			
			recording_id = int(recording.id.split("_")[1])
			
			if recording_id > 25:
				continue
			if recording_id > 125:
				continue
			
			if recording.activity_id == activity_id:
				recordings_list.append(recording)
				recording_annotation = self.fetch_recording_annotation(recording)
				
				annotation_activity_directory = f"{self.annotations_directory}/{self.activity_id_to_activity_name_map[recording.activity_id]}"
				annotation_activity_directory = annotation_activity_directory.replace(" ", "")
				create_directory(annotation_activity_directory)
	
	# recording_annotation_file_path = f"{annotation_activity_directory}/{recording.id}.json"
	# with open(recording_annotation_file_path, "w") as recording_annotation_file:
	# 	json_data = json.dumps(recording_annotation, indent=4)
	# 	recording_annotation_file.write(json_data)
	
	def fetch_activity_error_categories_split(self):
		user_recordings = dict(self.db_service.fetch_all_selected_recordings())
		
		activity_error_categories = {}
		for recording_id, user_recording_dict in user_recordings.items():
			recording = Recording.from_dict(user_recording_dict)
			if recording.activity_id not in self.activity_id_to_activity_name_map:
				print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			
			activity_name = self.activity_id_to_activity_name_map[recording.activity_id]
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
							if step_error.tag == "Other":
								continue
							activity_error_categories[activity_name][step_error.tag] += 1
		with open(f"{self.processed_files_directory}/activity_error_categories.json",
		          'w') as activity_error_categories_file:
			json_data = json.dumps(activity_error_categories, indent=4)
			activity_error_categories_file.write(json_data)
	
	def fetch_total_steps_count(self):
		total_steps_count = 0
		user_recordings = dict(self.db_service.fetch_all_selected_recordings())
		for recording_id, user_recording_dict in user_recordings.items():
			recording = Recording.from_dict(user_recording_dict)
			if recording.activity_id not in self.activity_id_to_activity_name_map:
				print(f"Recording {recording.id} does not belong to any recipe. Skipping...")
				print(f"-----------------------------------------------------")
				continue
			
			total_steps_count += len(recording.steps)
		print(f"Total steps count: {total_steps_count}")
	
	def save_activity_id_to_activity_name_map(self):
		with open(f"{self.processed_files_directory}/activity_id_to_activity_name_map.json",
		          'w') as activity_id_to_activity_name_map_file:
			json_data = json.dumps(self.activity_id_to_activity_name_map, indent=4)
			activity_id_to_activity_name_map_file.write(json_data)
	
	def generate_annotations_for_all_activities(self):
		for activity in self.activities:
			self.fetch_annotations_for_activity(activity.id)



if __name__ == '__main__':
	error_statistics = ErrorStatistics()
	error_statistics.generate_annotations_for_all_activities()
# error_statistics.fetch_error_script_for_all_recordings()
# error_statistics.compile_error_categories()
# error_statistics.backup_all_recordings()
# error_statistics.fetch_recipe_error_normal_division_statistics()
# error_statistics.fetch_activity_error_categories_split()
# error_statistics.fetch_annotations_for_activity(10)
# error_statistics.fetch_annotations_for_activity(8)
# error_statistics.fetch_annotations_for_activity(12)
# error_statistics.fetch_total_steps_count()
# error_statistics.save_activity_id_to_activity_name_map()
