import streamlit as st
from utils import save_workflow_definition, save_task_definitions


def add_native_task(task_name, native_task, workflow_alias, workflow_version, flow_definition):
    flow_definition["task_instances"][task_name] = {"type": native_task, "to": {}}
    save_workflow_definition(workflow_alias, workflow_version, flow_definition)


def remove_native_task(task_name, workflow_alias, workflow_version, flow_definition):
    del flow_definition["task_instances"][task_name]
    for task, details in flow_definition["task_instances"].items():
        if 'to' in details:
            if task_name in details['to']:
                details['to'].pop(task_name)
    save_workflow_definition(workflow_alias, workflow_version, flow_definition)
    st.success(f"Task {task_name} deleted successfully.")
