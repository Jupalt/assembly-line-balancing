import networkx as nx

class Graph:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_edges(self, edges):
        self.G.add_edges_from(edges)

    def get_subgraph(self, nodes):
        return self.G.subgraph(nodes).copy()
    
    def get_edges_of_subgraph_with_paths(self, nodes):
        relevant_edges = []
        for start_node in nodes:
            for end_node in nodes:
                if start_node != end_node:
                    try:
                        # Find all paths from start_node to end_node
                        for path in nx.all_simple_paths(self.G, source=start_node, target=end_node):
                            # Add edges from the path
                            relevant_edges.extend([(path[i], path[i + 1]) for i in range(len(path) - 1)])
                    except:
                        # If no path exists, skip to the next pair
                        continue
        relevant_edges = list(set(relevant_edges))
        return relevant_edges

    def get_nodes_with_predecessors_and_successors(self):
        return [
            node for node in self.G.nodes if list(self.G.predecessors(node)) and list(self.G.successors(node))
        ]

    def is_predecessor(self, node, potential_predecessor):
        return self.G.has_edge(potential_predecessor, node)