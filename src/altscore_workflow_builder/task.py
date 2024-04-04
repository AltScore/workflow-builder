import streamlit as st


def task_graph(task_key: str, task_definitions: dict, workflow_definitions: dict):
    st.subheader(f"Task: {task_key}")
    task_type = workflow_definitions["task_instances"][task_key]["type"]
    task_instance_data = task_definitions.get(task_type)
    if task_instance_data is None:
        return None
    st.json(task_instance_data)
