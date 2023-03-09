import json
from pprint import pprint
import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

with open('edge_matrices.json', 'r') as fin:
    all_recipes_edge_matrix = json.load(fin, )
pprint(all_recipes_edge_matrix)


def get_adjaceny_matrix(edge_matrix, num_steps):
    matrix = np.zeros((num_steps, num_steps))
    for idx_1 in range(edge_matrix.shape[0]):
        if edge_matrix[idx_1, 0] == 0 and edge_matrix[idx_1, 1] == 0:
            continue
        matrix[edge_matrix[idx_1, 0], edge_matrix[idx_1, 1]] = 1
    return matrix


def show_graph_with_labels(adjacency_matrix, mylabels, recipe_name):
    rows, cols = np.where(adjacency_matrix == 1)
    edges = zip(rows.tolist(), cols.tolist())
    gr = nx.DiGraph()
    gr.add_edges_from(edges)
    nx.draw(gr, node_size=500, with_labels=True)
    # plt.show()
    plt.savefig(f"graphs/{recipe_name}.png")
    plt.close()

for each_recipe in all_recipes_edge_matrix:
    edge_matrix = np.array(all_recipes_edge_matrix[each_recipe]).astype(int)
    print(edge_matrix)
    adj_matrix = get_adjaceny_matrix(edge_matrix, len(edge_matrix) + 1)
    show_graph_with_labels(adj_matrix, [i for i in range(1, len(edge_matrix) + 1)], each_recipe)