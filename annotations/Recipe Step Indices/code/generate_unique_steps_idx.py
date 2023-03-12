import json
import os
from pathlib import Path
from pprint import pformat, pprint

import yaml
from natsort import natsorted
from tqdm import tqdm

file_directory = "./"
file_name = "activity_details.txt"


def activity_info_text_to_dict(file_name, fileFolder=None):
    recipe_name = ""
    recipe_step_dict = {}
    recipe_step_dict_idx = {}
    idx = 0
    unique_steps = []
    with open(os.path.join(fileFolder, file_name), "r") as recipe_info_file:
        for line in recipe_info_file:
            word_list = line.split(":")
            recipe_details = word_list[0].replace("\n", "").strip()
            if len(word_list) == 1:
                recipe_name = recipe_details
                recipe_step_dict[recipe_name] = {}
                recipe_step_dict_idx[recipe_name] = {}
            else:
                step_details = word_list[1].replace("\n", "").strip()
                recipe_step_dict[recipe_name][word_list[0]] = step_details
                recipe_step_dict_idx[recipe_name][word_list[0]] = idx
                unique_steps.append(step_details)
                idx += 1
    print(f"Total Number of recipe steps = {idx}")
    return recipe_step_dict, unique_steps, recipe_step_dict_idx


activity_step_dict, all_steps, recipe_step_dict_idx = activity_info_text_to_dict(file_name, file_directory)
print(activity_step_dict, "\n", all_steps, "\n", recipe_step_dict_idx)


# We will need two files - First file stores each recipe and the indices of its unique recipes
# Second file will contain a dictionary with the indices and unique recipes
def update_step_index(all_steps, activity_step_dict):
    index_to_step = {}
    step_to_index = {}
    # all_steps = natsorted(list(all_steps))
    print(f"Unique number of recipe steps - {len(all_steps)}")
    idx = 0
    for k, v in enumerate(all_steps):
        if str(v) in step_to_index:
            continue
        else:
            step_to_index[str(v)] = idx
            idx += 1


    pprint(step_to_index)
    for k, v in step_to_index.items():
        index_to_step[str(v)] = str(k)
    pprint(index_to_step)
    updated_activity_dict = {}
    for recipe in activity_step_dict:
        updated_activity_dict[recipe] = {}
        for step in natsorted(activity_step_dict[recipe]):
            updated_activity_dict[recipe][step] = {}
            updated_activity_dict[recipe][step]["text"] = activity_step_dict[recipe][step]
            updated_activity_dict[recipe][step]["index"] = int(step_to_index[activity_step_dict[recipe][step]])
    return updated_activity_dict, index_to_step, step_to_index


updated_activity_dict, index_to_step, step_to_index = update_step_index(all_steps, activity_step_dict)
pprint(updated_activity_dict)
with open('./output/activity_dict_with_step_index.yml', 'w') as yaml_file:
    yaml.dump(updated_activity_dict, stream=yaml_file, default_flow_style=False, sort_keys=False)

with open('./output/index_to_step.yml', 'w') as yaml_file:
    yaml.dump(index_to_step, stream=yaml_file, default_flow_style=False, sort_keys=False)

with open('./output/step_to_index.yml', 'w') as yaml_file:
    yaml.dump(step_to_index, stream=yaml_file, default_flow_style=False, sort_keys=False)
