import logging
from pyomo.environ import *

class OptimizationModel:
    def __init__(self):
        logging.getLogger('pyomo').setLevel(logging.WARNING)
        self.model = None

    def build_model(self, cycle_time, tasks, precedence_relations, station_types, stationtype_compatibility, costs, incompatible_tasks, compatible_tasks):
        """
        Parameters: 
        ----------
        cycle_time : int
            The cycle time of the assembly line.
        tasks : list[{task_id: int, task_time: int}]
            A list of tasks with their IDs and times.
        precedence_relations : list[tuple]
            A list of tuples with precedence relations between tasks.
        station_types : list[str]
            A list of Strings, each representing a different station type.
        stationtype_compatibility : dict
            A matrix with the information which tasks can be performed on which station types
        costs : dict{station_type: int}
            A dictionary with the costs for opening a station with a certain type.
        """
        num_tasks = len(tasks)

        # Create Pyomo model
        model = ConcreteModel()

        model.STATIONS = RangeSet(num_tasks) 
        model.TASKS = RangeSet(num_tasks)
        model.STATION_TYPES = Set(initialize=station_types)
        # NOTE: Update the tasks to task_per_product
        model.PRODUCTS = RangeSet(len(tasks))

        model.C = Param(model.STATION_TYPES, initialize=costs)
        model.F = Param(model.Tasks, model.STATION_TYPES, initialize=stationtype_compatibility)
        model.c = Param(initialize=cycle_time)

        # Variables
        # x[i, k]: 1 if task i is assigned to station j
        model.x = Var(model.TASKS, model.STATIONS, domain=Binary)
        # y[j, k]: 1 if station j with stationtype k is used
        model.y = Var(model.STATIONS, model.STATION_TYPES, domain=Binary)

        # ---- OBJECTIVE FUNCTION ----
        def objective_rule(model):
            return sum(model.C[k] * model.y[j, k] for j in model.STATIONS for k in model.STATION_TYPES)

        model.objective = Objective(rule=objective_rule, sense=minimize)

        # ---- CONSTRAINTS ----
        # 1. Each task is assigned to exactly one station
        def task_assignment_rule(model, i):
            return sum(model.x[i, j] for j in model.STAIONS) == 1

        model.task_assignment = Constraint(model.TASKS, rule=task_assignment_rule)

        # 2. Cycle time constraint
        def cycle_time_rule(model, j):
            return sum(model.t[i] * model.x[i, j] for i in model.TASKS) <= model.c

        model.cycle_time = Constraint(model.STATIONS, rule=cycle_time_rule)

        # 3. Task-station compatibility
        def compatibility_rule(model, i, j):
            return model.x[i, j] <= sum(model.F[i, k] * model.y[j, k] for k in model.TYPES)

        model.compatibility = Constraint(model.TASKS, model.STATIONS, rule=compatibility_rule)

        # 4. Each station can have at most one type
        def station_type_rule(model, j):
            return sum(model.y[j, k] for k in model.STATION_TYPES) <= 1

        model.station_type = Constraint(model.STATIONS, rule=station_type_rule)

        # 5. Tasks can only be assigned if the station is opened
        def open_station_rule(model, i, j):
            return model.x[i, j] <= sum(model.y[j, k] for k in model.STATION_TYPES)
        
        model.open_station = Constraint(model.TASKS, model.STATIONS, rule=open_station_rule)

        # 6. Precedence constraint (task i must be completed before task j)
        def precedence_rule(model, i, j):
            return sum(k * model.x[i, k] for k in model.STATIONS) <= sum(m * model.x[j, m] for m in model.STATIONS)
        
        model.precedence = Constraint(precedence_relations, rule=precedence_rule)

        # 7. Incompatible rule (Task i can't be on the same station as task j)
        def incompatible_task_rule(model, i, j, k):
            return model.x[i, k] + model.x[j, k] <= 1
        
        model.incompatible_task = Constraint(incompatible_tasks, model.STATIONS, rule=incompatible_task_rule)

        # 8. Compatible_task_rule (Task i must be on the same station as task j)
        def compatible_task_rule(model, i, j):
            return sum((model.x[i, k] * model.x[j, k]) for k in model.STATIONS) == 1
        
        model.compatible_task = Constraint(compatible_tasks, rule=compatible_task_rule)


