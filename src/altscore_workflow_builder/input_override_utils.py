import streamlit as st
from utils import save_workflow_definition


@st.cache_resource
def altscore_login():
    from altscore import AltScore
    from decouple import config
    altscore = AltScore(
        client_id=config("ALTSCORE_CLIENT_ID"),
        client_secret=config("ALTSCORE_CLIENT_SECRET"),
        environment=config("ENVIRONMENT")
    )
    return altscore


@st.cache_data
def load_sources(_altscore):
    sources_ = _altscore.borrower_central.store_sources.retrieve_all()
    return sources_


@st.cache_data
def load_data_models(_altscore):
    data_models_ = _altscore.borrower_central.data_models.retrieve_all()
    return data_models_


@st.experimental_dialog("Choose the source package")
def add_input_override(selected_task, workflow_alias, workflow_version, flow_definition):
    altscore = altscore_login()
    sources_ = load_sources(altscore)
    data_models_ = load_data_models(altscore)

    selected_sources = st.selectbox('Select Source', [source.data.id for source in sources_])
    selected_data_models = st.multiselect('Select Access key', [data_model.data.key for data_model in data_models_])
    if len(selected_sources) == 0:
        st.error("Please select at least one source")
        return

    if st.button("Add"):
        flow_definition['task_instances'][selected_task]['input_overrides'] = {
            f"borrower_package_{selected_sources}":
                {
                    "type": "borrower_package",
                    "borrower_id_input_alias": "borrower_id",
                    "source_id": selected_sources
                }
        }
        if len(selected_data_models) == 0:
            selected_data_models = None
        else:
            selected_data_models = f'by_{convert_snake_case_to_camel_case(selected_data_models[0])}'
            flow_definition['task_instances'][selected_task]['input_overrides']['package_alias'] = selected_data_models
        save_workflow_definition(workflow_alias, workflow_version, flow_definition)
        st.rerun()


def convert_snake_case_to_camel_case(snake_str):
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])
