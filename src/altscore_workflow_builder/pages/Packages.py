import json
import streamlit as st
from altscore_workflow_builder.utils import hide_deploy_button

hide_deploy_button()
st.title("Packages")


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


altscore = altscore_login()


@st.cache_data
def load_sources(_altscore):
    sources_ = altscore.borrower_central.store_sources.retrieve_all()
    return sources_


sources_ = load_sources(altscore)

with st.form(key='my_form'):
    if 'borrower_id' not in st.session_state:
        st.session_state.borrower_id = None
        borrower_id = st.text_input("Borrower ID").replace('"', '').replace("'", "").strip()
    else:
        borrower_id = st.text_input("Borrower ID", value=st.session_state.borrower_id).replace('"', '').replace("'",
                                                                                                                "").strip()
    source_id = st.selectbox("Source", [None] + list(sorted([s.data.id for s in sources_])))
    submit_button = st.form_submit_button(label='Submit')


def set_package_content(package_id):
    package = altscore.borrower_central.store_packages.retrieve(package_id)
    package.get_content()
    st.session_state.package_content = json.loads(package.content)


def render_package(package):
    st.json(package.data.dict(by_alias=True))
    st.button(
        "Load Content",
        key=package.data.id,
        on_click=set_package_content,
        args=(package.data.id,)
    )


if submit_button:
    packages = altscore.borrower_central.store_packages.query(
        borrower_id=borrower_id if len(borrower_id) > 4 else None,
        source_id=source_id
    )
    for package in packages:
        render_package(package)

if 'package_content' not in st.session_state:
    st.session_state.package_content = None
if st.session_state.package_content is not None:
    st.json(st.session_state.package_content)
