from HalinGraphTspSolver import HalinGraphTspSolver
from GraphUtils import generate_weighted_halin_graph, draw_weighted_graph


if __name__ == '__main__':
    G, T = generate_weighted_halin_graph()
    draw_weighted_graph(T)
    draw_weighted_graph(G)
    solver = HalinGraphTspSolver(G, T)
    solver.solve()

