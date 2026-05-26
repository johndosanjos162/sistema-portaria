import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# Conexão com Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- LOGIN ---
if "autenticado" not in st.session_state: 
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""

if not st.session_state["autenticado"]:
    st.subheader("🔐 Login")
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

# --- INTERFACE PRINCIPAL ---
st.title("🔏 Sistema de Controle de Acesso")
st.sidebar.write(f"Usuário: **{st.session_state['username']}**")

# 1. ABA DE CADASTRO (Apenas Admin)
if st.session_state["username"] == "admin":
    with st.expander("📝 Cadastrar Nova Pessoa no Sistema"):
        with st.form("form_cad"):
            n_cpf = st.text_input("CPF (Somente números):")
            n_nome = st.text_input("Nome Completo:")
            n_vinc = st.text_input("Vínculo/Empresa:")
            if st.form_submit_button("Salvar Cadastro"):
                supabase.table("pessoas").insert({"cpf": n_cpf, "nome": n_nome, "vinculo": n_vinc}).execute()
                st.success("Pessoa cadastrada!")

# 2. REGISTRO DE MOVIMENTAÇÃO
with st.expander("🔵 Registrar Entrada/Saída"):
    cpf_busca = st.text_input("Digite o CPF para iniciar:")
    if cpf_busca:
        res = supabase.table("pessoas").select("*").eq("cpf", cpf_busca).execute()
        if res.data:
            p = res.data[0]
            st.write(f"**Localizado:** {p['nome']} ({p['vinculo']})")
            destino = st.selectbox("Setor de Destino:", ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Onco"])
            
            col_a, col_b = st.columns(2)
            if col_a.button("Confirmar Entrada"):
                supabase.table("movimentacao").insert({
                    "cpf": cpf_busca, "nome": p['nome'], "empresa": p['vinculo'], 
                    "destino": destino, "entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }).execute()
                st.success("Entrada registrada!")
                st.rerun()
        else:
            st.error("CPF não encontrado. Solicite o cadastro ao Administrador.")

# 3. GERENCIAMENTO (Admin)
if st.session_state["username"] == "admin":
    st.markdown("---")
    st.subheader("⚙️ Painel de Controle (Admin)")
    c1, c2 = st.columns(2)
    with c1:
        del_cpf = st.text_input("Deletar Cadastro (CPF):")
        if st.button("Apagar Cadastro"):
            supabase.table("pessoas").delete().eq("cpf", del_cpf).execute()
            st.warning("Cadastro removido.")
    with c2:
        del_id = st.text_input("Apagar Registro Histórico (ID):")
        if st.button("Apagar Registro"):
            supabase.table("movimentacao").delete().eq("id", int(del_id)).execute()
            st.warning("Registro removido.")

# 4. PAINEL VISUAL
st.subheader("📋 Painel de Movimentação")
dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute()
if dados.data:
    st.dataframe(pd.DataFrame(dados.data), use_container_width=True)

if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()
