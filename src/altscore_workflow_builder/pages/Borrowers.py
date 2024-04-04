import streamlit as st
from altscore_workflow_builder.utils import hide_deploy_button

hide_deploy_button()

st.title("Borrowers")

if 'borrower_id' not in st.session_state:
    st.session_state.borrower_id = None
if 'borrowers_query' not in st.session_state:
    st.session_state.borrowers_query = None


@st.cache_resource
def altscore_login():
    from altscore import AltScore
    from decouple import config
    altscore = AltScore(
        client_id=config("ALTSCORE_CLIENT_ID"),
        client_secret=config("ALTSCORE_CLIENT_SECRET"),
        environment=config("ALTSCORE_ENVIRONMENT")
    )
    return altscore


altscore = altscore_login()


@st.cache_data
def load_data_models(_altscore):
    data_models_ = altscore.borrower_central.data_models.retrieve_all()
    return data_models_


data_models = load_data_models(altscore)

with st.form(key='my_form'):
    borrower_query_by = st.selectbox(
        "Search By",
        ["self", "identity"]
    )
    search = st.text_input("Search")
    submit_button = st.form_submit_button(label='Submit')


def load_borrower(borrower_id):
    st.session_state.borrower_id = borrower_id


def render_borrower(borrower_summary):
    container = st.container(border=True)
    col1, col2 = container.columns(2)
    col1.write(f"ID: {borrower_summary.id} ({borrower_summary.persona})")
    col2.button(
        "Load",
        key=borrower_summary.id,
        on_click=load_borrower,
        args=(borrower_summary.id,)
    )
    container.json(borrower_summary.dict(by_alias=True))


if submit_button:
    st.session_state.borrowers_query = altscore.borrower_central.borrowers.query_summary(
        search=search,
        by=borrower_query_by
    )
if st.session_state.borrowers_query is not None:
    for borrower in st.session_state.borrowers_query:
        render_borrower(borrower)
