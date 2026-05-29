"""
dashboard.py
============
Dashboard interativo de análise exploratória do dataset de Obesidade.

Estrutura do arquivo
--------------------
1. Configuração da página e CSS
2. Paleta de cores e mapeamentos de rótulos
3. Carregamento e pré-processamento dos dados
4. Sidebar com filtros interativos
5. Filtragem reativa do dataframe
6. KPIs (métricas resumidas)
7. Gráficos:
   - Linha 1 : Distribuição por classe | Distribuição por gênero (barras)
   - Linha 2 : Boxplot IMC por classe  | Scatter Peso × Altura
   - Linha 3 : Histograma de Idade     | Histograma de IMC
   - Linha 4 : Hábitos por classe (seletor interativo)
   - Linha 5 : Meio de transporte      | Histórico familiar × Obesidade
8. Tabela de dados filtrados com exportação CSV

Dependências (streamlit/requirements)
--------------------------------------
    streamlit
    pandas
    numpy
    plotly
    requests
    scikit-learn

Como adicionar ao projeto
--------------------------
Coloque este arquivo em:
    TECHCHALLENGER4/streamlit/pages/dashboard.py

O Streamlit detecta a pasta `pages/` automaticamente e exibe
um menu de navegação lateral com todas as páginas disponíveis.
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# =============================================================================

st.set_page_config(
    page_title="Dashboard de Obesidade",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS customizado com tema escuro, tipografia DM Sans e cards de KPI estilizados.
# As variáveis de cor principais são:
#   #0f1117  → fundo geral (quase preto)
#   #1e2130  → superfície dos cards
#   #2d3250  → bordas e separadores
#   #7c8dff  → azul accent (valores dos KPIs)
#   #c5cae9  → texto principal sobre fundo escuro
#   #8b92a5  → texto secundário / labels
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=DM+Mono&display=swap');

    /* Tipografia global */
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    /* Fundo da área principal */
    .main { background-color: #0f1117; }

    /* Card de KPI — gradiente sutil sobre fundo escuro */
    .metric-card {
        background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
        border: 1px solid #2d3250;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }

    /* Valor numérico do KPI em fonte monoespaçada para alinhamento */
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #7c8dff;
        font-family: 'DM Mono', monospace;
    }

    /* Rótulo descritivo abaixo do valor */
    .metric-label {
        font-size: 0.8rem;
        color: #8b92a5;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    /* Título de seção acima de cada bloco de gráfico */
    .section-title {
        font-size: 1rem;
        font-weight: 500;
        color: #c5cae9;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #2d3250;
    }

    /* Labels dos widgets da sidebar */
    .stSelectbox label, .stMultiSelect label {
        color: #8b92a5 !important;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. PALETA DE CORES E MAPEAMENTOS DE RÓTULOS
# =============================================================================

# Paleta pastel com progressão visual intuitiva:
#   Azuis  → pesos saudáveis / insuficientes
#   Cinzas → sobrepeso
#   Vermelhos pastel → obesidade (intensidade crescente)
OBESITY_COLORS = {
    "Insufficient_Weight": "#a8c4e0",   # azul pastel claro
    "Normal_Weight":       "#b8cfe8",   # azul pastel médio
    "Overweight_Level_I":  "#b0b8c8",   # cinza azulado
    "Overweight_Level_II": "#9aa4b2",   # cinza médio
    "Obesity_Type_I":      "#f4b8b8",   # vermelho pastel claro
    "Obesity_Type_II":     "#e89090",   # vermelho pastel médio
    "Obesity_Type_III":    "#d96b6b",   # vermelho pastel forte
}

# Ordem canônica das classes (do menor para o maior IMC esperado)
OBESITY_ORDER = list(OBESITY_COLORS.keys())

# Tradução das classes para português (usada nos eixos e legendas dos gráficos)
OBESITY_PT = {
    "Insufficient_Weight": "Peso Insuficiente",
    "Normal_Weight":       "Peso Normal",
    "Overweight_Level_I":  "Sobrepeso Nível I",
    "Overweight_Level_II": "Sobrepeso Nível II",
    "Obesity_Type_I":      "Obesidade Tipo I",
    "Obesity_Type_II":     "Obesidade Tipo II",
    "Obesity_Type_III":    "Obesidade Tipo III",
}

# Paleta e ordem já com chaves em português (para uso direto no Plotly)
OBESITY_COLORS_PT = {OBESITY_PT[k]: v for k, v in OBESITY_COLORS.items()}
OBESITY_ORDER_PT  = [OBESITY_PT[k] for k in OBESITY_ORDER]

# Tradução do meio de transporte
TRANSP_PT = {
    "Public_Transportation": "Transporte Público",
    "Automobile":            "Carro",
    "Walking":               "A Pé",
    "Motorbike":             "Moto",
    "Bike":                  "Bicicleta",
}

# Mapeamento das variáveis de hábito
COL_MAP = {
    "Frequência de Exercício (FAF)": "FAF",
    "Consumo de Água (CH2O)":        "CH2O",
    "Consumo de Vegetais (FCVC)":    "FCVC",
    "Refeições por Dia (NCP)":       "NCP",
    "Tempo em Telas (TUE)":          "TUE",
}

# Macro-grupos de obesidade usados em múltiplos gráficos do dashboard
# Centralizado aqui para garantir consistência em todos os blocos
import unicodedata as _ud_global
def _rm_acento(s):
    return ''.join(c for c in _ud_global.normalize('NFD', s)
                   if _ud_global.category(c) != 'Mn')

GRUPO_MAP = {
    "Peso Insuficiente":  "Peso Saudavel",
    "Peso Normal":        "Peso Saudavel",
    "Sobrepeso Nivel I":  "Sobrepeso",
    "Sobrepeso Nivel II": "Sobrepeso",
    "Obesidade Tipo I":   "Obeso",
    "Obesidade Tipo II":  "Obeso",
    "Obesidade Tipo III": "Obeso",
}
GRUPO_MAP_NORM = {_rm_acento(k): v for k, v in GRUPO_MAP.items()}

GRUPO_COLORS = {
    "Peso Saudavel": "#a8c4e0",
    "Sobrepeso":     "#9aa4b2",
    "Obeso":         "#d96b6b",
}
GRUPO_ORDER = ["Peso Saudavel", "Sobrepeso", "Obeso"]

# Layout base reutilizável para todos os gráficos Plotly
# Fundo transparente para herdar o tema escuro do Streamlit
LAYOUT_BASE = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font_color="#c5cae9",
    font_family="DM Sans",
    margin=dict(t=10, b=10, l=0, r=0),
)

# Estilo de grade sutil para eixos dos gráficos
GRID = dict(showgrid=True, gridcolor="#1e2130")

# =============================================================================
# 3. CARREGAMENTO E PRÉ-PROCESSAMENTO DOS DADOS
# =============================================================================

@st.cache_data
def load_data():
    """
    Carrega o dataset Obesity.csv e aplica pré-processamento inicial.

    Tenta múltiplos caminhos para compatibilidade com diferentes ambientes
    (local, dentro do container Docker, subpastas do projeto).

    Transformações aplicadas:
    - Calcula a coluna BMI  → Weight / Height²
    - Converte Obesity para Categorical ordenado
    - Adiciona coluna 'Obesidade' com rótulos em português
    - Adiciona coluna 'Gênero' traduzida (Male/Female → Masculino/Feminino)
    - Adiciona coluna 'Histórico Familiar' traduzida (yes/no → Com/Sem Histórico)

    Returns
    -------
    pd.DataFrame ou None se nenhum caminho for encontrado.
    """
    paths = [
        "./Obesity.csv",
        "../train/Obesity.csv",
        "train/Obesity.csv",
    ]
    for p in paths:
        try:
            df = pd.read_csv(p)

            # Engenharia de feature: IMC calculado a partir de peso e altura
            df["BMI"] = (df["Weight"] / (df["Height"] ** 2)).round(2)

            # Categoria ordenada para ordenação correta nos gráficos
            df["Obesity"] = pd.Categorical(
                df["Obesity"], categories=OBESITY_ORDER, ordered=True
            )

            # Colunas auxiliares em português para uso nos gráficos
            df["Obesidade"] = pd.Categorical(
                df["Obesity"].map(OBESITY_PT),
                categories=OBESITY_ORDER_PT,
                ordered=True,
            )
            df["Gênero"] = df["Gender"].map({"Male": "Masculino", "Female": "Feminino"})
            df["Histórico Familiar"] = df["family_history"].map(
                {"yes": "Com Histórico", "no": "Sem Histórico"}
            )
            return df

        except FileNotFoundError:
            continue

    return None  # nenhum caminho encontrado → fallback para upload manual


df_raw = load_data()

# =============================================================================
# 4. FALLBACK DE UPLOAD (sem filtros interativos)
# =============================================================================

# Se o CSV não foi encontrado automaticamente, exibe opção de upload na sidebar
if df_raw is None:
    with st.sidebar:
        st.warning("CSV não encontrado automaticamente.")
        uploaded = st.file_uploader("Faça upload do Obesity.csv", type="csv")
        if uploaded:
            df_raw = pd.read_csv(uploaded)
            df_raw["BMI"] = (df_raw["Weight"] / (df_raw["Height"] ** 2)).round(2)
            df_raw["Obesity"] = pd.Categorical(
                df_raw["Obesity"], categories=OBESITY_ORDER, ordered=True
            )
            df_raw["Obesidade"] = pd.Categorical(
                df_raw["Obesity"].map(OBESITY_PT), categories=OBESITY_ORDER_PT, ordered=True
            )
            df_raw["Gênero"] = df_raw["Gender"].map({"Male": "Masculino", "Female": "Feminino"})
            df_raw["Histórico Familiar"] = df_raw["family_history"].map(
                {"yes": "Com Histórico", "no": "Sem Histórico"}
            )
        else:
            st.stop()

# =============================================================================
# 5. DATAFRAME COMPLETO (sem filtragem)
# =============================================================================

# Usa o dataset completo — sem filtros aplicados
df = df_raw.copy()

# ── Cabeçalho da página ───────────────────────────────────────────────────────
st.markdown("# Dashboard · Análise de Obesidade")
st.markdown(f"*{len(df):,} registros · 17 variáveis*")
st.markdown("---")

# =============================================================================
# 6. KPIs — MÉTRICAS RESUMIDAS
# =============================================================================

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    # Total de registros após filtragem
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{len(df):,}</div>
        <div class="metric-label">Registros</div></div>""", unsafe_allow_html=True)

