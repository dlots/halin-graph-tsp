import matplotlib.pyplot as plt
from networkx.generators.classic import full_rary_tree
from networkx import draw, draw_planar
from networkx import get_edge_attributes
from networkx import draw_networkx_edge_labels, spring_layout, planar_layout
from networkx.algorithms import check_planarity
from random import randint


def generate_weighted_halin_graph(r=3, nodes=10, min_weight=1, max_weight=10):
    tree = full_rary_tree(r, nodes)
    last_node = len(tree) - 1
    last_node_parent = next(tree.neighbors(last_node))
    if tree.degree(last_node_parent) == 2:
        return None, None

    graph = tree.copy()

    leaves = [node for node in graph.nodes() if graph.degree(node) == 1]
    first_in_cycle = -1
    last_in_group = -1

    for edge in tree.edges():
        weight = randint(min_weight, max_weight)
        graph[edge[0]][edge[1]]['weight'] = weight
        tree[edge[0]][edge[1]]['weight'] = weight

    for leaf in leaves:
        parent = next(graph.neighbors(leaf))
        siblings = [node for node in graph.neighbors(parent) if graph.degree(node) == 1]

        if first_in_cycle == -1:
            first_in_cycle = siblings[0]

        if last_in_group != -1:
            graph.add_edge(last_in_group, siblings[0])
            weight = randint(min_weight, max_weight)
            graph[last_in_group][siblings[0]]['weight'] = weight

        last_in_group = siblings[-1]
        leaves.remove(last_in_group)

        for leaf_index in range(len(siblings) - 1):
            sibling = siblings[leaf_index]
            next_sibling = siblings[leaf_index + 1]
            if leaf != sibling:
                leaves.remove(sibling)
            graph.add_edge(sibling, next_sibling)
            weight = randint(min_weight, max_weight)
            graph[sibling][next_sibling]['weight'] = weight

    graph.add_edge(last_in_group, first_in_cycle)
    weight = randint(min_weight, max_weight)
    graph[last_in_group][first_in_cycle]['weight'] = weight

    return graph, tree


def find_cycle_in_halin_graph(graph):
    cycle = []
    is_planar, PE = check_planarity(graph)
    #draw_weighted_graph(graph)
    for edge in PE.edges:
        face = PE.traverse_face(*edge)
        if len(face) > len(cycle):
            cycle = face
    return cycle


def print_adjacency_list(graph):
    for node in graph:
        print(node, end=': ')
        for adj in graph.adj[node]:
            print(adj, end=',')
        print()


def nx_to_adj_list(graph):
    adj_list = []
    for node in graph:
        adj_list.append([])
        for adj in graph.adj[node]:
            adj_list[node].append([adj, graph[node][adj]['weight']])
    return adj_list


def draw_weighted_graph(graph):
    pos = planar_layout(graph)
    draw_planar(graph, with_labels=True)
    weights = get_edge_attributes(graph, 'weight')
    draw_networkx_edge_labels(graph, pos, weights)
    plt.show()


def draw_graph(graph):
    draw(graph, with_labels=True)
    plt.show()
