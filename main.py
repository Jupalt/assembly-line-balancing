import logging

import read_data
import glkp_solver
import utils.validate_input as validator

from optimization_model import OptimizationModel
from highs_solver import SolverHiGHS
from scip_solver import SolverSCIP
from utils.graph_utils import validate_graph, visualize_graph


INPUT_DATA_PATH = "data/input.xlsx"
MPS_FILE_PATH = "result_data/alb_model.mps"

def main():
    # Sets the log level to DEBUG to display all logs from DEBUG level and above.
    logging.basicConfig(level=logging.DEBUG)

    # Tries to read input data from the INPUT_DATA_PATH Excel file.
    try:
        (
            solver, 
            cycle_time,
            num_tasks, 
            tasks_per_product, 
            precedence_relations, 
            incompatible_tasks,
            compatible_tasks
        ) = read_data.read_input_from_excel(INPUT_DATA_PATH)
    except FileNotFoundError as e:
        logging.error(f"File {INPUT_DATA_PATH} was not found: {e}")
    except Exception as e:
        logging.error(f"An error occurred while reading the input data: {e}")

    # Checks if precedence_relations is valid, e.g. if it contains a cycle
    print("Precedence relations validation: ", end="")
    validate_graph(precedence_relations)

    print(tasks_per_product)
    validator.validate_input(tasks_per_product, compatible_tasks, incompatible_tasks, precedence_relations, cycle_time)

    # Visualizes the precedence relations as a graph
    visualize_graph(precedence_relations)
    
    # Builds the model
    model = OptimizationModel().build_model(cycle_time, num_tasks, tasks_per_product, precedence_relations, incompatible_tasks, compatible_tasks)
    OptimizationModel().save_to_mps(model, MPS_FILE_PATH)
    
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
    
if __name__ == '__main__':
    main()
