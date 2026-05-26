import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# Conexão (Configurada nos Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- LOGIN ---
if "autenticado" not in st.session_state: 
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""

if not st.session_state["autenticado"]:
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

st.title("🔏 Sistema de Controle de Acesso")

# --- REGISTRO DE ENTRADA (Todos) ---
with st.expander("🔵 Registrar Entrada/Saída"):
    cpf = st.text_input("CPF:")
    if cpf:
        res = supabase.table("pessoas").select("*").eq("cpf", cpf).execute()
        if res.data:
            p = res.data[0]
            st.write(f"Nome: {p['nome']} | Vínculo: {p['vinculo']}")
            destino = st.selectbox("Destino:", ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Onco"])
            if st.button("Registrar Entrada"):
                supabase.table("movimentacao").insert({
                    "cpf": cpf, "nome": p['nome'], "empresa": p['vinculo'], 
                    "destino": destino, "entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }).execute()
                st.success("Entrada registrada!")
        else:
            st.error("CPF não cadastrado.")

# --- ÁREA DE ADMIN (Gestão de Dados) ---
if st.session_state["username"] == "admin":
    st.markdown("---")
    st.subheader("⚙️ Área do Administrador")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📝 Gerenciar Cadastros")
        cpf_del = st.text_input("CPF para deletar cadastro:")
        if st.button("Deletar Cadastro"):
            supabase.table("pessoas").delete().eq("cpf", cpf_del).execute()
            st.warning("Cadastro removido!")

    with col2:
        st.write("### 🗑️ Gerenciar Histórico")
        id_del = st.text_input("ID do registro para deletar:")
        if st.button("Deletar Registro Específico"):
            supabase.table("movimentacao").delete().eq("id", int(id_del)).execute()
            st.warning("Registro removido!")

# --- PAINEL DE MONITORAMENTO ---
st.subheader("📋 Movimentações")
dados = supabase.table("movimentacao").select("*").execute()
if dados.data:
    df = pd.DataFrame(dados.data)
    st.dataframe(df, use_container_width=True)

if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()
