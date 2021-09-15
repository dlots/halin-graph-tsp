from HalinGraphTspSolver import HalinGraphTspSolver
from GraphUtils import generate_weighted_halin_graph, draw_weighted_graph, draw_graph
from networkx.algorithms.planarity import check_planarity
from networkx.algorithms.approximation import traveling_salesman_problem
import itertools


def naive_tsp(graph):
    permutations = [list(i) for i in itertools.permutations(graph.nodes)]
    min_cost = 99999
    min_cycle = None
    for path in permutations:
        path.append(path[0])
        cost = 0
        path_exists = True
        for i in range(len(path) - 1):
            try:
                cost += graph[path[i]][path[i + 1]]['weight']
            except KeyError:
                path_exists = False
        if not path_exists:
            continue
        if cost < min_cost:
            min_cost = cost
            min_cycle = path
    return min_cycle, min_cost


def find_cycle_in_halin_graph(graph):
    cycle = []
    is_planar, PE = check_planarity(graph)
    draw_weighted_graph(graph)
    for edge in PE.edges:
        face = PE.traverse_face(*edge)
        if len(face) > len(cycle):
            cycle = face
    return cycle


if __name__ == '__main__':
    G, T = generate_weighted_halin_graph()
    #print(find_cycle_in_halin_graph(G))
    draw_graph(T)
    draw_graph(G)
    #draw_weighted_graph(T)
    #draw_weighted_graph(G)
    #solver = HalinGraphTspSolver(G, T)
    #print(naive_tsp(G))
    #print(solver.solve())
