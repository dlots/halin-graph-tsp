from HalinGraphTspSolver import HalinGraphTspSolver
from GraphUtils import generate_weighted_halin_graph, draw_weighted_graph, draw_graph, find_cycle_in_halin_graph
from GraphUtils import nx_to_adj_list
from networkx.algorithms.approximation import traveling_salesman_problem
import itertools
import time
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
from math import exp

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


if __name__ == '__main__':
    solver = HalinGraphTspSolver()
    G, T = generate_weighted_halin_graph(nodes=7)
    draw_graph(G)
    print(nx_to_adj_list(G))
    ns = []
    times = []
    if False:
        for n in range(4, 11):
            G, T = generate_weighted_halin_graph(nodes=n)
            # draw_graph(T)
            # draw_graph(G)
            #draw_weighted_graph(T)
            #draw_weighted_graph(G)
            if not G:
                continue
            num_edges = G.number_of_edges()
            solver.set_graph(G, T)
            start = time.time()
            naive_tsp(G)
            elapsed = time.time() - start
            #ns.append(n)
            ns.append(num_edges)
            times.append(elapsed)
            #print(n, elapsed)
            print(n, num_edges, elapsed)
        #plt.show()
        ns_exp = [exp(n) for n in ns]
        to_normalize = [times, ns_exp]
        normalized = normalize(to_normalize)
        plt.plot(ns, times, color='red')
        plt.show()
        plt.plot(ns, ns_exp, color='green')
        plt.show()
        plt.plot(ns, normalized[0], color='red')
        plt.plot(ns, normalized[1], color='green')
        plt.show()
    if False:
        for n in range(4, 6000, 100):
            G, T = generate_weighted_halin_graph(nodes=n)
            # draw_graph(T)
            # draw_graph(G)
            #draw_weighted_graph(T)
            #draw_weighted_graph(G)
            if not G:
                continue
            num_edges = G.number_of_edges()
            solver.set_graph(G, T)
            start = time.time()
            #find_cycle_in_halin_graph(G)
            result = solver.solve()
            elapsed = time.time() - start
            #ns.append(n)
            ns.append(num_edges)
            times.append(elapsed)
            #print(n, elapsed)
            print(n, num_edges, elapsed)
        #plt.show()
        ns_square = [n*n for n in ns]
        to_normalize = [times, ns_square]
        normalized = normalize(to_normalize)
        plt.plot(ns, times, color='red')
        plt.show()
        plt.plot(ns, ns_square, color='green')
        plt.show()
        plt.plot(ns, normalized[0], color='red')
        plt.plot(ns, normalized[1], color='green')
        plt.show()
    #print(find_cycle_in_halin_graph(G))

    #print(naive_tsp(G))
    #print(solver.solve())
