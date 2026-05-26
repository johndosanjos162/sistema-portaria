import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso ao Sistema")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if user == "admin" and pwd == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos!")
    st.stop()

st.sidebar.title("Menu")
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

st.title("🏥 Controle de Acesso - Portaria")

st.write("Bem-vindo ao sistema principal!")
