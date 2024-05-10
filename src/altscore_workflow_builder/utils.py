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
    # plus native_configuration
    with open(Path(config("PROJECT_ROOT")) / "app" / "tasks" / "task_definitions.json") as f:
        custom_configuration = json.load(f)
    return {**native_configuration, **custom_configuration}


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


def determine_levels(task_nodes):
    levels = {}
    max_width = 1500  # Define the maximum width of the graph
    level_spacing = {}
    no_incoming = set(task_nodes.keys())

    # Find tasks with no incoming edges (start nodes)
    for task, info in task_nodes.items():
        for next_task in info.get("to", []):
            if next_task in no_incoming:
                no_incoming.remove(next_task)

    # Assign levels using a queue
    queue = [(task, 0) for task in no_incoming]
    while queue:
        current, level = queue.pop(0)
        if current not in levels:
            levels[current] = level
        for next_task in task_nodes[current].get("to", []):
            if next_task not in levels or level + 1 > levels[next_task]:
                levels[next_task] = level + 1
                queue.append((next_task, level + 1))

    # Calculate spacing for each level
    for level in set(levels.values()):
        level_tasks = [task for task, lvl in levels.items() if lvl == level]
        width_per_task = max_width / max(1, len(level_tasks))
        level_spacing[level] = [width_per_task * (i + 0.5) for i in range(len(level_tasks))]

    return levels, level_spacing


native_configuration = {
    "workflow_args": {
        "name": "workflow_args",
        "custom_function": "",
        "inputs": [
            {
                "alias": "arguments"
            }
        ],
        "outputs": [],
    },
    "get_borrower_authorization": {
        "name": "get_borrower_authorization",
        "custom_function": "",
        "inputs": [
            {
                "alias": "key",
                "hint": "authorization key",
            },
            {
                "alias": "ensure",
                "hint": "ensure an authorization exists",
            },
            {
                "alias": "signed",
                "hint": "ensure there is a signed authorization",
            },
            {
                "alias": "borrower_id",
            },
        ],
        "outputs": [
            {
                "alias": "authorization",
                "hint": "aliased authorization dict",
            },
        ],
    },
    "persona_source": {
        "name": "persona_source",
        "custom_function": "",
        "inputs": [
            {
                "alias": "source_id",
                "hint": "source id",
            },
            {
                "alias": "source_version",
                "hint": "source version",
            },
            {
                "alias": "persona_info",
                "hint": "persona info",
            },
            {
                "alias": "authorization_reference",
                "hint": "authorization id",
                "optional": True,
            },
            {
                "alias": "override_keys",
                "hint": "dictionary specifying custom keys",
                "optional": True,
            },
            {
                "alias": "sandbox_version",
                "hint": "sandbox version",
                "optional": True,
            },
        ],
        "outputs": [
            {
                "alias": "source_output_package",
                "hint": "source output package",
            },
        ],
    },
    "evaluate_with_evaluator": {
        "name": "evaluate_with_evaluator",
        "custom_function": "",
        "inputs": [
            {
                "alias": "evaluator_alias",
                "hint": "evaluator alias",
            },
            {
                "alias": "evaluator_version",
                "hint": "evaluator version",
            },
            {
                "alias": "evaluation_instance",
                "hint": "evaluation instance",
            },
            {
                "alias": "evaluation_contacts",
                "hint": "evaluation contacts",
            },
        ],
        "outputs": [
            {
                "alias": "evaluator_output",
                "hint": "evaluator output",
            },
        ],
    },
    "borrower_data_enrichment": {
        "name": "borrower_data_enrichment",
        "custom_function": "",
        "inputs": [
            {
                "alias": "borrower_id",
                "hint": "borrower id",
            },
            {
                "alias": "input_keys",
                "hint": "input keys",
            },
            {
                "alias": "timeout",
                "hint": "timeout",
                "optional": True,
            },
            {
                "alias": "sources_config",
                "hint": "sources config",
            },
            {
                "alias": "conditions_met",
                "hint": "conditions met",
            }
        ],
        "outputs": [
            {
                "alias": "sources_output_packages",
                "hint": "sources output packages",
            },
        ],
    },
    "sat_data_extraction": {
        "name": "sat_data_extraction",
        "custom_function": "",
        "inputs": [
            {
                "alias": "rfc",
                "hint": "RFC of the borrower",
            },
            {
                "alias": "date_to_analyze",
                "hint": "Date to analyze the SAT data",
            },
            {
                "alias": "days_of_tolerance",
                "hint": "Days of tolerance to check for coverage",
            },
        ],
        "outputs": [
            {
                "alias": "has_coverage",
                "hint": "indicator that the borrower has coverage",
            },
            {
                "alias": "extraction_running",
                "hint": "indicator that the extraction is running",
            }
        ],
    },
    "wait_for_condition": {
        "name": "wait_for_condition",
        "custom_function": "",
        "inputs": [
            {
                "alias": "value",
                "hint": "value to evaluate the conditions",
            },
            {
                "alias": "should_be",
                "hint": "eq, ne, gt, lt, ge, le",
            },
            {
                "alias": "target",
                "hint": "target to compare with",
            },
            {
                "alias": "deadline",
                "hint": "datetime of the deadline to wait for",
            },
            {
                "alias": "abort_on_wait",
                "hint": "Prevent rest of workflow to run until condition is met",
            }
        ],
        "outputs": [
            {
                "alias": "w_schedule_callback",
                "hint": "indicator that the callback should be scheduled",
            },
        ],
    },
}
