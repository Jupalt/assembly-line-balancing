import utils.graph as graph

def find_connected_task_groups(compatible_task_pairs):
    """
    Finds groups of tasks connected through compatibility pairs.

    Args:
        compatible_task_pairs (list of tuple): A list of task pairs that are compatible.

    Returns:
        list of list: A list of unique task groups.
    """
    def _find_group(initial_pair, remaining_pairs):
        """
        Recursively finds all tasks connected through compatibility pairs.

        Args:
            initial_pair (list): The initial group of tasks.
            remaining_pairs (list of tuple): The remaining compatibility pairs to process.

        Returns:
            list: A complete list of tasks connected to the initial pair.
        """
        group = list(initial_pair)
        pairs_to_process = remaining_pairs.copy()
        newly_added = True

        while newly_added:
            newly_added = False
            for task1, task2 in pairs_to_process:
                if task1 in group or task2 in group:
                    if task1 not in group:
                        group.append(task1)
                    if task2 not in group:
                        group.append(task2)
                    pairs_to_process.remove((task1, task2))
                    newly_added = True
        return group

    # Find all connected groups
    groups = []
    for pair in compatible_task_pairs:
        remaining_pairs = compatible_task_pairs.copy()
        group = _find_group(pair, remaining_pairs)
        groups.append(group)

    # Remove duplicate groups
    unique_groups = {frozenset(group) for group in groups}
    return [list(group) for group in unique_groups]


def check_task_groups_against_cycle_time(task_groups, tasks, cycle_time):
    """
    Checks if groups of tasks can be completed within the given cycle time.

    Args:
        task_groups (list of list): A list of task groups.
        tasks (dict): A dictionary where keys are task IDs and values are task times.
        cycle_time (int): The maximum allowable time for a group of tasks.

    Returns:
        None
    """
    for group in task_groups:
        total_time = sum(tasks[task] for task in group)
        if total_time > cycle_time:
            print(f"Tasks {group} cannot be processed together (total time: {total_time}).")
        else:
            print(f"Tasks {group} can be processed together (total time: {total_time}).")


def validate_task_groups(task_groups, incompatible_task_pairs):
    """
    Validates that task groups do not contain any incompatible tasks.

    Args:
        task_groups (list of list): A list of task groups.
        incompatible_task_pairs (list of tuple): A list of task pairs that are incompatible.

    Returns:
        None
    """
    for group in task_groups:
        for task1, task2 in incompatible_task_pairs:
            if task1 in group and task2 in group:
                print(f"Group {group} contains incompatible tasks ({task1}, {task2}).")
                return False  # Incompatible tasks detected
    print("All task groups are valid.")
    return True

def check_precedence_relations(connected_task_groups, precedence_relations, incompatible_task_pairs):
    g = graph.Graph()
    g.add_edges(precedence_relations)

    for connected_task_group in connected_task_groups:
        subgraph_edges = g.get_edges_of_subgraph_with_paths(connected_task_group)

        subgraph = graph.Graph()
        subgraph.add_edges(subgraph_edges)

        nodes_with_predecessors_and_successors = subgraph.get_nodes_with_predecessors_and_successors()

        for task1, task2 in incompatible_task_pairs:
            if task1 in nodes_with_predecessors_and_successors:
                if subgraph.is_predecessor(task1, task2):
                    print("------------------------------------------------------------------------")
                    print(f"Error due to: ")
                    print(f"Task {task1} is incompatible to task {task2}, but ", end="")
                    print(f"Task {task2} is predecessor of task {task1}.")
                    print(f"This contradicts to the following compatible tasks: {connected_task_groups}")
                    print(f"This is the corresponding subgraph: {subgraph_edges}")
                    print("------------------------------------------------------------------------")
                    return False

            if task2 in nodes_with_predecessors_and_successors:
                if subgraph.is_predecessor(task2, task1):
                    print("------------------------------------------------------------------------")
                    print(f"Error due to: ")
                    print(f"Task {task2} is incompatible to task {task1}, but ", end="")
                    print(f"Task {task1} is predecessor of task {task2}.")
                    print(f"This contradicts to the following compatible tasks: {connected_task_groups}")
                    print(f"This is the corresponding subgraph: {subgraph_edges}")
                    print("------------------------------------------------------------------------")
                    return False
                
    return True

def validate_input(tasks_per_product, compatible_task_pairs, incompatible_task_pairs, precedence_relations, cycle_time):
    """
    Processes tasks with compatibility, incompatibility, precedence, and cycle time constraints.

    Args:
        tasks (dict): A dictionary where keys are task IDs and values are task times.
        compatible_task_pairs (list of tuple): A list of task pairs that are compatible.
        incompatible_task_pairs (list of tuple): A list of task pairs that are incompatible.
        precedence_relations (list of tuple): A list of precedence relations (task1, task2).
        cycle_time (int): The maximum allowable time for a group of tasks.

    Returns:
        None
    """
    print("Finding connected task groups... ", end="")
    connected_task_groups = find_connected_task_groups(compatible_task_pairs)
    print("Done.")

    print("Validating task groups against incompatibilities... ", end="")
    valid = validate_task_groups(connected_task_groups, incompatible_task_pairs)
    if not valid:
        print("\nTask group validation failed due to incompatibilities.")
        return

    print("Checking groups against cycle time...")
    for tasks in tasks_per_product:
        check_task_groups_against_cycle_time(connected_task_groups, tasks, cycle_time)

    print("Checking precedence relations...")
    valid = check_precedence_relations(connected_task_groups, precedence_relations, incompatible_task_pairs)
    if not valid:
        print("Precedence relations check failed.")
        return

    print("Processing complete.")


# Example usage
tasks = [{1: 1, 2: 1, 3: 1, 4: 6, 5: 8}]
compatible_task_pairs = [(1, 3)]
incompatible_task_pairs = [(1, 2)]
precedence_relations = [(1, 2), (2, 3)]
cycle_time = 500

# validate_input(tasks, compatible_task_pairs, incompatible_task_pairs, precedence_relations, cycle_time)

