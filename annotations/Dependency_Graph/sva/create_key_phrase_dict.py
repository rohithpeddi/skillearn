import csv

import yaml
from keyphrase_vectorizers import KeyphraseCountVectorizer
from tqdm import tqdm

with open("activity_dict_with_step_index.yml", "r") as stream:
    try:
        activity_dict = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
all_key_phrases = {}
for each_recipe in tqdm(activity_dict):
    recipe_key_phrases = []
    for each_step in activity_dict[each_recipe]:
        text = activity_dict[each_recipe][each_step]['text']
        # Init default vectorizer.
        vectorizer = KeyphraseCountVectorizer()
        # extract the keyphrases for this sentence
        # keyphrases act as the noun entities for a given recipe.
        document_keyphrase_matrix = vectorizer.fit_transform([text]).toarray()
        keyphrases = vectorizer.get_feature_names_out().tolist()
        recipe_key_phrases.append(keyphrases)
    all_key_phrases[each_recipe] = recipe_key_phrases
    print(all_key_phrases)

import json
with open('key_phrases.json', 'w') as fout:
    json.dump(all_key_phrases, fout, ensure_ascii=False, indent=4)

with open('key_phrases.json', 'r') as fin:
    all_key_phrase = json.load(fin, )
print(all_key_phrase)

