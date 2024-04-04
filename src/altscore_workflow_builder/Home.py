import streamlit as st

# This must go first
st.set_page_config(
    page_title="AltScore Workflow Builder",
    page_icon=":bar_chart:",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "This is a workflow builder for AltScore",
    }
)
from altscore_workflow_builder.utils import hide_deploy_button

hide_deploy_button()
