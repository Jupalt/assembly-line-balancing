import networkx as nx

# Create a directed graph
G = nx.DiGraph()
G.add_edges_from([(1, 2), (2, 3)])
nodes = [1, 3]

relevant_edges = []
for start_node in nodes:
    for end_node in nodes:
        if start_node != end_node:
            for path in nx.all_simple_paths(G, source=start_node, target=end_node):
                relevant_edges.extend([(path[i], path[i + 1]) for i in range(len(path) - 1)])
relevant_edges = list(set(relevant_edges))

print(relevant_edges)

