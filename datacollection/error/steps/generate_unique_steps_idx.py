import json
import os
from pathlib import Path
from pprint import pformat, pprint

import yaml
from tqdm import tqdm

file_directory = "./"
file_name = "activity_details.txt"


def activity_info_text_to_dict(file_name, fileFolder=None):
    recipe_name = ""
    recipe_step_dict = {}
    recipe_step_dict_idx = {}
    idx = 0
    all_steps = []
    with open(os.path.join(fileFolder, file_name), "r") as recipe_info_file:
        for line in recipe_info_file:
            word_list = line.split(":")
            recipe_details = word_list[0].replace("\n", "")
            if len(word_list) == 1:
                recipe_name = recipe_details
                recipe_step_dict[recipe_name] = {}
                recipe_step_dict_idx[recipe_name] = {}
            else:
                step_details = word_list[1].replace("\n", "").strip()
                recipe_step_dict[recipe_name][word_list[0]] = step_details
                recipe_step_dict_idx[recipe_name][word_list[0]] = idx
                all_steps.append(step_details)
                idx += 1
    return recipe_step_dict, all_steps, recipe_step_dict_idx


activity_step_dict, all_steps, recipe_step_dict_idx = activity_info_text_to_dict(file_name, file_directory)
print(activity_step_dict, "\n", all_steps, "\n", recipe_step_dict_idx)


def load_similar_steps(similar_step_file):
    # The left index is smaller than the right index
    similar_steps = yaml.safe_load(Path(similar_step_file).read_text())
    print(similar_steps)


similar_steps = load_similar_steps("./same_steps.yml")
# We will need two files - First file stores each recipe and the indices of its unique steps
# Second file will contain a dictionary with the indices and unique steps
def update_step_index_and_remove_steps(similar_steps, all_steps):
    idx = 0
    old_step_index_to_updated_step_index = {}
    old_step_index = {}
    for k, v in enumerate(all_steps):
        old_step_index[str(k)] = v
    for old_index in old_step_index:




