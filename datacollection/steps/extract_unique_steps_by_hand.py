import json
import os
from pprint import pformat, pprint

import yaml
from tqdm import tqdm

file_directory = "./"
file_name = "activity_details.txt"


def activity_info_text_to_dict(file_name, fileFolder=None):
    recipe_name = ""
    recipe_step_dict = {}
    all_steps = []
    with open(os.path.join(fileFolder, file_name), "r") as recipe_info_file:
        for line in recipe_info_file:
            word_list = line.split(":")
            recipe_details = word_list[0].replace("\n", "")
            if len(word_list) == 1:
                recipe_name = recipe_details
                recipe_step_dict[recipe_name] = {}
            else:
                step_details = word_list[1].replace("\n", "").strip()
                recipe_step_dict[recipe_name][word_list[0]] = step_details
                all_steps.append(step_details)
    return recipe_step_dict, all_steps


def detect_similar_steps(all_steps):
    same_steps = {}
    for idx1, step_1 in enumerate(tqdm(all_steps)):
        for idx2, step_2 in enumerate(all_steps):
            if idx1 >= idx2:
                continue
            if step_1 == step_2:
                if idx1 in same_steps:
                    same_steps[idx1].append(idx2)
                else:
                    same_steps[idx1] = [idx2]

                print(idx1, step_1)
                print(idx2, step_2)
                print()
    return same_steps
    # classes = ["not paraphrase", "is paraphrase"]
    # for i in range(len(classes)):
    #     print(f"{classes[i]}: {round(results[i] * 100)}%")


activity_step_dict, all_steps = activity_info_text_to_dict(file_name, file_directory)

d = {}
for k, v in enumerate(all_steps):
    d[str(k)] = v

with open('step_idx.yml', 'w') as yaml_file:
    yaml.dump(d, stream=yaml_file, default_flow_style=False)

same_steps = detect_similar_steps(list(all_steps))
with open('same_steps.yml', 'w') as yaml_file:
    yaml.dump(same_steps, stream=yaml_file, default_flow_style=False)