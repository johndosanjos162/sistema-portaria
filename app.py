import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# Conexão (Configurado nos Secrets do Streamlit Cloud)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- LOGIN SIMPLIFICADO ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso ao Sistema")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin123":
            st.session_state["autenticado"] = True
            st.rerun()
    st.stop()

st.title("🔏 Sistema de Controle de Acesso")

# --- REGISTRO DE ENTRADA ---
with st.expander("🔵 Registrar Nova Entrada"):
    cpf = st.text_input("CPF (somente números):")
    if cpf:
        res = supabase.table("pessoas").select("*").eq("cpf", cpf).execute()
        if res.data:
            p = res.data[0]
            st.write(f"Nome: {p['nome']} | Vínculo: {p['vinculo']}")
            destino = st.selectbox("Destino:", ["C.C", "UTI", "Pronto Socorro"])
            if st.button("Confirmar Entrada"):
                supabase.table("movimentacao").insert({
                    "cpf": cpf, "nome": p['nome'], "empresa": p['vinculo'], 
                    "destino": destino, "entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }).execute()
                st.success("Entrada registrada!")
                st.rerun()
        else:
            st.error("CPF não cadastrado.")

# --- PAINEL ---
st.subheader("📋 Movimentações Atuais")
dados = supabase.table("movimentacao").select("*").execute()
if dados.data:
    st.dataframe(pd.DataFrame(dados.data))

if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()
