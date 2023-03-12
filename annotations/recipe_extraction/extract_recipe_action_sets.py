import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

# recipes = pd.read_csv(r'./dataset/small.csv')
recipes = pd.read_csv(r'./dataset/full_dataset.csv')
recipes = recipes.rename(columns={'Unnamed: 0': "idx"})
recipes = recipes.drop(columns=['ingredients', 'link', 'source', 'NER'])
recipes = recipes.to_numpy()
# for actions we have verb, noun
actions = np.loadtxt("./dataset/epic_action_classes.csv", delimiter=",", dtype=str)


def create_action_dict(actions):
    # In action dict first key is verb and second key is noun
    action_dict = {}
    for each_action in actions:
        action_dict[each_action[0], each_action[1]] = []
    return action_dict


def populate_action_dict(actions, recipes):
    action_dict = create_action_dict(actions)
    recipe_dict = {i: [] for i in range(len(recipes))}
    for each_recipe in tqdm(recipes):
        index, title, directions = each_recipe
        directions_list = directions.split('",')
        for each_step in directions_list:
            for each_action_pair in action_dict:
                if each_action_pair[0] in each_step and each_action_pair[1] in each_step:
                    action_dict[each_action_pair].append(index)
                    recipe_dict[index].append(each_action_pair)
                    break
    return action_dict, recipe_dict


action_dict, recipe_dict = populate_action_dict(actions, recipes)
from pathlib import Path

directory = "./output/"
Path(directory).mkdir(parents=True, exist_ok=True)
# with open(f'{directory}recipes_with_actions.yml', 'w') as yaml_file:
#     yaml.dump(action_dict, stream=yaml_file, default_flow_style=False, sort_keys=False)

import pickle

with open(f'{directory}recipes_for_actions.pkl', 'wb') as f:
    pickle.dump(action_dict, f)


with open(f'{directory}actions_in_recipes.pkl', 'wb') as f:
    pickle.dump(recipe_dict, f)

with open(f'{directory}actions_in_recipes.pkl', 'rb') as f:
    loaded_dict = pickle.load(f)
print(loaded_dict)

with open(f'{directory}recipes_for_actions.pkl', 'rb') as f:
    loaded_dict = pickle.load(f)

print(loaded_dict)
