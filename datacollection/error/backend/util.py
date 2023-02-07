import os

from datacollection.error.backend.constants import *
from datacollection.error.backend.firebase_service import FirebaseService

file_directory = os.path.dirname(__file__)


# Function to update Firebase Database of the information about all the recipes
def activity_info_text_to_database(db_service, file_name, fileFolder=None):
	recipe_name = ""
	recipe_step_dict = {}
	fileFolder = file_directory
	with open(os.path.join(fileFolder, file_name), "r") as recipe_info_file:
		for line in recipe_info_file:
			word_list = line.split(":")
			recipe_details = word_list[0].replace("\n", "")
			if len(word_list) == 1:
				if not recipe_name == "":
					db_service.add_activity_info_details(recipe_name, recipe_step_dict)
				recipe_name = recipe_details
				recipe_step_dict = {}
			else:
				step_details = word_list[1].replace("\n", "")
				recipe_step_dict[word_list[0]] = step_details
		if not recipe_name == "":
			db_service.add_activity_info_details(recipe_name, recipe_step_dict)


def info_text_to_database(db_service, file_name, info_child):
	info_dict = {}
	file_folder = file_directory
	with open(os.path.join(file_folder, file_name), "r") as info_file:
		for line in info_file:
			word_list = line.split(":")
			info_key = word_list[0].replace("\n", "")
			info_value = word_list[1].replace("\n", "")
			info_dict[info_key] = info_value
	db_service.add_info_details(info_child, info_dict)


if __name__ == "__main__":
	db_service = FirebaseService()
	activity_info_text_to_database(db_service, "info_files/activity_details.txt")
	info_text_to_database(db_service, "info_files/persons.txt", PERSONS)
	info_text_to_database(db_service, "info_files/places.txt", PLACES)
	info_text_to_database(db_service, "info_files/recording_numbers.txt", RECORDING_NUMBERS)
