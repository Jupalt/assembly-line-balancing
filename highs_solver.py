import highspy
from collections import defaultdict
import os
import networkx as nx

class SolverHiGHS:
    def __init__(self, num_tasks, precedence_relations):
        self.max_num_stations = num_tasks
        self.precedence_relations = precedence_relations

    def solve(self, file_path):
        # Check if filename is a valid MPS file
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File '{file_path}' wasn't found.")
        elif not file_path.lower().endswith('.mps'):
            raise ValueError(f"File '{file_path}' is not an mps-file.")

        print("Using HiGHS to solve the model...")
        # Call solver
        self.run_highs_optimizer(file_path)

    # Uses the Open-Source-Library to solve the problem
    def run_highs_optimizer(self, file_path):
        h = highspy.Highs()
        h.readModel(file_path)
        h.run()
        solution = h.getSolution()
        model_status = h.getModelStatus()
        print('Model status = ', h.modelStatusToString(model_status))

        station_task_dict = self.create_station_task_dict(solution)

        # Sorts the tasks of a station according to precedence relations
        sorted_station_task_dict = self.sort_tasks_in_stations(station_task_dict)

        self.print_task_assignments(sorted_station_task_dict)

    def create_station_task_dict(self, solution):
        station_task_dict = defaultdict(list)
        # Iterate through tasks and stations
        for task in range(self.max_num_stations):
            for station in range(self.max_num_stations):
                index = task * self.max_num_stations + station  # Calculate Index
                value = solution.col_value[index]
                rounded_value = round(value)
                if rounded_value == 1:
                    station_task_dict[station + 1].append(task + 1)  # Add station and task to dictionary

        return station_task_dict
    
    def sort_tasks_in_stations(self, station_task_dict):
        # Erstelle einen gerichteten Graphen basierend auf den precedence_relations
        G = nx.DiGraph()
        G.add_edges_from(self.precedence_relations)

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

    def print_task_assignments(self, station_task_dict):
        sorted_station_keys = sorted(station_task_dict.keys())

        print("\nTask Assignment Summary:")
        for idx, station in enumerate(sorted_station_keys, start=1):
            # Get the tasks for this station
            tasks = station_task_dict[station]
            # Output the station with the new name (Station 1, Station 2, etc.)
            print(f"Station {idx}: {tasks}")