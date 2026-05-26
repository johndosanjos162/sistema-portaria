import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# Conexão
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- LOGIN ---
if "autenticado" not in st.session_state: 
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""

if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso ao Sistema")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "admin"
            st.rerun()
        elif u == "porteiro1" and p == "hospital123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "porteiro1"
            st.rerun()
    st.stop()

# --- INTERFACE ---
st.title("🔏 Sistema de Controle de Acesso")
st.sidebar.write(f"Logado como: **{st.session_state['username']}**")

if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()

# --- ÁREA DO ADMIN (Cadastro) ---
# Esta parte aparece apenas se o usuário for "admin"
if st.session_state["username"] == "admin":
    st.subheader("📝 Cadastro de Pessoas")
    with st.form("form_cadastro"):
        c_cpf = st.text_input("CPF:")
        c_nome = st.text_input("Nome:")
        c_vinc = st.text_input("Vínculo/Empresa:")
        if st.form_submit_button("Salvar no Banco"):
            supabase.table("pessoas").insert({
                "cpf": c_cpf, "nome": c_nome, "vinculo": c_vinc
            }).execute()
            st.success("Cadastrado com sucesso!")

# --- REGISTRO DE ENTRADA (Todos podem ver) ---
st.markdown("---")
st.subheader("🔵 Registrar Nova Entrada")
cpf_busca = st.text_input("CPF para buscar:")
if cpf_busca:
    res = supabase.table("pessoas").select("*").eq("cpf", cpf_busca).execute()
    if res.data:
        p = res.data[0]
        st.write(f"👤 **{p['nome']}** | **{p['vinculo']}**")
        if st.button("Confirmar Entrada"):
            supabase.table("movimentacao").insert({
                "cpf": cpf_busca, "nome": p['nome'], "empresa": p['vinculo'], 
                "destino": "Portaria", "entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }).execute()
            st.success("Entrada registrada!")
    else:
        st.error("CPF não encontrado no cadastro.")
