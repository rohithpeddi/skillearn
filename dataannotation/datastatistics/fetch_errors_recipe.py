import json
import os
import os.path as osp
import sys
import yaml


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

from datacollection.user_app.backend.app.services.firebase_service import FirebaseService
from datacollection.user_app.backend.app.models.recording import Recording
from datacollection.user_app.backend.app.models.activity import Activity
from revChatGPT.V3 import Chatbot


def create_directory(output_directory):
	if not osp.exists(output_directory):
		os.makedirs(output_directory)


class ErrorStatistics:
	
	def __init__(self):
		self.db_service = FirebaseService()
		
		self.environments_info_list = load_yaml_file(
			'../../datacollection/user_app/backend/info_files/environments.yaml')
		self.activities_dict = self.db_service.fetch_activities()
		self.activities = [Activity.from_dict(activity) for activity in self.activities_dict if activity is not None]
		self.activity_id_to_activity_name_map = {activity.id: activity.name for activity in self.activities}
		self.activity_id_to_activity_map = {activity.id: activity for activity in self.activities}
		
		self.output_directory = './output_directory'
		create_directory(self.output_directory)
		self.chatgpt_response_directory = "./chatgpt_response"
		create_directory(self.chatgpt_response_directory)
		self.processed_files_directory = "./processed_files"
		create_directory(self.processed_files_directory)
	
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
				json_data = json.dumps(error_dictionary, indent=4,  default=set_default)
				error_categories_file.write(json_data)


if __name__ == '__main__':
	error_statistics = ErrorStatistics()
	# error_statistics.fetch_error_script_for_all_recordings()
	error_statistics.compile_error_categories()
