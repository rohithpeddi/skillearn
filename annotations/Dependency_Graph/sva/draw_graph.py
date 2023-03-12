import json
from pprint import pprint
import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
similarity_value = 0.70
with open(f'edge_matrices_similarity_{similarity_value}.json', 'r') as fin:
    all_recipes_edge_matrix = json.load(fin, )
pprint(all_recipes_edge_matrix)


def get_adjaceny_matrix(edge_matrix, num_steps):
    matrix = np.zeros((num_steps, num_steps))
    for idx_1 in range(edge_matrix.shape[0]):
        if edge_matrix[idx_1, 0] == 0 and edge_matrix[idx_1, 1] == 0:
            continue
        matrix[edge_matrix[idx_1, 0] - 1, edge_matrix[idx_1, 1] - 1] = 1
    return matrix


def show_graph_with_labels(adjacency_matrix, mylabels, recipe_name):
    rows, cols = np.where(adjacency_matrix == 1)
    edges = zip(rows.tolist(), cols.tolist())
    gr = nx.DiGraph()
    gr.add_edges_from(edges)
    gr = nx.relabel_nodes(gr, mylabels)
    nx.draw_planar(gr, with_labels=True,
                        arrowsize = 12,
                        node_size = 800,
                        node_color = "#ffff8f",
                        linewidths = 2.0,
                        width = 1.5,
                        font_size = 14,)

    # plt.show()
    plt.savefig(f"graphs_{similarity_value}/{recipe_name}.png")
    plt.close()

for each_recipe in all_recipes_edge_matrix:
    edge_matrix = np.array(all_recipes_edge_matrix[each_recipe]).astype(int)
    print(edge_matrix)
    from pathlib import Path
    Path(f"graphs_{similarity_value}").mkdir(parents=True, exist_ok=True)
    adj_matrix = get_adjaceny_matrix(edge_matrix, len(edge_matrix) + 1)
    show_graph_with_labels(adj_matrix, {i-1: i for i in range(1, len(edge_matrix) + 1)}, each_recipe)