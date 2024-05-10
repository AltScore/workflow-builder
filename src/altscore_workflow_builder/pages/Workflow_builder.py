import streamlit as st
from altscore_workflow_builder.utils import list_workflows, load_workflow_definition, load_task_definitions, \
    save_workflow_definition, save_task_definitions, calculate_positions
from altscore_workflow_builder.workflow import task_instance_dropdown, task_instance_graph
from altscore_workflow_builder.task import task_graph
from altscore_workflow_builder.utils import hide_deploy_button
from streamlit_agraph import agraph, Node, Edge, Config
import json

st.set_page_config(layout="wide")
hide_deploy_button()
st.title("Workflow Inspector")
st.sidebar.header("Graph Configuration")
workflow = st.sidebar.selectbox("Select Workflow", list_workflows())
flow_definition = load_workflow_definition(workflow['alias'], workflow['version'])
task_definitions = load_task_definitions()

# Configurable parameters in the sidebar
graph_height = st.sidebar.number_input("Height", min_value=500, max_value=1500, value=750)
background_color = st.sidebar.color_picker("Background Color", '#ffffff')
font_size = st.sidebar.slider("Font Size", 10, 20, 14)
node_color = st.sidebar.color_picker("Node Color", '#88c999')
edge_color = st.sidebar.color_picker("Edge Color", '#000000')
edge_type = st.sidebar.selectbox("Edge Type", ["STRAIGHT", "CURVE_SMOOTH", "CURVE_FULL"])
physics_enabled = st.sidebar.checkbox("Enable Physics", True)
solver_type = st.sidebar.selectbox("Physics Solver",
                                   ["barnesHut", "repulsion", "hierarchicalRepulsion", "forceAtlas2Based"])
directed = st.sidebar.checkbox("Directed Graph", True)
node_highlight = st.sidebar.checkbox("Highlight Nodes", True)
collapsible = st.sidebar.checkbox("Collapsible Nodes", True)
hierarchical_view = st.sidebar.checkbox("Hierarchical View", False)

# Create nodes, edges, and levels for the agraph
nodes = []
edges = []
task_nodes = flow_definition["task_instances"]
positions = calculate_positions(task_nodes)
all_task_names = list(task_nodes.keys())

for task_name, task_info in task_nodes.items():
    task_details = task_definitions.get(task_info['type'], {})
    x, y = positions[task_name]
    label = f"{task_name}\nInputs: {', '.join([inp['alias'] for inp in task_details.get('inputs', [])])}\nOutputs: {', '.join([out['alias'] for out in task_details.get('outputs', [])])}"
    nodes.append(Node(id=task_name, label=label, color=node_color, size=30, x=x, y=y))

for task_name, task_info in task_nodes.items():
    if 'to' in task_info:
        for next_task in task_info['to']:
            edges.append(Edge(source=task_name, target=next_task, color=edge_color, type=edge_type))

# Configuration for agraph
config = Config(
    height=graph_height,
    width='100%',
    directed=directed,
    nodeHighlightBehavior=node_highlight,
    highlightColor=node_color,
    collapsible=collapsible,
    node={'labelProperty': 'label', 'font_size': font_size},
    link={'labelProperty': 'label', 'renderLabel': True},
    staticGraph=not physics_enabled,
    physics={
        "solver": solver_type,
        "hierarchical": hierarchical_view
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

    # Editable fields for inputs, outputs, input conversions, and overrides
    input_json = st.sidebar.text_area("Inputs", value=json.dumps(task_details.get('inputs', []), indent=4))
    output_json = st.sidebar.text_area("Outputs", value=json.dumps(task_details.get('outputs', []), indent=4))
    input_override = st.sidebar.text_area("Input Override",
                                          value=json.dumps(task_info.get("input_override", {}), indent=4))
    input_conversion = st.sidebar.text_area("Input Conversion",
                                            value=json.dumps(task_info.get("input_conversion", {}), indent=4))

    current_edges = task_nodes[selected_task].get("to", [])
    new_edges = st.sidebar.multiselect("Select tasks that this task should point to:",
                                       all_task_names,
                                       default=current_edges)

    # Display the task graph
    if st.sidebar.button("Save Changes"):
        try:
            task_details['inputs'] = json.loads(input_json)
            task_details['outputs'] = json.loads(output_json)
            task_info['input_override'] = json.loads(input_override)
            task_info['input_conversion'] = json.loads(input_conversion)
            save_workflow_definition(workflow['alias'], workflow['version'], flow_definition)
            save_task_definitions(task_definitions)
            if new_edges != current_edges:
                task_nodes[selected_task]["to"] = new_edges
            st.sidebar.success("Changes saved successfully!")
            st.rerun()
        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON format. Please check your input.")
