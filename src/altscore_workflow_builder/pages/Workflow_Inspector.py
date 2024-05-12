import streamlit as st
from altscore_workflow_builder.utils import list_workflows, load_workflow_definition, load_task_definitions
from altscore_workflow_builder.workflow import task_instance_dropdown, task_instance_graph
from altscore_workflow_builder.task import task_graph
from altscore_workflow_builder.utils import hide_deploy_button

hide_deploy_button()
st.title("Workflow Inspector")
all_workflows = list_workflows()
native_task_definitions, custom_task_definitions = load_task_definitions()
task_definitions = {**native_task_definitions, **custom_task_definitions}
workflow = st.selectbox(label="Select Workflow", options=all_workflows, format_func=lambda x: x["label"])
workflow_definition = load_workflow_definition(
    workflow_alias=workflow["alias"],
    workflow_version=workflow["version"]
)

selected_task_instance = task_instance_dropdown(workflow_definition)
task_dict = task_instance_graph(selected_task_instance["task_instance_key"], workflow_definitions=workflow_definition)
selected_task = [k for k, v in task_dict.items() if v]

if len(selected_task) > 0:
    selected_task = selected_task[0]
    task_graph(selected_task, task_definitions=task_definitions, workflow_definitions=workflow_definition)
