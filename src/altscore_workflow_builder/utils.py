import os
import json
from decouple import config
from pathlib import Path
import streamlit as st
from workflows.native_tasks import native_configuration


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
        custom_configuration = json.load(f)
    return native_configuration, custom_configuration


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
        for next_task in info.get("to", {}):
            if next_task in no_incoming:
                no_incoming.remove(next_task)

    # Assign levels using a queue
    queue = [(task, 0) for task in no_incoming]
    while queue:
        current, level = queue.pop(0)
        if current not in levels:
            levels[current] = level
        for next_task in task_nodes[current].get("to", {}):
            if next_task not in levels or level + 1 > levels[next_task]:
                levels[next_task] = level + 1
                queue.append((next_task, level + 1))

    # Calculate spacing for each level
    for level in set(levels.values()):
        level_tasks = [task for task, lvl in levels.items() if lvl == level]
        width_per_task = max_width / max(1, len(level_tasks))
        level_spacing[level] = [width_per_task * (i + 0.5) for i in range(len(level_tasks))]

    return levels, level_spacing


def add_item(task_details, key, item_details, task_definitions, selected_task, is_key_value=False):
    """Add an item (input/output/override/conversion) to the task details."""
    if is_key_value:
        if all(item_details.values()):
            task_details[key].append(item_details)
            task_definitions[selected_task] = task_details
            save_task_definitions(task_definitions)
            st.sidebar.success(f"New {key[:-1]} added successfully!")
        else:
            st.sidebar.error(f"Both key and value are required for {key[:-1]}.")
    else:
        if item_details['alias']:
            task_details[key].append(item_details)
            task_definitions[selected_task] = task_details
            save_task_definitions(task_definitions)
            st.sidebar.success(f"New {key[:-1]} added successfully!")
        else:
            st.sidebar.error(f"{key[:-1].capitalize()} alias cannot be empty.")
    st.rerun()


def update_edges(action, src, tgt, workflow_alias, workflow_version, flow_definition):
    data_to_append = {src: {}}
    if action == 'add' and tgt not in flow_definition["task_instances"][src]["to"]:
        flow_definition["task_instances"][src]["to"][tgt] = {}
    elif action == 'remove' and tgt in flow_definition["task_instances"][src]["to"]:
        flow_definition["task_instances"][src]["to"].pop(tgt)
    save_workflow_definition(workflow_alias, workflow_version, flow_definition)


def create_task(new_task_name, task_definitions, new_task_inputs, new_task_outputs, workflow_alias, workflow_version,
                flow_definition):
    new_task_name = new_task_name.replace(" ", "").lower()
    new_task_inputs = new_task_inputs.replace(" ", "").lower()
    new_task_outputs = new_task_outputs.replace(" ", "").lower()

    task_definitions[new_task_name] = {
        "name": new_task_name,
        "inputs": [{"alias": inp.strip()} for inp in new_task_inputs.split(',') if inp],
        "outputs": [{"alias": out.strip()} for out in new_task_outputs.split(',') if out]
    }
    flow_definition["task_instances"][new_task_name] = {"type": new_task_name, "to": {}}
    new_task_class = new_task_name.replace("_", " ").title().replace(" ", "")
    save_task_definitions(task_definitions)
    save_workflow_definition(workflow_alias, workflow_version, flow_definition)
    add_custom_class(Path(config("PROJECT_ROOT")) / "app" / "tasks" / "__init__.py", new_task_name,
                     new_task_class)
    create_task_file(Path(config("PROJECT_ROOT")) / "app" / "tasks" / f"{new_task_name}.py",
                     new_task_class,
                     new_task_inputs, new_task_outputs)

    st.success("Task created successfully!")


