import streamlit as st


def task_instance_dropdown(workflow_definition):
    options = []
    counter = 1
    for k, v in workflow_definition["task_instances"].items():
        options.append(
            {
                "task_instance_index": counter,  # this is used to sort the options
                "task_instance_key": k,
                "task_instance_type": v["type"]
            }
        )
        counter += 1
    return st.selectbox(
        "Select Task Instance",
        options,
        format_func=lambda x: f"{x['task_instance_index']} - {x['task_instance_key']} ({x['task_instance_type']})"
    )


def task_hitters(target_task_instance: str, workflow_definitions: dict):
    hitter_instances = []
    for task_instance_name, task_instance_data in workflow_definitions["task_instances"].items():
        if target_task_instance in task_instance_data.get("to", []):
            hitter_instances.append(task_instance_name)
    return list(set(hitter_instances))


def task_instance_graph(task_instance_key, workflow_definitions):
    task_instance_data = workflow_definitions["task_instances"].get(task_instance_key)
    st.json(task_instance_data)
    if task_instance_data is None:
        return None
    col1, col2 = st.columns(2)
    # the inputs
    col1.write("Hitters")
    hitters = task_hitters(target_task_instance=task_instance_key, workflow_definitions=workflow_definitions)
    task_dict = {}
    for hitter in hitters:
        task_dict[hitter] = col1.button(hitter)
    # the outputs
    col2.write("Targets")
    for target in task_instance_data["to"]:
        task_dict[target] = col2.button(target)
    return task_dict
