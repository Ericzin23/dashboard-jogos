import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import ast

# Função segura pra converter texto pra lista
def tentar_converter(valor):
    try:
        return ast.literal_eval(valor)
    except:
        return []

# Traduções de gêneros do inglês para português
TRADUCAO_GENEROS = {
    'Action': 'Ação',
    'Adventure': 'Aventura',
    'RPG': 'RPG',
    'Strategy': 'Estratégia',
    'Simulation': 'Simulação',
    'Sports': 'Esporte',
    'Puzzle': 'Quebra-cabeça',
    'Racing': 'Corrida',
    'Shooter': 'Tiro',
    'Platformer': 'Plataforma',
    'Fighting': 'Luta',
    'Horror': 'Terror'
    # Pode adicionar mais aqui
}

# Conexão com o banco (troque a senha se precisar)
engine = create_engine("mysql+pymysql://root:eric2705@localhost/jogos_db")

@st.cache_data
def carregar_dados():
    df = pd.read_sql("SELECT * FROM jogos", engine)
    df['genres'] = df['genres'].apply(tentar_converter)
    df['genres'] = df['genres'].apply(lambda lista: [TRADUCAO_GENEROS.get(g, g) for g in lista])
    df['team'] = df['team'].apply(tentar_converter)
    return df

df = carregar_dados()

st.set_page_config(page_title="Dashboard de Jogos", layout="wide")
st.title("🎮 Dashboard Interativo de Jogos")

st.sidebar.header("🔍 Filtros")

generos_disponiveis = sorted(set(g for lista in df.genres for g in lista))
genero_escolhido = st.sidebar.selectbox("Filtrar por Gênero", generos_disponiveis)

nota_minima = st.sidebar.slider("Nota mínima (rating)", 0.0, 5.0, 3.0, 0.1)
limite_jogos = st.sidebar.radio("Mostrar:", ["Todos os jogos", "Top 10 por nota"])

# Filtro dos dados
df_filtrado = df[
    df['genres'].apply(lambda x: genero_escolhido in x) &
    (df['rating'] >= nota_minima)
]

# Top 10 com aviso se tiver poucos
if limite_jogos == "Top 10 por nota":
    if len(df_filtrado) > 10:
        df_filtrado = df_filtrado.sort_values(by='rating', ascending=False).head(10)
    else:
        st.info(f"⚠️ Apenas {len(df_filtrado)} jogos encontrados com esses critérios.")

# Visão geral
st.markdown("### 📌 Visão Geral")
col1, col2 = st.columns(2)
col1.metric("🎮 Jogos encontrados", len(df_filtrado))
col2.metric("⭐ Nota média", round(df_filtrado['rating'].mean(), 2) if not df_filtrado.empty else "N/A")

# Gráfico de barras
st.markdown("### ⭐ Avaliação dos Jogos")
if not df_filtrado.empty:
    fig = px.bar(
        df_filtrado,
        x='title',
        y='rating',
        color='rating',
        labels={'title': 'Jogo', 'rating': 'Nota'},
        title="Ranking dos Jogos"
    )
    fig.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum jogo encontrado com os filtros selecionados.")

# Gráfico de pizza
st.markdown("### 🧩 Distribuição dos Gêneros")
if not df_filtrado.empty:
    generos_flat = pd.Series([g for sublist in df_filtrado.genres for g in sublist])
    generos_count = generos_flat.value_counts().head(10)
    fig_pie = px.pie(
        names=generos_count.index,
        values=generos_count.values,
        title="Distribuição dos Gêneros"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("Não há dados suficientes para gerar o gráfico de pizza.")
