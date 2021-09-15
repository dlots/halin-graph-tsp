from GraphUtils import draw_weighted_graph


class StoredFan:
    def __init__(self, fan, center_edge, side_edge_0, side_edge_1, center_edge_cost, side_edge_0_cost, side_edge_1_cost,
                 cycle_edges, min_delta_edge):
        self.fan = fan
        self.center_edge = center_edge
        self.side_edge_0 = side_edge_0
        self.side_edge_1 = side_edge_1
        self.center_edge_cost = center_edge_cost
        self.side_edge_0_cost = side_edge_0_cost
        self.side_edge_1_cost = side_edge_1_cost
        self.cycle_edges = cycle_edges
        self.min_delta_edge = min_delta_edge


class HalinGraphTspSolver:
    def __init__(self, graph, tree, center_node=0):
        self.graph = graph
        self.tree = tree
        self.center_node = center_node
        self.fan_list = []
        self.path = []
        self.path_length = 0
        self.debug_counter = 0
        self.solution = None
        self.solution_cost = 0

    def get_edge_cost(self, edge):
        return self.graph[edge[0]][edge[1]]['weight']

    def cost_two_side_edges_path(self, cycle_cost, cycle_edges, fan_center):
        min_delta = 99999
        min_delta_edge = None
        for edge in cycle_edges:
            delta = self.get_edge_cost((edge[0], fan_center)) + self.get_edge_cost((fan_center, edge[1])) \
                    - self.get_edge_cost(edge)
            if delta < min_delta:
                min_delta = delta
                min_delta_edge = edge
        return cycle_cost + min_delta, min_delta_edge

    def cost_center_and_side_edge_path(self, cycle_cost, fan_center, opposite_side_edge):
        return cycle_cost + self.get_edge_cost((opposite_side_edge[0], fan_center))

    def shrink_fan(self, fan_center, fan_center_parent):
        leaves = [node for node in self.graph.neighbors(fan_center) if node != fan_center_parent]
        current_fan = self.graph.subgraph([fan_center] + leaves).copy()

        side_edges = []
        counter = 0
        for i in range(-1, len(leaves) - 1):
            for adj in self.graph.neighbors(leaves[i]):
                if adj not in current_fan:
                    side_edges.append((leaves[i], adj))
                    counter += 1
                if counter > 1:
                    break
            if counter > 1:
                break

        cycle_edges = [edge for edge in current_fan.edges if fan_center not in edge]
        cycle_cost = 0
        for edge in cycle_edges:
            cycle_cost += self.get_edge_cost(edge)

        cost_of_path_through_center_and_side_0 = self.cost_center_and_side_edge_path(cycle_cost, fan_center,
                                                                                     opposite_side_edge=side_edges[1])

        cost_of_path_through_center_and_side_1 = self.cost_center_and_side_edge_path(cycle_cost, fan_center,
                                                                                     opposite_side_edge=side_edges[0])

        cost_of_path_through_side_edges, min_delta_edge = self.cost_two_side_edges_path(cycle_cost, cycle_edges, fan_center)

        new_cost_side_0 = self.get_edge_cost(side_edges[0]) \
                          + (cost_of_path_through_side_edges + cost_of_path_through_center_and_side_0
                             - cost_of_path_through_center_and_side_1) / 2

        new_cost_side_1 = self.get_edge_cost(side_edges[1]) \
                          + (cost_of_path_through_side_edges + cost_of_path_through_center_and_side_1
                             - cost_of_path_through_center_and_side_0) / 2

        new_cost_center = self.get_edge_cost((fan_center, fan_center_parent)) \
                          + (cost_of_path_through_center_and_side_0 + cost_of_path_through_center_and_side_1
                             - cost_of_path_through_side_edges) / 2

        self.fan_list.append(StoredFan(current_fan, (fan_center, fan_center_parent), side_edges[0], side_edges[1],
                                       self.get_edge_cost((fan_center, fan_center_parent)),
                                       self.get_edge_cost(side_edges[0]), self.get_edge_cost(side_edges[1]),
                                       cycle_edges, min_delta_edge))

        for leaf in leaves:
            self.graph.remove_node(leaf)

        self.graph.add_edge(fan_center, side_edges[0][1], weight=new_cost_side_0)
        self.graph.add_edge(fan_center, side_edges[1][1], weight=new_cost_side_1)
        self.graph[fan_center][fan_center_parent]['weight'] = new_cost_center

        # if self.debug_counter == 0:
        #     draw_weighted_graph(self.graph)
        #     self.debug_counter += 1

    def restore_fan(self):
        #draw_weighted_graph(self.graph)
        stored_fan = self.fan_list.pop()

        for node in stored_fan.fan:
            if node != stored_fan.center_edge[0]:
                self.graph.add_node(node)
        for edge in stored_fan.fan.edges:
            self.graph.add_edge(*edge, weight=stored_fan.fan[edge[0]][edge[1]]['weight'])

        center_edge = stored_fan.center_edge
        side_edge_0 = stored_fan.side_edge_0
        side_edge_1 = stored_fan.side_edge_1

        self.graph[center_edge[0]][center_edge[1]]['weight'] = stored_fan.center_edge_cost
        fake_side_edge_0 = (center_edge[0], side_edge_0[1])
        fake_side_edge_1 = (center_edge[0], side_edge_1[1])
        self.graph.remove_edge(*fake_side_edge_0)
        self.graph.remove_edge(*fake_side_edge_1)
        self.graph.add_edge(*side_edge_0, weight=stored_fan.side_edge_0_cost)
        self.graph.add_edge(*side_edge_1, weight=stored_fan.side_edge_1_cost)

        center_edge_in_solution = False
        side_edge_0_in_solution = False
        side_edge_1_in_solution = False
        fake_edge_indices = []

        for edge_index, edge in enumerate(self.solution):
            if center_edge == edge or center_edge[::-1] == edge:
                center_edge_in_solution = True
            if fake_side_edge_0 == edge or fake_side_edge_0[::-1] == edge:
                side_edge_0_in_solution = True
                fake_edge_indices.append(edge_index)
            if fake_side_edge_1 == edge or fake_side_edge_1[::-1] == edge:
                side_edge_1_in_solution = True
                fake_edge_indices.append(edge_index)
            if center_edge_in_solution + side_edge_0_in_solution + side_edge_1_in_solution == 2:
                break

        fake_edge_indices[0] += 1
        for fake_edge_index in fake_edge_indices:
            fake_edge_index -= 1
            del self.solution[fake_edge_index]

        if center_edge_in_solution:
            for cycle_edge in stored_fan.cycle_edges:
                self.solution.append(cycle_edge)
            if side_edge_0_in_solution:
                self.solution.append((center_edge[0], side_edge_1[0]))
                self.solution.append(side_edge_0)
            else:
                self.solution.append((center_edge[0], side_edge_0[0]))
                self.solution.append(side_edge_1)
        else:
            for cycle_edge in stored_fan.cycle_edges:
                if cycle_edge == stored_fan.min_delta_edge or cycle_edge[::-1] == stored_fan.min_delta_edge:
                    self.solution.append((stored_fan.min_delta_edge[0], center_edge[0]))
                    self.solution.append((center_edge[0], stored_fan.min_delta_edge[1]))
                else:
                    self.solution.append(cycle_edge)
            self.solution.append(side_edge_0)
            self.solution.append(side_edge_1)

    def solve_tsp_for_wheel(self):
        self.solution = [edge for edge in self.graph.edges if self.center_node not in edge]
        min_delta = float('inf')
        min_delta_edge = None
        for edge in self.solution:
            delta = self.get_edge_cost((edge[0], self.center_node)) + self.get_edge_cost((self.center_node, edge[1])) \
                    - self.get_edge_cost(edge)
            if delta < min_delta:
                min_delta = delta
                min_delta_edge = edge
        self.solution.remove(min_delta_edge)
        self.solution.append((min_delta_edge[0], self.center_node))
        self.solution.append((self.center_node, min_delta_edge[1]))

    def solve_tsp_recursively(self, current_node, current_node_parent=-1):
        leaf = True
        for child in self.tree.neighbors(current_node):
            if child == current_node_parent:
                continue
            leaf = False
            child_is_leaf = self.solve_tsp_recursively(child, current_node)
            if child_is_leaf:
                break

        if leaf:
            return leaf
        elif current_node != self.center_node:
            self.shrink_fan(current_node, current_node_parent)
        else:
            #draw_weighted_graph(self.graph)
            self.solve_tsp_for_wheel()
        return leaf

    def solve(self):
        self.solve_tsp_recursively(self.center_node)
        while len(self.fan_list) > 0:
            self.restore_fan()
        #draw_weighted_graph(self.graph)
        for edge in self.solution:
            self.solution_cost += self.graph[edge[0]][edge[1]]['weight']
        return self.solution, self.solution_cost

