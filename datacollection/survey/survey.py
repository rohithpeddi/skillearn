import json

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
    questions = list()
    with open(questions_json_file) as f:
        data = json.load(f)
        for name, recipe in data.items():
            questions.append(recipe)
    return questions


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
    # 1. Fetch recipes from json
    recipe_dict = {}
    # 2. Fetch actions from json
    category_action_dict = {}
    # 3. Specify output path for the output_surveys
    output_path = ""
    # 3. Make all the output_surveys
    make_surveys(recipe_dict, category_action_dict, output_path)

    recipes_json_path = "./input_data/recipe.json"
    actions_json_path = "./input_data/action.json"
    questions_json_path = "./input_data/questions.json"

    recipes, recipe_by_steps = fetch_recipes_from_json(recipes_json_path)
    actions, actions_list, skills_list = fetch_actions_from_json(actions_json_path)

    questions_tags_list = fetch_questions_from_json(questions_json_path)
    for q in questions_tags_list:
        print(q)

    tags_list_map = {
        '{recipe}': recipes,
        '{recipe::step}': recipe_by_steps,
        '{skill_list}': skills_list,
        '{action_list}': get_joined_list_str(actions_list),
        '{action}': actions,
    }

    tags_list = ['{recipe}', '{recipe::step}', '{skill_list}', '{action_list}', '{action}']
    counter = 1
    for question_tag in questions_tags_list:
        questions = list([question_tag])
        for tag in tags_list:
            if tag in questions[0]:
                questions = generate_questions(questions, tag, tags_list_map)
        # Save that question in that corresponding file
        with open(f'./questions/Q{counter}', 'w') as f:
            for question in questions:
                f.write(question)
                f.write("\n\n")
        counter += 1
    pass


if __name__ == '__main__':
    main()