def delete_task(selected_task, task_definitions, flow_definition, workflow):
    if selected_task in task_definitions:
        del task_definitions[selected_task]
    if selected_task in flow_definition["task_instances"]:
        del flow_definition["task_instances"][selected_task]
    for task, details in flow_definition["task_instances"].items():
        if 'to' in details:
            if selected_task in details['to']:
                details['to'].pop(selected_task)

    save_task_definitions(task_definitions)
    save_workflow_definition(workflow['alias'], workflow['version'], flow_definition)
    remove_custom_class(Path(config
                             ("PROJECT_ROOT")) / "app" / "tasks" / "__init__.py", selected_task)
    delete_task_file(Path(config("PROJECT_ROOT")) / "app" / "tasks" / f"{selected_task}.py")
    st.success(f"Task '{selected_task}' deleted successfully!")


def add_custom_class(file_path, new_task_name, new_task_class):
    new_import = f"from app.tasks.{new_task_name.lower()} import {new_task_class}\n"
    new_dict_entry = f'    "{new_task_name.lower()}": {new_task_class},\n'

    # Read the existing content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Prepare to modify the file content
    with open(file_path, 'w') as file:
        import_added = False
        dict_entry_added = False
        i = 0  # Index to keep track of the current line in the loop
        while i < len(lines):
            line = lines[i]
            # Check if the import section has ended and our import is not yet added
            if 'import' in line and not import_added:
                if 'from app.tasks' not in line:
                    file.write(new_import)
                    import_added = True

            # Check where to add the new dictionary entry
            if 'custom_functions:' in line and not dict_entry_added:
                file.write(line)
                i += 1  # Move to the next line
                if i < len(lines):
                    file.write(lines[i])  # Write the next line which starts the dictionary
                    file.write(new_dict_entry)  # Add new entry
                    dict_entry_added = True
                    i += 1  # Skip writing the next line manually
                    continue

            # Write the current line back to the file
            file.write(line)
            i += 1

        # In case imports or dictionary entries are at the end and no modification was triggered
        if not import_added:
            file.write(new_import)
        if not dict_entry_added:
            file.write(f"\ncustom_functions['{new_task_name.lower()}'] = {new_task_class}\n")


def remove_custom_class(file_path, task_name):
    # Define the target import line and dictionary entry
    target_import = f"from app.tasks.{task_name.lower()} import "
    target_dict_key = f'    "{task_name.lower()}": '

    # Read the existing content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Prepare to modify the file content
    with open(file_path, 'w') as file:
        skip_import = False
        skip_dict_entry = False
        for line in lines:
            # Check for the import line to skip
            if line.startswith(target_import):
                skip_import = True
                continue  # Skip this import line

            # Check for the dictionary entry line to skip
            if line.startswith(target_dict_key):
                skip_dict_entry = True
                continue  # Skip this dictionary entry line

            # Write back other lines
            file.write(line)

    # Confirm removal status for diagnostics
    if skip_import and skip_dict_entry:
        print(f"Removed import and dictionary entry for {task_name}.")
    else:
        print(f"Could not find import or dictionary entry for {task_name}.")


def create_task_file(file_path, class_name, inputs, outputs):
    # Try to split the inputs and outputs by ',', if not possible, use the whole string as list with one element
    inputs = inputs.split(',') if ',' in inputs else [inputs]
    outputs = outputs.split(',') if ',' in outputs else [outputs]

    content = f"""from typing import Dict
from workflows.model.task_definition import TaskConfiguration
from workflows.model.task_instance import TaskInstanceConfiguration
from workflows.model.custom_function import CustomFunction


class {class_name}(CustomFunction):
    \"\"\"
    Inputs: {inputs}
    Outputs: {outputs}
    \"\"\"

    async def _execute(self, inputs: dict, task_configuration: TaskConfiguration,
                       task_instance_configuration: TaskInstanceConfiguration, context: Dict):
        # Example processing of inputs
"""

    for input_name in inputs:
        content += f"        {input_name} = inputs.get('{input_name}')\n"

    content += "\n"

    content += "        return {\n"
    for output in outputs:
        content += f"            '{output}': {output},  # Adjust the output as needed\n"
    content += "        }\n"

    with open(file_path, 'w') as file:
        file.write(content)
    print(f"File created: {file_path}")


def delete_task_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File deleted: {file_path}")
    else:
        print(f"File not found: {file_path}")
