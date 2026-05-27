import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
# Certifique-se de que ADMIN_PASSWORD e VIGILANTE_PASSWORD estejam no seu secrets.toml
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
senha_admin = st.secrets["ADMIN_PASSWORD"]
senha_vigilante = st.secrets["VIGILANTE_PASSWORD"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- CONTROLE DE SESSÃO ---
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.perfil = None 

with st.sidebar:
    st.header("🔑 Acesso ao Sistema")
    if not st.session_state.logado:
        senha_input = st.text_input("Digite sua senha:", type="password")
        if st.button("Entrar"):
            if senha_input == senha_admin:
                st.session_state.logado = True
                st.session_state.perfil = 'admin'
                st.rerun()
            elif senha_input == senha_vigilante:
                st.session_state.logado = True
                st.session_state.perfil = 'vigilante'
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.write(f"Logado como: **{st.session_state.perfil.upper()}**")
        if st.button("Sair"):
            st.session_state.logado = False
            st.session_state.perfil = None
            st.rerun()
        
        # Apenas Admin tem acesso a funções de sistema
        if st.session_state.perfil == 'admin':
            st.divider()
            st.subheader("⚙️ Funções Administrativas")
            if st.button("🔄 Reiniciar Sistema"):
                st.rerun()
            if st.button("🛑 Desligar Servidor"):
                os._exit(0)

# --- APLICATIVO PRINCIPAL ---
if st.session_state.logado:
    st.title("🏥 Painel de Monitoramento - Portaria")

    # 1. ADICIONAR COLABORADOR (Todos)
    with st.expander("➕ Adicionar Novo Colaborador"):
        col_a, col_b, col_c = st.columns(3)
        novo_cpf = col_a.text_input("CPF do Novo:", key="novo_cpf")
        novo_nome = col_
