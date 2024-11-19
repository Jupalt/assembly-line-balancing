import networkx as nx

def write_results(station_task_dict, precedence_relations):
    sorted_dict = sort_tasks_in_stations(station_task_dict, precedence_relations)
    print_task_assignments(sorted_dict)


def sort_tasks_in_stations(station_task_dict, precedence_relations):
    # Erstelle einen gerichteten Graphen basierend auf den precedence_relations
    G = nx.DiGraph()
    G.add_edges_from(precedence_relations)

    # Durchlaufe jede Station und sortiere die Aufgaben
    for station, tasks in station_task_dict.items():
        items_in_graph = [task for task in tasks if task in G.nodes]
        items_not_in_graph = [task for task in tasks if task not in G.nodes]

        subgraph = G.subgraph(items_in_graph)
        # Wenn keine Aufgaben in der aktuellen Station sind, überspringe die Station
        sorted_items = list(nx.topological_sort(subgraph))

        sorted_list = []
        for item in tasks:
            if item in items_in_graph:
                sorted_list.append(sorted_items.pop(0))  # Füge die sortierten Items hinzu
            else:
                sorted_list.append(item)

        # Sortiere die Aufgaben der Station nach der Reihenfolge
        station_task_dict[station] = sorted_list

    return station_task_dict

def print_task_assignments(station_task_dict):
    sorted_station_keys = sorted(station_task_dict.keys())

    print("\nTask Assignment Summary:")
    for idx, station in enumerate(sorted_station_keys, start=1):
        # Get the tasks for this station
        tasks = station_task_dict[station]
        # Output the station with the new name (Station 1, Station 2, etc.)
        print(f"Station {idx}: {tasks}")