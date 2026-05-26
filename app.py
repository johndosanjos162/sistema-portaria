import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# URL DO CSV PUBLICADO NO GOOGLE SHEETS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTjiiw8OFiPFZswRmxO3IDIqNT2jVi6q_fWQn37P0OLRfA-Dt5zWl2kzo5HifDGYSCHlUIbXXVp_H6Z/pub?output=csv"

# --- ESTADO DE SESSÃO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""

# --- FUNÇÃO PARA CARREGAR DADOS ---
@st.cache_data(ttl=60) # Atualiza o cache a cada 60 segundos
def carregar_dados():
    try:
        df = pd.read_csv(URL_CSV)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return None

# --- LÓGICA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso ao Sistema de Portaria")
    usuario = st.text_input("Username")
    senha = st.text_input("Password", type="password")
    
    if st.button("Entrar", use_container_width=True):
        if usuario == "admin" and senha == "admin123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "admin"
            st.rerun()
        elif usuario == "porteiro1" and senha == "hospital123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "porteiro1"
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🔏 Sistema de Controle de Acesso")
st.sidebar.write(f"Logado como: **{st.session_state['username']}**")

if st.sidebar.button("Sair do Sistema"):
    st.session_state["autenticado"] = False
    st.rerun()

# --- CARGA E EXIBIÇÃO DOS DADOS ---
st.subheader("📋 Monitoramento em Tempo Real")
df = carregar_dados()

if df is not None:
    st.dataframe(df, use_container_width=True)
else:
    st.warning("A planilha não retornou dados. Verifique se o arquivo está publicado na web.")
