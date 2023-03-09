import pickle
from collections import OrderedDict

import pandas as pd

with open(f'./output/actions_in_recipes.pkl', 'rb') as f:
    actions_in_recipes = pickle.load(f)

with open(f'./output/recipes_for_actions.pkl', 'rb') as f:
    recipes_for_actions = pickle.load(f)

recipes = pd.read_csv(r'./dataset/full_dataset.csv')
recipes = recipes.rename(columns={'Unnamed: 0': "idx"})
recipes = recipes.drop(columns=['ingredients', 'link', 'source', 'NER'])
# recipes = recipes.to_numpy()


from itertools import islice


def take(n, iterable):
    """Return the first n items of the iterable as a list."""
    return list(islice(iterable, n))


res = OrderedDict(sorted(actions_in_recipes.items(), key=lambda x: len(x[1]), reverse=True))
first_100 = take(5, res.items())
for each in first_100:
    recipe_index = each[0]
    mask = recipes['idx'] == recipe_index
    df_new = pd.DataFrame(recipes[mask])
    print(df_new["title"].iloc[0])
    print("Number of actions : ", len(each[1]))
# print(first_100[0])