import streamlit as st
import pandas as pd
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portaria Hospitalar", layout="centered")

# ESTADO DE AUTENTICAÇÃO
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""

# TELA DE LOGIN (BLOQUEIA O ACESSO)
if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso ao Sistema de Portaria")
    usuario_input = st.text_input("Username")
    senha_input = st.text_input("Password", type="password")
    if st.button("Entrar", use_container_width=True):
        if usuario_input == "admin" and senha_input == "admin123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "admin"
            st.rerun()
        elif usuario_input == "porteiro1" and senha_input == "hospital123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "porteiro1"
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# SISTEMA PRINCIPAL (APÓS LOGIN)
st.title("🔏 Sistema de Controle de Acesso")
if st.sidebar.button("Sair do Sistema"):
    st.session_state["autenticado"] = False
    st.rerun()

st.success(f"Logado como: {st.session_state['username']}")
st.subheader("📋 Painel de Monitoramento")
st.write("O sistema está online! (Integre sua base de dados via st.connection para ver os registros reais).")
