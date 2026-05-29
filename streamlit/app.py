import streamlit as st

# Definindo páginas
dashboard_page = st.Page(
    "pages/1_dashboard.py",
    title="Dashboard",
    icon="📊"
)

modelo_page = st.Page(
    "pages/2_modeloML.py",
    title="Modelo ML",
    icon="🤖"
)

# Navegação
pg = st.navigation(
    [dashboard_page, modelo_page]
)

# Elementos globais
st.sidebar.title("Tech Challenge")

# Executa página selecionada
pg.run()