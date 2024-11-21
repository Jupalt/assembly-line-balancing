import logging
from pyomo.environ import *
from pyomo.opt import SolverFactory

class OptimizationModel:
    def __init__(self):
        logging.getLogger('pyomo').setLevel(logging.WARNING)
        self.model = None

    def build_model(self, cycle_time, tasks, station_types, products, task_time_dict, precedence_relations,
                    incompatible_tasks, same_station_pairs, stationtype_compatibility, station_costs):
        """
        Parameters: 
        ----------
        cycle_time : int
            The cycle time of the assembly line.
        tasks : list[int]
            A list of tasks with their IDs.
        station_types : list[str]
            A list of Strings, each representing a different station type.
        products: list[str]
            A list of Strings, each representing one product of the assembly line
        task_time_dict: dict[tuple[int, str], int]
            A dictionary where:
            - The key is a tuple (task_ID, product_ID) indicating the task and product combination
            - The value is the processing time (in integer units) required for the task on the given product
        precedence_relations: list[tuple[int, int]]:
            A list of tuples (g, h) where task g must precede task h
        incompatible_tasks: list[tuple[int, int]]
            A list of tuples (d, f) where tasks d and f cannot be assigned to the same station
        same_station_pairs: list[tuple[int, int]]
            A list of tuples (m, n) where tasks m and n must be assigned to the same station
        stationtype_compatibility: dict[tuple[int, str], int]
            A dictionary where:
            - The key is a tuple (task_ID, station_type) indicating the task and station type combination
            - The value is 1 if the task is compatible with the station type, and 0 otherwise
        station_costs: dict[str, int]
            A dictionary where:
            - The key is a station type (string)
            - The value is the fixed cost (integer) of opening a station of that type
        """
        # Define the model
        model = ConcreteModel()

        # Define upper bound for number of stations
        max_stations = len(tasks)

        # Sets
        model.TASKS = Set(initialize=tasks)
        model.STATIONS = Set(initialize=range(1, max_stations + 1)) # Initialize STATIONS with an upper bound
        model.TYPES = Set(initialize=station_types)
        model.PRODUCTS = Set(initialize=products)
        model.PrecedencePairs = Set(initialize=precedence_relations, within=model.TASKS * model.TASKS)
        model.IncompatiblePairs = Set(initialize=incompatible_tasks, within=model.TASKS * model.TASKS)
        model.SameStationPairs = Set(initialize=same_station_pairs, within=model.TASKS * model.TASKS)

        # Parameters
        model.c = Param(initialize=cycle_time) # Cycle time
        model.t = Param(model.TASKS, model.PRODUCTS, initialize=task_time_dict) # Processing time of a task 
        model.F = Param(model.TASKS, model.TYPES, initialize=stationtype_compatibility, within=Binary)
        model.C = Param(model.TYPES, initialize=station_costs) # Cost for opening a station

        # Decision Variables
        model.x = Var(model.TASKS, model.STATIONS, within=Binary)  # Task assignment
        model.z = Var(model.STATIONS, within=Binary)  # Station open/close
        model.y = Var(model.STATIONS, model.TYPES, within=Binary)  # Station type assignment

        # Objective function
        def objective_rule(model):
            return sum(model.C[k] * model.y[j, k] for j in model.STATIONS for k in model.TYPES)
        model.objective = Objective(rule=objective_rule, sense=minimize)

        # Constraints

        # Task Assignment: Each task is assigned to exactly one station
        def task_assignment_rule(model, i):
            return sum(model.x[i, j] for j in model.STATIONS) == 1
        model.task_assignment = Constraint(model.TASKS, rule=task_assignment_rule)

        # Open Stations: Tasks can only be assigned to open stations
        def open_station_rule(model, i, j):
            return model.x[i, j] <= model.z[j]
        model.open_station = Constraint(model.TASKS, model.STATIONS, rule=open_station_rule)

        # Cycle Time Constraint
        def cycle_time_rule(model, j, p):
            return sum(model.t[i, p] * model.x[i, j] for i in model.TASKS) <= model.c * model.z[j]
        model.cycle_time = Constraint(model.STATIONS, model.PRODUCTS, rule=cycle_time_rule)

        # Precedence Relations
        def precedence_rule(model, g, h):
            return sum(j * model.x[g, j] for j in model.STATIONS) <= sum(j * model.x[h, j] for j in model.STATIONS)
        model.precedence = Constraint(model.PrecedencePairs, rule=precedence_rule)

        # Station Type Assignment: Each station has exactly one type
        def station_type_rule(model, j):
            return sum(model.y[j, k] for k in model.TYPES) == model.z[j]
        model.station_type = Constraint(model.STATIONS, rule=station_type_rule)

        # Station Type Compatibility
        def station_compatibility_rule(model, i, j):
            return model.x[i, j] <= sum(model.F[i, k] * model.y[j, k] for k in model.TYPES)
        model.station_compatibility = Constraint(model.TASKS, model.STATIONS, rule=station_compatibility_rule)

        """
        # First Station Opening: If any station is opened, station 1 must be opened
        def first_station_rule(model):
            return model.z[1] >= sum(model.z[j] for j in model.STATIONS if j > 1)
        model.first_station = Constraint(rule=first_station_rule)

        # Station Opening Priority
        def station_priority_rule(model, b, w):
            return Constraint.Skip if b >= w else model.z[w] <= model.z[b]
        model.station_priority = Constraint(model.STATIONS, model.STATIONS, rule=station_priority_rule)
        """
        
        # Incompatible Tasks
        def incompatible_tasks_rule(model, d, f, j):
            return model.x[d, j] + model.x[f, j] <= 1
        model.incompatible_tasks = Constraint(model.IncompatiblePairs, model.STATIONS, rule=incompatible_tasks_rule)

        # Same Station Tasks
        def same_station_tasks_rule(model, m, n, j):
            return model.x[m, j] == model.x[n, j]
        model.same_station_tasks = Constraint(model.SameStationPairs, model.STATIONS, rule=same_station_tasks_rule)

        self.model = model

    def export_model(self, file_path):
        # Write the model to a mps file
        if self.model is not None:
            self.model.write(file_path)
            print("Model exported successfully.")
        else:
            raise ValueError("Model shouldn't be None.")
        
    def execute_solver(self, solver_name):
        # Solve the model
        solver = SolverFactory(solver_name)
        if not solver.available():
            print(f"{solver_name} solver is not available!")
        else:
            print(f"{solver_name} solver is ready to use!")
            results = solver.solve(self.model)
            self._write_results(results)

    def _write_results(self, results):
        station_results = {}

        # Iterate over all stations
        for j in self.model.STATIONS:
            if self.model.z[j].value == 1:  # Station is open
                # Find the assigned station type
                station_type = None
                for k in self.model.TYPES:
                    if self.model.y[j, k].value == 1:  # Station type is assigned
                        station_type = k
                        break

                # Find the tasks assigned to this station
                assigned_tasks = [
                    i for i in self.model.TASKS if self.model.x[i, j].value == 1
                ]

                # Store the results for this station
                station_results[j] = {
                    "station_type": station_type,
                    "assigned_tasks": assigned_tasks,
                }

        # Print results
        count = 1
        for station_index, info in station_results.items():
            print(
                f"Station {count} with type {info['station_type']}: {info['assigned_tasks']}"
            ) 
            count += 1      
