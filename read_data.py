import pandas as pd

def read_input_from_excel(file_path):
    """
    Reads the input data from the Excel file.

    Args:
        file_path (str): Path to the Excel file containing the input data.

    Returns:
        tuple: Contains the following elements:
            - solver (str): Type of solver to use.
            - cycle_time (int): The cycle time for the problem.
            - num_tasks (int): The total number of tasks.
            - tasks_per_product (list): A list of dictionaries containing task durations for each product.
            - precedence_relations (list): List of tuples indicating task precedence relations.
            - incompatible_tasks (list): List of tuples indicating incompatible tasks.
    """
    solver, cycle_time, num_products, num_tasks = _read_hyperparameters(file_path)

    tasks_per_product = _read_task_times(file_path, num_products, num_tasks)

    precedence_relations = _read_task_pairs(file_path, 'precedence_relations')
    incompatible_tasks = _read_task_pairs(file_path, 'incompatible_tasks')
    compatible_tasks = _read_task_pairs(file_path, 'compatible_tasks')

    print(f"Data successfully loaded from `{file_path}`.")

    return (solver, cycle_time, num_tasks, tasks_per_product, precedence_relations, incompatible_tasks, compatible_tasks)

def _read_hyperparameters(file_path):
    df_overview = pd.read_excel(file_path, sheet_name='overview', header=None)

    solver = df_overview.iloc[0, 1]
    cycle_time = int(df_overview.iloc[1, 1])
    num_products = int(df_overview.iloc[2, 1])
    num_tasks = int(df_overview.iloc[3, 1])

    return (solver, cycle_time, num_products, num_tasks)

def _read_task_times(file_path, num_products, num_tasks):
    df_tasks = pd.read_excel(file_path, sheet_name='task_times')

    tasks_per_product = []
    for i in range(num_products):
        tasks = {}
        for j in range(num_tasks):
            task_duration = df_tasks.iloc[j, i+1]
            tasks[j+1] = task_duration
        tasks_per_product.append(tasks)

    return tasks_per_product

def _read_task_pairs(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return [
        tuple(map(int, task_pair.split(';')))
        for task_pair in df.iloc[:, 0].apply(str)
    ]