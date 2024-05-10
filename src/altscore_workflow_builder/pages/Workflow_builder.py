import streamlit as st
from altscore_workflow_builder.utils import list_workflows, load_workflow_definition, load_task_definitions, \
    save_workflow_definition, save_task_definitions, determine_levels, add_item, update_edges
from altscore_workflow_builder.workflow import task_instance_dropdown, task_instance_graph
from altscore_workflow_builder.task import task_graph
from altscore_workflow_builder.utils import hide_deploy_button
from streamlit_agraph import agraph, Node, Edge, Config
import json

st.set_page_config(layout="wide")
hide_deploy_button()
st.sidebar.header("Graph Configuration")
workflow = st.sidebar.selectbox("Select Workflow", list_workflows())
flow_definition = load_workflow_definition(workflow['alias'], workflow['version'])
task_definitions = load_task_definitions()

# Create nodes, edges, and levels for the agraph
nodes = []
edges = []
task_nodes = flow_definition["task_instances"]
levels, level_spacing = determine_levels(task_nodes)
all_task_names = list(task_nodes.keys())

for task_name, task_info in flow_definition["task_instances"].items():
    inputs = ", ".join([inp['alias'] for inp in task_definitions.get(task_info['type'], {}).get('inputs', [])])
    outputs = ", ".join([out['alias'] for out in task_definitions.get(task_info['type'], {}).get('outputs', [])])
    label = f"{task_name}"
    tooltip = f"Inputs: {inputs}\nOutputs: {outputs}"
    level = levels[task_name]
    nodes.append(
        Node(id=task_name, label=label, color="lightblue", size=50, x=level_spacing[level].pop(0), y=level * 150,
             title=tooltip))

    for next_task in task_info.get("to", []):
        edges.append(Edge(source=task_name, target=next_task, type="STRAIGHT"))

# Configuration for agraph
config = Config(
    height=900,
    width='100%',
    directed=True,
    nodeHighlightBehavior=True,
    highlightColor='#88c999',
    collapsible=True,
    node={'labelProperty': 'label', 'font_size': 20},
    link={'labelProperty': 'label', 'renderLabel': True},
    staticGraph=True,
    physics={
        "solver": 'barnesHut',
        "hierarchical": False
    }
)

# Display the graph
selection = agraph(nodes=nodes, edges=edges, config=config)

if selection:
    st.sidebar.write(f"Selected task: {selection}")
    task_info = task_nodes[selection]
    selected_task = st.sidebar.selectbox("Select Task", all_task_names, index=all_task_names.index(selection))
    if selected_task:
        st.sidebar.write(f"Editing: {selected_task}")
        task_info = task_nodes[selected_task]
        task_details = task_definitions.get(task_info['type'], {})

        # Inputs, Outputs, Overrides, Conversions management
        for detail_key in ['inputs', 'outputs', 'overrides', 'conversions']:
            # Add a Title
            st.sidebar.title(f"{detail_key.capitalize()} Management")
            st.sidebar.json(task_details.get(detail_key, []))

            if detail_key in ['overrides', 'conversions']:
                key_name = st.sidebar.text_input(f"Key for {detail_key[:-1]}", key=f"{detail_key}_key")
                value_name = st.sidebar.text_input(f"Value for {detail_key[:-1]}", key=f"{detail_key}_value")
                item_details = {"key": key_name, "value": value_name}
                button_label = f"Add new {detail_key[:-1]}"
                if st.sidebar.button(button_label):
                    add_item(task_details, detail_key, item_details, task_definitions, selected_task, is_key_value=True)
            else:
                alias_name = st.sidebar.text_input(f"Alias for {detail_key[:-1]}", key=f"{detail_key}_alias")
                item_details = {"alias": alias_name}
                button_label = f"Add new {detail_key[:-1]}"
                if st.sidebar.button(button_label):
                    add_item(task_details, detail_key, item_details, task_definitions, selected_task)

            # Deletion interface remains largely the same
            aliases = [item['alias'] if 'alias' in item else f"{item['key']}:{item['value']}" for item in
                       task_details.get(detail_key, [])]
            item_to_remove = st.sidebar.selectbox(f"Select {detail_key[:-1]} to remove", aliases,
                                                  key=f"{detail_key}_remove")
            if st.sidebar.button(f"Remove selected {detail_key[:-1]}"):
                if detail_key in ['overrides', 'conversions']:
                    task_details[detail_key] = [item for item in task_details[detail_key] if
                                                f"{item['key']}:{item['value']}" != item_to_remove]
                else:
                    task_details[detail_key] = [item for item in task_details[detail_key] if
                                                item['alias'] != item_to_remove]
                task_definitions[selected_task] = task_details
                save_task_definitions(task_definitions)
                st.sidebar.success(f"{detail_key[:-1].capitalize()} removed successfully!")
                st.rerun()





    # UI for edge management
    st.sidebar.title("Manage Edges")
    source_task = st.sidebar.selectbox("Source Task", all_task_names, index=all_task_names.index(selection))
    target_task = st.sidebar.selectbox("Target Task", all_task_names, index=all_task_names.index(selection))
    if st.sidebar.button("Add Edge"):
        update_edges('add', source_task, target_task, workflow['alias'], workflow['version'], flow_definition)
        st.rerun()
    if st.sidebar.button("Remove Edge"):
        update_edges('remove', source_task, target_task, workflow['alias'], workflow['version'], flow_definition)
        st.rerun()
