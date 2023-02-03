import os

fileDirectory = os.path.dirname(__file__)


# Function to update Firebase Database of the information about all the recipes
def infoTextToDatabase(dbService, fileName, fileFolder=None):
	recipe_name = ""
	recipe_step_dict = {}
	fileFolder = fileDirectory
	with open(os.path.join(fileFolder, fileName), "r") as recipe_info_file:
		for line in recipe_info_file:
			word_list = line.split(":")
			recipe_details = word_list[0].replace("\n", "")
			if len(word_list) == 1:
				if not recipe_name == "":
					dbService.add_activity_details(recipe_name, recipe_step_dict)
				recipe_name = recipe_details
				recipe_step_dict = {}
			else:
				step_details = word_list[1].replace("\n", "")
				recipe_step_dict[word_list[0]] = step_details
		if not recipe_name == "":
			dbService.add_activity_details(recipe_name, recipe_step_dict)
