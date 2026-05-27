import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
senha_admin = st.secrets["ADMIN_PASSWORD"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- CONTROLE DE SESSÃO (LOGIN) ---
if "logado" not in st.session_state:
    st.session_state.logado = False

with st.sidebar:
    st.header("🔑 Acesso ao Sistema")
    if not st.session_state.logado:
        senha_input = st.text_input("Digite a senha de acesso:", type="password")
        if st.button("Entrar"):
            if senha_input == senha_admin:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.success("Administrador autenticado.")
        if st.button("Sair"):
            st.session_state.logado = False
            st.rerun()
        
        st.divider()
        st.header("⚙️ Funções Administrativas")
        if st.button("🔄 Reiniciar Sistema"):
            st.rerun()
        if st.button("🛑 Desligar Servidor"):
            os._exit(0)

# --- APLICATIVO PRINCIPAL (SÓ APARECE SE LOGADO) ---
if st.session_state.logado:
    st.title("🏥 Painel de Monitoramento - Portaria")

    # --- 0. NOVO CADASTRO ---
    with st.expander("➕ Adicionar Novo Colaborador"):
        col_a, col_b, col_c = st.columns(3)
        novo_cpf = col_a.text_input("CPF do Novo:", key="novo_cpf")
        novo_nome = col_b.text_input("Nome do Novo:", key="novo_nome")
        novo_vinculo = col_c.selectbox("Setor/Vínculo:", ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"], key="novo_vinculo")
        
        if st.button("Salvar Novo Cadastro"):
            if novo_cpf and novo_nome:
                supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo}).execute()
                st.success("Cadastro salvo!")
                st.rerun()

    # --- 1. REGISTRO DE ENTRADA ---
    with st.expander("🔵 Registrar Nova Entrada"):
        c1, c2 = st.columns([3, 1])
        cpf_input = c1.text_input("CPF para entrada:")
        if c2.button("Adicionar Entrada"):
            p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
            if p:
                supabase.table("movimentacao").insert({
                    "cpf": p[0]['cpf'], "nome": p[0]['nome'], "setor_destino": p[0]['vinculo'],
                    "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), "data_saida": ""
                }).execute()
                st.rerun()
            else:
                st.error("CPF não cadastrado.")

    # --- 2. PAINEL DE STATUS ---
    st.subheader("📋 Pessoas Presentes")
    dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
    if dados:
        setores = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]
        abas = st.tabs(setores)
        for i, nome_setor in enumerate(setores):
            with abas[i]:
                presentes = [r for r in dados if r['setor_destino'] == nome_setor]
                for pessoa in presentes:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    col1.write(f"**{pessoa['nome']}**")
                    col2.write(f"Entrada: {pessoa['data_entrada']}")
                    if col3.button("Registrar SAÍDA", key=f"saida_{pessoa['id']}"):
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", pessoa['id']).execute()
                        st.rerun()
else:
    st.info("🔒 Por favor, faça login na barra lateral para acessar o sistema.")
