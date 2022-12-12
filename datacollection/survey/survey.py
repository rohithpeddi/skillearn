class Survey:

	def __init__(self, name, step_list, category_action_dict, output_path):
		self.name = name
		self.step_list = step_list
		self.category_action_dict = category_action_dict
		self.output_path = output_path

	def create_survey(self):
		# 1. Create a file with name of the recipe in the output path
		# 2. Loop through each step
		# 3. For each step create a block with name of the step as first question
		# 4. Take all action categories and append them after evey step
		# 5. Write everything to the file after each step
		pass


def make_surveys(recipe_dict, category_action_dict, output_path):
	pass


if __name__ == '__main__':
	# 1. Fetch recipes from json
	recipe_dict = {}
	# 2. Fetch actions from json
	category_action_dict = {}
	# 3. Specify output path for the output_surveys
	output_path = ""
	# 3. Make all the output_surveys
	make_surveys(recipe_dict, category_action_dict, output_path)
