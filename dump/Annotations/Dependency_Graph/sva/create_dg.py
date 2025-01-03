import json
from pprint import pprint

from gensim.models import Word2Vec
import gensim.downloader
from nltk import PorterStemmer
similarity_value = 0.70
glove_vectors = gensim.downloader.load('word2vec-google-news-300')
ps = PorterStemmer()
# print(glove_vectors.similarity('france', 'spain'))
import numpy as np

with open('key_phrases.json', 'r') as fin:
    all_key_phrase = json.load(fin, )
print(all_key_phrase)

all_recipes_edge_matrix = {}
for recipe in enumerate(all_key_phrase):
    print(recipe)
    this_recipe_key_phrases = all_key_phrase[recipe[1]]
    num_steps = len(this_recipe_key_phrases)
    edge_matrix = np.zeros((num_steps-1, 2))
    edges = []
    for idx_1 in range(0, num_steps):
        key_phrases_idx_1 = this_recipe_key_phrases[idx_1]
        # Goes over each step
        done = False
        for idx_2 in range(idx_1-1, -1, -1):
            key_phrases_idx_2 = this_recipe_key_phrases[idx_2]
            if done:
                break
            # Goes over previous recipes to check dependence
            for each_phrase_1 in key_phrases_idx_1:
                if done:
                    break
                for each_phrase_2 in key_phrases_idx_2:
                    if done:
                        break
                    for each_word_1 in each_phrase_1.split(" "):
                        if done:
                            break
                        # if each_word_1 in each_phrase_2.split(" "):
                        #     edge_matrix[idx_1 - 1, 0] = idx_2
                        #     edge_matrix[idx_1 - 1, 1] = idx_1
                        #     done = True
                        #     break
                        else:
                            for each_word_2 in each_phrase_2.split(" "):
                                each_word_1 = ps.stem(each_word_1)
                                each_word_2 = ps.stem(each_word_2)
                                if each_word_1 == each_word_2:
                                    edge_matrix[idx_1 - 1, 0] = idx_2 + 1
                                    edge_matrix[idx_1 - 1, 1] = idx_1 + 1
                                    done = True
                                    break
                                # if each_word_1 in each_phrase_2.split(" "):
                                try:
                                    similarity = glove_vectors.similarity(each_word_1, each_word_2)
                                except KeyError:
                                    continue
                                if similarity > similarity_value:
                                    edge_matrix[idx_1-1, 0] = idx_2 + 1
                                    edge_matrix[idx_1-1, 1] = idx_1 + 1
                                    done = True
                                    break
    # TODO - Do post processing here -
    # Right now 0,0 means the node is not dependent on other nodes
    # Remove/Use in other way when we have (0,0) - Add th node to the graph
    for edge_idx in range(edge_matrix.shape[0]):
        if edge_idx != edge_matrix.shape[0]:
            if edge_matrix[edge_idx, 0] == 0 and edge_matrix[edge_idx, 1] == 0:
                edge_matrix[edge_idx, 0] = edge_idx + 1
                edge_matrix[edge_idx, 1] = edge_idx + 2


    all_recipes_edge_matrix[recipe[1]] = edge_matrix.tolist()

import json
with open(f'edge_matrices_similarity_{similarity_value}.json', 'w') as fout:
    json.dump(all_recipes_edge_matrix, fout, ensure_ascii=False, indent=4)

with open(f'edge_matrices_similarity_{similarity_value}.json', 'r') as fin:
    all_recipes_edge_matrix = json.load(fin, )
pprint(all_recipes_edge_matrix)