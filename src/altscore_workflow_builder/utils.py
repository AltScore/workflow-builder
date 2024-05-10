import os
import json
from decouple import config
from pathlib import Path
import streamlit as st


def hide_deploy_button():
    hide_deploy_button_css = """
    <style>
        /* Replace .element-class with the actual class name or ID of the deploy button */
        .stDeployButton{
            display: none;
        }
    </style>
    """
    # Inject the CSS with the markdown component
    st.markdown(hide_deploy_button_css, unsafe_allow_html=True)


def load_task_definitions():
    with open(Path(config("PROJECT_ROOT")) / "app" / "tasks" / "task_definitions.json") as f:
        return json.load(f)


def save_task_definitions(task_definitions):
    with open(Path(config("PROJECT_ROOT")) / "app" / "tasks" / "task_definitions.json", "w") as f:
        json.dump(task_definitions, f)


def load_workflow_definition(workflow_alias: str, workflow_version: str):
    with open(Path(config(
            "PROJECT_ROOT")) / "app" / "workflows" / f"{workflow_alias}_{workflow_version}/flow_definition.json") as f:
        return json.load(f)


def save_workflow_definition(workflow_alias: str, workflow_version: str, flow_definition: dict):
    with open(Path(config(
            "PROJECT_ROOT")) / "app" / "workflows" / f"{workflow_alias}_{workflow_version}/flow_definition.json",
              "w") as f:
        json.dump(flow_definition, f)


def list_workflows():
    workflows = [f for f in os.listdir(Path(config("PROJECT_ROOT")) / "app" / "workflows") if
                 os.path.isdir(Path(config("PROJECT_ROOT")) / "app" / "workflows" / f)]
    return [
        {"alias": workflow.split("_")[0], "version": workflow.split("_")[-1], "label": workflow} for workflow in
        workflows
    ]


def calculate_task_levels(task_nodes):
    levels = {}
    queue = []

    # Start with tasks that have no incoming edges (sources)
    sources = [task for task, details in task_nodes.items() if
               all(task not in t.get("to", []) for t in task_nodes.values())]
    for source in sources:
        queue.append((source, 0))  # (task_name, level)

    # BFS to assign levels
    while queue:
        current_task, current_level = queue.pop(0)
        if current_task in levels:
            continue
        levels[current_task] = current_level
        for next_task in task_nodes[current_task].get("to", []):
            queue.append((next_task, current_level + 1))

    return levels
