import streamlit as st
from utils import save_workflow_definition


def add_workflow_args(new_workflow_arg, workflow_alias, workflow_version, flow_definition):
    flow_definition["workflow_args"].append({"alias": new_workflow_arg})
    save_workflow_definition(workflow_alias, workflow_version, flow_definition)


def remove_workflow_args(workflow_arg, workflow_alias, workflow_version, flow_definition):
    flow_definition["workflow_args"] = [arg for arg in flow_definition["workflow_args"] if arg["alias"] != workflow_arg]
    save_workflow_definition(workflow_alias, workflow_version, flow_definition)
