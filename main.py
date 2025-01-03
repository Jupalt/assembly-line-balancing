import logging

import read_data
import utils.validate_input as validator

from model_with_stationtypes import OptimizationModel
from highs_solver import SolverHiGHS
from scip_solver import SolverSCIP
from utils.graph_utils import validate_graph, visualize_graph


INPUT_DATA_PATH = "data/input.xlsx"
MPS_FILE_PATH = "result_data/alb_model.mps"
NUMBER_OF_SOLUTIONS = 1

def main():
    # Sets the log level to DEBUG to display all logs from DEBUG level and above.
    logging.basicConfig(level=logging.DEBUG)

    # Tries to read input data from the INPUT_DATA_PATH Excel file.
    data_input = read_data.read_input_from_excel(INPUT_DATA_PATH)

    precedence_relations = data_input["precedence_relations"]
    num_tasks = data_input["num_tasks"]
    tasks = data_input["tasks"]
    cycle_time_dict = data_input["cycle_time_dict"]
    product_names = data_input["product_names"]
    task_time_dict = data_input["task_time_dict"]
    stationtype_compatibility = data_input["stationtype_compatibility"]
    incompatible_tasks = data_input["incompatible_tasks"]
    compatible_tasks = data_input["compatible_tasks"]
    station_types = data_input["station_types"]
    station_costs = data_input["station_costs"]

    print(f"Cycle time dict: {cycle_time_dict}")

    # Checks if precedence_relations is valid, e.g. if it contains a cycle
    print("Precedence relations validation: ", end="")
    validate_graph(precedence_relations)

    # validator.validate_input(task_time_dict, compatible_tasks, incompatible_tasks, precedence_relations, cycle_time)

    # Visualizes the precedence relations as a graph
    visualize_graph(precedence_relations)

    # Builds the model
    model = OptimizationModel()
    
    model.build_model(cycle_time_dict, tasks, station_types, product_names, task_time_dict, precedence_relations,
                      incompatible_tasks, compatible_tasks, stationtype_compatibility, station_costs)
    print("Solution 1: ")
    model.execute_solver("gurobi")

    """
    model.export_model(MPS_FILE_PATH)
    
    if solver == "HiGHS":
        # Initialize the solver
        highs_solver = SolverHiGHS(num_tasks, precedence_relations)

        # Solve the model with HiGHS
        highs_solver.solve(MPS_FILE_PATH)

    elif solver == "SCIP":
        # Initialize the solver
        scip_solver = SolverSCIP(num_tasks, precedence_relations)

        # Solve the model with SCIP
        scip_solver.solve(MPS_FILE_PATH)

    else:
        raise ValueError(f"Solver '{solver}' is not supported.")
    """
if __name__ == '__main__':
    main()