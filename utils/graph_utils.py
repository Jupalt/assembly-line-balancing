import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv
from networkx.drawing.nx_agraph import graphviz_layout
import logging
import os

# Set the log level of matplotlib to WARNING
logging.getLogger('matplotlib').setLevel(logging.WARNING)

def validate_graph(edges):
    """
    Validates the input data

    Args:
        precedence_relations (list of tuples): Precedence relations between tasks.
    
    Raises:
        ValueError: If precedence relations contain a cycle.
    """
    
    # Check if precedence_relations has a cycle
    if _has_cycle(edges):
        raise ValueError("Graph has a cycle.")
    else:
        print("Passed.")

def _has_cycle(edges):
    # Creates a graph based on precedence_relations
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # Check if there's a cycle in the graph
    for cycle in nx.simple_cycles(G):
        print("Cycle found -> ", cycle)
        return True
    
    return False # No cycle found

def visualize_graph(edges, visualizer="graphviz"):
    # Create a directed graph using NetworkX
    G = nx.DiGraph()
    G.add_edges_from(edges)

    graph_file_path = os.path.join("result_data", "precedence_graph.png")

    if visualizer == "matplotlib":
        _visualize_using_matplotlib(G, graph_file_path)
    elif visualizer == "graphviz":
        _visualize_using_graphviz(G, graph_file_path)

def _visualize_using_matplotlib(graph, graph_file_path):
    # Visualizing the graph
    plt.figure(figsize=(8, 6))
    nx.draw(graph, with_labels=True, node_size=700, node_color="skyblue", font_size=12, font_weight="bold", arrows=True)
    
    # Save the figure to the file
    plt.savefig(graph_file_path)

    plt.close()

def _visualize_using_graphviz(graph, graph_file_path):
    # Use Graphviz layout for a hierarchical structure
    pos = graphviz_layout(graph, prog='dot', args='-Grankdir=LR')


    node_colors = ['#0E9682'] * len(graph.nodes)
    nx.draw(graph, pos, with_labels=True, arrows=True, node_color=node_colors)

    # Save the figure to the file
    plt.savefig(graph_file_path)

    plt.close()
