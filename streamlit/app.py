import streamlit as st

st.set_page_config(layout="wide")

pagina = st.selectbox(
    "Escolha a página",
    (
        "Dashboard",
        "Modelo ML"
    )
)

if pagina == "Dashboard":
    st.switch_page("pages/1_dashboard.py")

elif pagina == "Modelo ML":
    st.switch_page("pages/2_modeloML.py")