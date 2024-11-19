from pyscipopt import Model
import os
from collections import defaultdict
import write_assignments

class SolverSCIP:
    def __init__(self, num_tasks, precedence_relations):
        self.max_num_stations = num_tasks
        self.precedence_relations = precedence_relations

    def solve(self, file_path):
        # Check if filename is a valid MPS file
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File '{file_path}' wasn't found.")
        elif not file_path.lower().endswith('.mps'):
            raise ValueError(f"File '{file_path}' is not an mps-file.")

        print("Using SCIP to solve the model...")
        # Call solver
        station_task_dict = self.run_scip_optimizer(file_path)
        write_assignments.write_results(station_task_dict, self.precedence_relations)


    def run_scip_optimizer(self, file_path):
        model = Model()
        model.readProblem(file_path)
        model.optimize()

        print("SCIP Status: ", model.getStatus())
        station_task_dict = self.create_station_task_dict(model)
        return station_task_dict


    def create_station_task_dict(self, model):
        # Dictionary für die Stationen und zugeordneten Aufgaben
        station_task_dict = defaultdict(list)

        # Durchlaufe alle Variablen und überprüfe, ob sie zu einer Station und Aufgabe gehören
        for task in range(self.max_num_stations):
            for station in range(self.max_num_stations):
                index = task * self.max_num_stations + station  # Calculate Index
                value = model.getVal(model.getVars()[index])
                rounded_value = round(value)
                if rounded_value == 1:
                    station_task_dict[station + 1].append(task + 1)

        return station_task_dict