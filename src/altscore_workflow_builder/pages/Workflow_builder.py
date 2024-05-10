import streamlit as st
from altscore_workflow_builder.utils import list_workflows, load_workflow_definition, load_task_definitions, \
    save_workflow_definition, save_task_definitions, determine_levels, add_item, remove_item
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
agraph(nodes=nodes, edges=edges, config=config)

# Task editing sidebar
st.sidebar.header("Edit Task Properties")
selected_task = st.sidebar.selectbox("Select a task to edit:", list(task_nodes.keys()))

if selected_task:
    st.sidebar.write(f"Editing: {selected_task}")
    task_info = task_nodes[selected_task]
    task_details = task_definitions.get(task_info['type'], {})

    # Inputs management
    st.sidebar.json(task_details.get('inputs', []))
    input_alias = st.sidebar.text_input("Input Alias")
    if st.sidebar.button("Add new input"):
        add_item(task_details, 'inputs', input_alias, task_definitions, selected_task)

    input_aliases = [input_item['alias'] for input_item in task_details.get('inputs', [])]
    input_to_remove = st.sidebar.selectbox("Select input to remove", input_aliases)
    if st.sidebar.button("Remove selected input"):
        remove_item(task_details, 'inputs', input_to_remove, task_definitions, selected_task)

    # Outputs management
    st.sidebar.json(task_details.get('outputs', []))
    output_alias = st.sidebar.text_input("Output Alias")
    if st.sidebar.button("Add new output"):
        add_item(task_details, 'outputs', output_alias, task_definitions, selected_task)

    output_aliases = [output_item['alias'] for output_item in task_details.get('outputs', [])]
    output_to_remove = st.sidebar.selectbox("Select output to remove", output_aliases)
    if st.sidebar.button("Remove selected output"):
        remove_item(task_details, 'outputs', output_to_remove, task_definitions, selected_task)


    # output_json = st.sidebar.json(task_details.get('outputs', []))

    # input_override = st.sidebar.text_area("Input Override",
    #                                       value=json.dumps(task_info.get("input_override", {}), indent=4))
    # input_conversion = st.sidebar.text_area("Input Conversion",
    #                                         value=json.dumps(task_info.get("input_conversion", {}), indent=4))
    #
    # current_edges = task_nodes[selected_task].get("to", [])
    # new_edges = st.sidebar.multiselect("Select tasks that this task should point to:",
    #                                    all_task_names,
    #                                    default=current_edges)

    # if st.sidebar.button("Save Changes"):
    #     try:
    #         task_details['outputs'] = json.loads(output_json)
    #         task_info['input_override'] = json.loads(input_override)
    #         task_info['input_conversion'] = json.loads(input_conversion)
    #         save_workflow_definition(workflow['alias'], workflow['version'], flow_definition)

    #         if new_edges != current_edges:
    #             task_nodes[selected_task]["to"] = new_edges
    #         st.sidebar.success("Changes saved successfully!")
    #         st.rerun()
    # except json.JSONDecodeError:
    #     st.sidebar.error("Invalid JSON format. Please check your input.")
