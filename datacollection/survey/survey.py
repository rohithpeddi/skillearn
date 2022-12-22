import json
import os

import pandas as pd
from pyinflect import getInflection


# For "-ing" form of a word
# Ref: https://stackoverflow.com/questions/64977817/gerund-form-of-a-word-in-python

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


def fetch_recipes_from_json(recipe_json_file):
	recipes = list()
	recipe_by_steps_list = list()
	with open(recipe_json_file) as f:
		data = json.load(f)
		for name, recipe in data.items():
			recipes.append('\n'.join(recipe))
			recipe_by_steps_list.append(recipe)
	return recipes, recipe_by_steps_list


def fetch_questions_from_json(questions_json_file):
	questions_template_dict = dict()
	with open(questions_json_file) as f:
		data = json.load(f)
		for q_no, q_template in data.items():
			questions_template_dict[q_no] = q_template
	return questions_template_dict


def get_joined_list_str(list_items):
	return "[" + ", ".join(list_items) + "]"


def fetch_actions_from_json(action_json_file):
	actions = list()
	actions_list = list()
	total_skills_list = list()
	with open(action_json_file) as f:
		data = json.load(f)
		for category, action_list in data.items():
			skills_list = list()
			for action in action_list:
				actions.append(action)
				gerund = getInflection(action, 'VBG')
				if gerund is None:
					continue
				gerund = gerund[0]
				actions_list.append(gerund)
				skills_list.append(gerund)
			total_skills_list.append(get_joined_list_str(skills_list))
	return actions, actions_list, total_skills_list


def generate_questions(questions, tag, tags_list_map):
	replace_list = tags_list_map[tag]
	questions_new = list()
	if isinstance(replace_list, str):
		for question in questions:
			questions_new.append(question.replace(tag, replace_list))
		return questions_new
	for rl in replace_list:
		for question in questions:
			if isinstance(rl, list):
				for item in rl:
					questions_new.append(question.replace(tag, item))
			else:
				questions_new.append(question.replace(tag, rl))
	return questions_new


def main():
	recipes_json_path = "input_data/recipe.json.bak1"
	actions_json_path = "./input_data/action.json"
	questions_json_path = "./input_data/questions.json"

	recipes, recipe_by_steps = fetch_recipes_from_json(recipes_json_path)
	actions, actions_list, skills_list = fetch_actions_from_json(actions_json_path)

	questions_template_dict = fetch_questions_from_json(questions_json_path)
	for q_no, q_template in questions_template_dict.items():
		print(q_no, ":", q_template)

	tags_list_map = {
		'{recipe}': recipes,
		'{recipe::step}': recipe_by_steps,
		'{skill_list}': skills_list,
		'{action_list}': get_joined_list_str(actions_list),
		'{action}': actions,
	}

	tags_list = ['{recipe}', '{recipe::step}', '{skill_list}', '{action_list}', '{action}']
	for q_no, q_template in questions_template_dict.items():
		questions = list([q_template])
		for tag in tags_list:
			if tag in questions[0]:
				questions = generate_questions(questions, tag, tags_list_map)
		# Save that question in that corresponding file
		with open(f'./questions/{q_no}.txt', 'w') as f:
			for question in questions:
				f.write(question)
				f.write("\n\n")
		with open(f'./questions/{q_no}.pkl', 'wb') as fp:
			q_len = len(questions)
			answers = [""] * q_len
			done = [False] * q_len
			df = pd.DataFrame({
				'question': questions,
				'answer': answers,
				'done': done,
			})
			# pickle.dump(questions, fp)
			df.to_pickle(fp)
		df = pd.read_pickle(f'./questions/{q_no}.pkl')
		print(df.shape)
	pass


def generate_questions_for_recipe(skills, recipe, recipe_directory, output_path):
	with open(os.path.join(output_path, recipe), 'w+') as recipe_question_output_file:
		with open(os.path.join(recipe_directory, recipe), 'r') as recipe_file:
			recipe_steps = [line[:-1] for line in recipe_file]
			for recipe_step in recipe_steps:
				for category_skill_list in skills:
					question = "What skills from \'{}\' are required to perform \'{}\'?".format(category_skill_list,
																								recipe_step)
					recipe_question_output_file.write(question)
					recipe_question_output_file.write("\n")


def generate_questions_for_api():
	actions_json_file = "./input_data/action.json"
	recipes_dir_path = "./recipes"
	questions_dir_path = "./questions"

	recipes = os.listdir(recipes_dir_path)
	actions, actions_list, skills_list = fetch_actions_from_json(actions_json_file)

	for recipe in recipes:
		generate_questions_for_recipe(skills_list, recipe, recipes_dir_path, questions_dir_path)


def generate_answers_for_questions():
	questions_dir_path = "./questions"
	answers_dir_path = "./answers"

	recipeQuestionListFiles = os.listdir(questions_dir_path)
	for recipeQuestionListFile in recipeQuestionListFiles:
		with open(os.path.join(answers_dir_path, recipeQuestionListFile), 'w+') as recipe_answer_output_file:
			with open(os.path.join(questions_dir_path, recipeQuestionListFile), 'r') as recipe_questions_file:
				recipe_questions = [line[:-1] for line in recipe_questions_file]
				for recipe_question in recipe_questions:
					recipe_answer_output_file.write(recipe_question)
					recipe_answer_output_file.write("\n\n")
					recipe_answer_output_file.write(
						"\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")


if __name__ == '__main__':
	generate_answers_for_questions()
