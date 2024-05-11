import os
import json
from decouple import config
from pathlib import Path
import streamlit as st
from utils import save_workflow_definition, save_task_definitions


def add_native_task(task_name, native_task, workflow_alias, workflow_version, flow_definition):
    flow_definition["task_instances"][task_name] = {"type": native_task, "to": {}}
    save_workflow_definition(workflow_alias, workflow_version, flow_definition)


def remove_native_task(task_name, workflow_alias, workflow_version, flow_definition):
    if st.button("Delete Task"):
        del flow_definition["task_instances"][task_name]
        save_workflow_definition(workflow_alias, workflow_version, flow_definition)
        st.success(f"Task {task_name} deleted successfully.")
