import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Portaria", layout="centered")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.subheader("Login")
    user = st.text_input("Usuário")
    pw = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if user == "admin" and pw == "admin123":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")
    st.stop()

st.title("Sistema de Portaria")
if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()

st.write("Bem-vindo ao sistema!")
