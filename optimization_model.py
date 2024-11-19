import logging
from pyomo.environ import ConcreteModel, Var, Objective, Constraint, RangeSet, SolverFactory, Binary, minimize

class OptimizationModel:
    def __init__(self):
        logging.getLogger('pyomo').setLevel(logging.WARNING)
        self.model = None

    def build_model(self, cycle_time, num_tasks, tasks_per_product, precedence_relations, incompatible_tasks, compatible_tasks):
        # Create Pyomo model
        model = ConcreteModel()
        model.Products = RangeSet(len(tasks_per_product))
        model.Stations = RangeSet(num_tasks) 
        model.Tasks = RangeSet(num_tasks)

        # Variables
        # x[i, k]: 1 if task i is assigned to station k
        model.x = Var(model.Tasks, model.Stations, within=Binary)
        # y[k]: 1 if station k is used
        model.y = Var(model.Stations, within=Binary)

        # Ziel: Minimierung der genutzten Stationen
        model.obj = Objective(expr=sum(model.y[k] for k in model.Stations), sense=minimize)

        # 1. Jede Aufgabe muss an genau eine Station zugewiesen werden
        def task_assignment_rule(model, i):
            return sum(model.x[i, k] for k in model.Stations) == 1
        model.task_assignment = Constraint(model.Tasks, rule=task_assignment_rule)

        # 2. Cycle time constraint per station
        def cycle_time_rule(model, p, k):
            # Hier wird die Cycle-Time-Beschränkung für Produkt p und Station k festgelegt
            return sum(tasks_per_product[p - 1][i] * model.x[i, k] for i in model.Tasks) <= cycle_time * model.y[k]
        model.cycle_time_constraint = Constraint(model.Products, model.Stations, rule=cycle_time_rule)

        # 3. Precedence constraint (task i must be completed before task j)
        def precedence_rule(model, i, j):
            return sum(k * model.x[i, k] for k in model.Stations) <= sum(m * model.x[j, m] for m in model.Stations)
        model.precedence_constraint = Constraint(precedence_relations, rule=precedence_rule)

        # 4. Incompatible rule (Task i can't be on the same station as task j)
        def incompatible_task_rule(model, i, j, k):
            return model.x[i, k] + model.x[j, k] <= 1
        model.incompatible_task_constraint = Constraint(incompatible_tasks, model.Stations, rule=incompatible_task_rule)

        # 5. Compatible_task_rule (Task i must be on the same station as task j)
        def compatible_task_rule(model, i, j):
            return sum((model.x[i, k] * model.x[j, k]) for k in model.Stations) == 1
        model.compatible_task_constraint = Constraint(compatible_tasks, rule=compatible_task_rule)

        return model

    def save_to_mps(self, model, file_path):
        # Write the model to a mps file
        model.write(file_path)