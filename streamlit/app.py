import streamlit as st

st.set_page_config(
    page_title="Tech Challenge",
    layout="wide"
)

st.title("Tech Challenge")

st.page_link("pages/1_dashboard.py", label="Dashboard")
st.page_link("pages/2_modeloML.py", label="Modelo ML")