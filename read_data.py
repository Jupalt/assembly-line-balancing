import pandas as pd

def read_input_from_excel(file_path):
    """
    Reads the input data from the Excel file.

    Args:
        file_path (str): Path to the Excel file containing the input data.
    """
    
    solver, cycle_time, num_products, num_tasks = _read_hyperparameters(file_path)

    tasks, product_names, task_time_dict = _read_task_times(file_path)
    stationtype_compatibility, station_types = _read_station_types(file_path)
    station_costs = _read_station_costs(file_path)
    precedence_relations = _read_task_pairs(file_path, 'precedence_relations')
    incompatible_tasks = _read_task_pairs(file_path, 'incompatible_tasks')
    compatible_tasks = _read_task_pairs(file_path, 'compatible_tasks')

    data_input = {
        "solver": solver,
        "cycle_time": cycle_time,
        "num_tasks": num_tasks,
        "tasks": tasks,
        "product_names": product_names,
        "task_time_dict": task_time_dict,
        "station_costs": station_costs,
        "stationtype_compatibility": stationtype_compatibility,
        "station_types": station_types,
        "precedence_relations": precedence_relations,
        "incompatible_tasks": incompatible_tasks,
        "compatible_tasks": compatible_tasks,
    }

    print(f"Data successfully loaded from `{file_path}`.")

    return data_input

def _read_hyperparameters(file_path):
    df_overview = pd.read_excel(file_path, sheet_name='overview', header=None)

    solver = df_overview.iloc[0, 1]
    cycle_time = int(df_overview.iloc[1, 1])
    num_products = int(df_overview.iloc[2, 1])
    num_tasks = int(df_overview.iloc[3, 1])

    return (solver, cycle_time, num_products, num_tasks)

def _read_task_times(file_path):
    df_tasks = pd.read_excel(file_path, sheet_name='task_times')

    tasks = df_tasks.iloc[:, 0].tolist()

    product_names = df_tasks.columns[1:].tolist()

    product_columns = df_tasks.columns[1:]

    # Create task_time_dict dynamically
    task_time_dict = {}
    for _, row in df_tasks.iterrows():
        for product in product_columns:
            task_time_dict[(row.iloc[0], product)] = row[product]

    return tasks, product_names, task_time_dict

def _read_station_types(file_path):
    df_station_types = pd.read_excel(file_path, sheet_name='station_types')

    station_types = [col for col in df_station_types.columns if col != 'task_ID']

    # Convert the DataFrame to the required dictionary
    stationtype_compatibility = {
        (row['task_ID'], station_type): row[station_type]
        for _, row in df_station_types.iterrows()
        for station_type in station_types
    }

    return stationtype_compatibility, station_types

def _read_station_costs(file_path):
    df_station_costs = pd.read_excel(file_path, sheet_name='station_costs')

    station_costs = {row["Station"]: row["Costs"] for _, row in df_station_costs.iterrows()}

    return station_costs

def _read_task_pairs(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return [
        tuple(map(int, task_pair.split(';')))
        for task_pair in df.iloc[:, 0].apply(str)
    ]