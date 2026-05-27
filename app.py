import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import os

# --- CONFIGURAÇÃO ---
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
        
        # Funções do Sistema (Apenas Admin pode desligar/reiniciar)
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

    # 1. NOVO CADASTRO (Todos logados podem)
    with st.expander("➕ Adicionar Novo Colaborador"):
        col_a, col_b, col_c = st.columns(3)
        novo_cpf = col_a.text_input("CPF do Novo:", key="novo_cpf")
        novo_nome = col_b.text_input("Nome do Novo:", key="novo_nome")
        novo_vinculo = col_c.selectbox("Setor:", ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"], key="novo_vinculo")
        if st.button("Salvar Novo Cadastro"):
            if novo_cpf and novo_nome:
                supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo}).execute()
                st.success("Cadastro salvo!")
                st.rerun()

    # 2. REGISTRO DE ENTRADA (Todos logados podem)
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

    # 3. PAINEL DE STATUS (Todos logados podem)
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

    # 4. HISTÓRICO GERAL (Todos logados podem)
    with st.expander("🕒 Histórico Geral (Entradas e Saídas Concluídas)"):
        todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
        if todos_dados:
            st.dataframe(pd.DataFrame(todos_dados))
        if st.button("🚨 APAGAR TODO O HISTÓRICO"):
            if st.session_state.perfil == 'admin':
                supabase.table("movimentacao").delete().neq("id", 0).execute()
                st.rerun()
            else:
                st.error("Apenas o Administrador pode apagar o histórico.")

    # 5. GESTÃO DE EXCLUSÃO (APENAS ADMINISTRADOR)
    if st.session_state.perfil == 'admin':
        with st.expander("⚙️ Gestão de Cadastros (Excluir Pessoa)"):
            st.warning("⚠️ Esta área é restrita para administradores.")
            todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
            if todos_colaboradores:
                lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
                selecionado = st.selectbox("Selecione para excluir:", lista_nomes)
                cpf_selecionado = selecionado.split("(CPF: ")[1].replace(")", "")
                if st.button("Confirmar Exclusão"):
                    supabase.table("Pessoas").delete().eq("cpf", cpf_selecionado).execute()
                    st.success("Cadastro removido!")
                    st.rerun()
else:
    st.info("🔒 Por favor, faça login na barra lateral.")