with k2:
    # Percentual de pessoas com algum grau de obesidade (Obesity_Type_*)
    obesos = df["Obesity"].astype(str).str.startswith("Obesity").sum()
    pct = obesos / len(df) * 100
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{pct:.1f}%</div>
        <div class="metric-label">Com Obesidade</div></div>""", unsafe_allow_html=True)

with k3:
    # IMC médio do grupo filtrado
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{df['BMI'].mean():.1f}</div>
        <div class="metric-label">IMC Médio</div></div>""", unsafe_allow_html=True)

with k4:
    # Idade média do grupo filtrado
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{df['Age'].mean():.1f}</div>
        <div class="metric-label">Idade Média</div></div>""", unsafe_allow_html=True)

with k5:
    # Percentual com histórico familiar de obesidade
    hist_pct = df["family_history"].eq("yes").sum() / len(df) * 100
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{hist_pct:.1f}%</div>
        <div class="metric-label">Hist. Familiar</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# 7. GRÁFICOS
# =============================================================================

# ── 7.1 Distribuição por classe de obesidade + Distribuição por gênero ────────
col_a, col_b = st.columns([2, 1])

with col_a:
    st.markdown('<p class="section-title">Distribuição por Classe de Obesidade</p>', unsafe_allow_html=True)

    # Contagem de pessoas por classe, na ordem canônica
    counts = (
        df["Obesidade"].value_counts()
        .reindex(OBESITY_ORDER_PT)
        .dropna()
        .reset_index()
    )
    counts.columns = ["Classe", "Quantidade"]

    fig_classe = px.bar(
        counts, x="Classe", y="Quantidade",
        color="Classe",
        color_discrete_map=OBESITY_COLORS_PT,
        text="Quantidade",
        labels={"Classe": "", "Quantidade": "Pessoas"},
    )
    fig_classe.update_traces(textposition="outside", marker_line_width=0)
    fig_classe.update_layout(**LAYOUT_BASE, showlegend=False,
                             yaxis=dict(**GRID), xaxis=dict(tickangle=-20))
    st.plotly_chart(fig_classe, use_container_width=True)

with col_b:
    st.markdown('<p class="section-title">Distribuição por Gênero</p>', unsafe_allow_html=True)

    # Barras simples: Masculino (azul pastel) e Feminino (vermelho pastel)
    gen_counts = df["Gênero"].value_counts().reset_index()
    gen_counts.columns = ["Gênero", "Quantidade"]

    fig_gen = px.bar(
        gen_counts, x="Gênero", y="Quantidade",
        color="Gênero",
        color_discrete_map={"Masculino": "#a8c4e0", "Feminino": "#d96b6b"},
        text="Quantidade",
        labels={"Gênero": "", "Quantidade": "Pessoas"},
    )
    fig_gen.update_traces(textposition="outside", marker_line_width=0, width=0.4)
    fig_gen.update_layout(**LAYOUT_BASE, showlegend=False, yaxis=dict(**GRID))
    st.plotly_chart(fig_gen, use_container_width=True)

# ── 7.2 Obesidade por Sexo + Scatter Peso × Altura ───────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<p class="section-title">Obesidade por Sexo</p>', unsafe_allow_html=True)

    # Barras agrupadas: distribuição das classes de obesidade separada por gênero
    # Permite identificar se homens e mulheres diferem nos padrões de obesidade
    sexo_cross = (
        df.groupby(["Gênero", "Obesidade"], observed=True)
        .size()
        .reset_index(name="Quantidade")
    )
    fig_sexo = px.bar(
        sexo_cross, x="Obesidade", y="Quantidade",
        color="Gênero",
        barmode="group",
        color_discrete_map={"Masculino": "#a8c4e0", "Feminino": "#d96b6b"},
        category_orders={"Obesidade": OBESITY_ORDER_PT},
        labels={"Quantidade": "Pessoas", "Obesidade": "", "Gênero": ""},
        text="Quantidade",
    )
    fig_sexo.update_traces(textposition="outside", textfont_size=10)
    fig_sexo.update_layout(**LAYOUT_BASE,
                           legend=dict(bgcolor="rgba(0,0,0,0)"),
                           yaxis=dict(**GRID), xaxis=dict(tickangle=-20))
    st.plotly_chart(fig_sexo, use_container_width=True)

with col_d:
    st.markdown('<p class="section-title">Peso × Altura por Classe</p>', unsafe_allow_html=True)

    # Scatter com amostra de até 800 pontos para não sobrecarregar a renderização
    # Permite identificar clusters e sobreposições entre classes
    amostra = df.sample(min(len(df), 800), random_state=42)
    fig_scat = px.scatter(
        amostra, x="Height", y="Weight",
        color="Obesidade",
        color_discrete_map=OBESITY_COLORS_PT,
        category_orders={"Obesidade": OBESITY_ORDER_PT},
        opacity=0.75,
        labels={"Height": "Altura (m)", "Weight": "Peso (kg)", "Obesidade": "Classe"},
    )
    fig_scat.update_layout(**LAYOUT_BASE,
                           legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
                           xaxis=dict(**GRID), yaxis=dict(**GRID))
    st.plotly_chart(fig_scat, use_container_width=True)

# ── 7.3 Histograma de Idade + Histograma de IMC ───────────────────────────────
col_e, col_f = st.columns(2)

with col_e:
    st.markdown('<p class="section-title">Distribuição de Idade e Classe de Obesidade</p>', unsafe_allow_html=True)

    # Agrupa idades em faixas de 5 anos e as classes em 3 macro-grupos
    # (Peso Saudavel, Sobrepeso, Obeso) para leitura mais clara do gráfico
    _age_min = int(df["Age"].min())
    _age_max = int(df["Age"].max())
    _start   = (_age_min // 5) * 5
    _bins    = list(range(_start, _age_max + 6, 5))
    _labels  = [f"{b}-{b+4}" for b in _bins[:-1]]

    df_age = df.copy()
    df_age["Faixa Etaria"] = pd.cut(
        df_age["Age"], bins=_bins, right=False, labels=_labels
    ).astype(str)
    df_age["Obesidade_str"] = df_age["Obesidade"].astype(str)
    df_age["Grupo"] = df_age["Obesidade_str"].apply(_rm_acento).map(GRUPO_MAP_NORM)

    age_grouped = (
        df_age.groupby(["Faixa Etaria", "Grupo"], observed=True)
        .size()
        .reset_index(name="Quantidade")
    )
    age_grouped["Faixa Etaria"] = pd.Categorical(
        age_grouped["Faixa Etaria"], categories=_labels, ordered=True
    )
    age_grouped["Grupo"] = pd.Categorical(
        age_grouped["Grupo"], categories=GRUPO_ORDER, ordered=True
    )
    age_grouped = age_grouped.sort_values("Faixa Etaria")

    fig_age = px.bar(
        age_grouped, x="Faixa Etaria", y="Quantidade",
        color="Grupo",
        barmode="stack",
        color_discrete_map=GRUPO_COLORS,
        category_orders={"Grupo": GRUPO_ORDER},
        labels={"Faixa Etaria": "Faixa Etaria", "Quantidade": "Pessoas", "Grupo": ""},
    )
    fig_age.update_layout(**LAYOUT_BASE,
                          legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
                          yaxis=dict(**GRID), xaxis=dict(tickangle=-20))
    st.plotly_chart(fig_age, use_container_width=True)

with col_f:
    st.markdown('<p class="section-title">Distribuição de IMC</p>', unsafe_allow_html=True)

    # Histograma de IMC empilhado por classe
    # Espera-se separação clara entre classes com IMC crescente
    fig_bmi = px.histogram(
        df, x="BMI", color="Obesidade",
        color_discrete_map=OBESITY_COLORS_PT,
        category_orders={"Obesidade": OBESITY_ORDER_PT},
        nbins=40, barmode="stack",
        labels={"BMI": "IMC", "count": "Pessoas", "Obesidade": "Classe"},
    )
    fig_bmi.update_layout(**LAYOUT_BASE,
                          legend=dict(bgcolor="rgba(0,0,0,0)", font_size=10),
                          yaxis=dict(**GRID))
    st.plotly_chart(fig_bmi, use_container_width=True)

# ── 7.4 Hábitos por grupo de obesidade — médias comparadas ──────────────────
st.markdown("---")
st.markdown('<p class="section-title">Hábitos por Grupo de Obesidade</p>', unsafe_allow_html=True)

df_grupo = df.copy()
df_grupo["Grupo"] = df_grupo["Obesidade"].astype(str).apply(_rm_acento).map(GRUPO_MAP_NORM)

# Calcula a média de cada hábito por grupo
HAB_COLS = list(COL_MAP.values())   # FAF, CH2O, FCVC, NCP, TUE
HAB_NOMES = list(COL_MAP.keys())

df_medias = (
    df_grupo.groupby("Grupo", observed=True)[HAB_COLS]
    .mean()
    .round(2)
    .reset_index()
)
df_medias["Grupo"] = pd.Categorical(df_medias["Grupo"], categories=GRUPO_ORDER, ordered=True)
df_medias = df_medias.sort_values("Grupo")

# Transforma para formato longo para o gráfico de barras agrupadas
df_long = df_medias.melt(id_vars="Grupo", var_name="Habito", value_name="Media")
df_long["Habito"] = df_long["Habito"].map(dict(zip(HAB_COLS, HAB_NOMES)))

fig_hab = px.bar(
    df_long, x="Habito", y="Media",
    color="Grupo",
    barmode="group",
    color_discrete_map=GRUPO_COLORS,
    category_orders={"Grupo": GRUPO_ORDER},
    text=df_long["Media"].round(2),
    labels={"Habito": "", "Media": "Media", "Grupo": ""},
)
fig_hab.update_traces(textposition="outside", textfont_size=10)
fig_hab.update_layout(**LAYOUT_BASE,
                      legend=dict(bgcolor="rgba(0,0,0,0)"),
                      yaxis=dict(**GRID),
                      xaxis=dict(tickangle=-15))
st.plotly_chart(fig_hab, use_container_width=True)

# ── 7.5 Meio de transporte + Histórico familiar × Obesidade ──────────────────
col_g, col_h = st.columns(2)

with col_g:
    st.markdown('<p class="section-title">Transporte × Grupo de Obesidade</p>', unsafe_allow_html=True)

    # Usa o mesmo GRUPO_MAP definido na seção de Hábitos para agrupar as classes
    # em Peso Saudavel, Sobrepeso e Obeso, mantendo consistência visual no dashboard
    df_transp = df.copy()
    df_transp["Grupo"] = df_transp["Obesidade"].astype(str).apply(_rm_acento).map(GRUPO_MAP_NORM)
    df_transp["Transporte"] = df_transp["MTRANS"].map(TRANSP_PT)

    transp_cross = (
        df_transp.groupby(["Transporte", "Grupo"], observed=True)
        .size()
        .reset_index(name="Quantidade")
    )
    transp_cross["Grupo"] = pd.Categorical(
        transp_cross["Grupo"], categories=GRUPO_ORDER, ordered=True
    )

    fig_transp = px.bar(
        transp_cross, x="Transporte", y="Quantidade",
        color="Grupo",
        barmode="stack",
        color_discrete_map=GRUPO_COLORS,
        category_orders={"Grupo": GRUPO_ORDER},
        labels={"Transporte": "", "Quantidade": "Pessoas", "Grupo": ""},
    )
    fig_transp.update_layout(**LAYOUT_BASE,
                             legend=dict(bgcolor="rgba(0,0,0,0)", font_size=11),
                             yaxis=dict(**GRID), xaxis=dict(tickangle=-15))
    st.plotly_chart(fig_transp, use_container_width=True)

with col_h:
    st.markdown('<p class="section-title">Histórico Familiar × Obesidade</p>', unsafe_allow_html=True)

    # Barras agrupadas: compara distribuição de classes entre quem tem
    # e quem não tem histórico familiar de obesidade
    hist_cross = (
        df.groupby(["Histórico Familiar", "Obesidade"], observed=True)
        .size()
        .reset_index(name="Quantidade")
    )

    fig_hist = px.bar(
        hist_cross, x="Obesidade", y="Quantidade",
        color="Histórico Familiar",
        barmode="group",
        color_discrete_map={"Com Histórico": "#a8c4e0", "Sem Histórico": "#d96b6b"},
        labels={"Quantidade": "Pessoas", "Obesidade": "", "Histórico Familiar": ""},
        category_orders={"Obesidade": OBESITY_ORDER_PT},
    )
    fig_hist.update_layout(**LAYOUT_BASE,
                           legend=dict(bgcolor="rgba(0,0,0,0)"),
                           yaxis=dict(**GRID), xaxis=dict(tickangle=-20))
    st.plotly_chart(fig_hist, use_container_width=True)