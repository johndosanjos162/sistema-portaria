import streamlit as st
import pandas as pd

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# ID DA PLANILHA (FIXO)
ID_PLANILHA = "1-j0vduIJNpbKthmabUA7Ud8ZnMLazq4RBkhLodf190M"
# URL PARA EXPORTAÇÃO CSV (O G-Sheets precisa estar "Publicado na Web")
URL_CSV = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/export?format=csv"

# --- ESTADO DE SESSÃO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""

# --- FUNÇÃO PARA CARREGAR DADOS ---
@st.cache_data(ttl=600) # Atualiza o cache a cada 10 minutos
def carregar_dados():
    try:
        df = pd.read_csv(URL_CSV)
        return df
    except Exception as e:
        return None

# --- LÓGICA DE LOGIN ---
if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso ao Sistema de Portaria")
    usuario = st.text_input("Username")
    senha = st.text_input("Password", type="password")
    
    if st.button("Entrar"):
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

if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()

# --- CARGA E EXIBIÇÃO DOS DADOS ---
st.subheader("📋 Monitoramento em Tempo Real")
df = carregar_dados()

if df is not None:
    st.dataframe(df, use_container_width=True)
else:
    st.error("Erro ao carregar a planilha. Verifique se ela está publicada na web.")
