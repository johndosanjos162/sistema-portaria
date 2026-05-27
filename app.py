import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
import os

# --- CONFIGURAÇÃO E CONEXÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
senha_admin = st.secrets.get("ADMIN_PASSWORD", "senha_padrao_caso_nao_exista")
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- BARRA LATERAL: LOGIN E REINICIALIZAÇÃO ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    input_senha = st.text_input("Senha do Administrador:", type="password")
    
    # A lógica abaixo garante que o botão de reiniciar só funcione com a senha correta
    if st.button("🔄 Reiniciar Sistema"):
        if input_senha == senha_admin:
            st.warning("Senha correta. Reiniciando...")
            st.rerun()
        else:
            st.error("Senha de administrador necessária!")

st.title("🏥 Painel de Monitoramento - Portaria")

# --- 0. NOVO CADASTRO DE PESSOAS ---
with st.expander("➕ Adicionar Novo Colaborador"):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("CPF do Novo:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome do Novo:", key="novo_nome")
    novo_vinculo = col_c.selectbox("Setor/Vínculo:", ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"], key="novo_vinculo")
    
    if st.button("Salvar Novo Cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({
                "cpf": novo_cpf, 
                "nome": novo_nome, 
                "vinculo": novo_vinculo
            }).execute()
            st.success("Cadastro salvo com sucesso!")
            st.rerun()
        else:
            st.error("Preencha CPF e Nome!")

# --- 1. REGISTRO DE NOVA ENTRADA ---
with st.expander("🔵 Registrar Nova Entrada"):
    c1, c2 = st.columns([3, 1])
    cpf_input = c1.text_input("Digite o CPF do colaborador para entrada:")
    if c2.button("Adicionar Entrada"):
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'], 
                "nome": p[0]['nome'], 
                "setor_destino": p[0]['vinculo'],
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "data_saida": ""
            }).execute()
            st.success(f"{p[0]['nome']} entrou em {p[0]['vinculo']}!")
            st.rerun()
        else:
            st.error("CPF não cadastrado.")

# --- 2. PAINEL DE STATUS ---
st.subheader("📋 Pessoas Presentes (Aguardando Saída)")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    setores = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]
    abas = st.tabs(setores)

    for i, nome_setor in enumerate(setores):
        with abas[i]:
            presentes = [r for r in dados if r['setor_destino'] == nome_setor]
            if presentes:
                for pessoa in presentes:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    col1.write(f"**{pessoa['nome']}**")
                    col2.write(f"Entrada: {pessoa['data_entrada']}")
                    if col3.button("Registrar SAÍDA", key=f"saida_{pessoa['id']}"):
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", pessoa['id']).execute()
                        st.rerun()
            else:
                st.info("Setor vazio.")
else:
    st.write("Ninguém presente no momento.")

# --- 3. HISTÓRICO GERAL ---
with st.expander("🕒 Histórico Geral (Entradas e Saídas Concluídas)"):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        st.dataframe(pd.DataFrame(todos_dados))
    if st.button("🚨 APAGAR TODO O HISTÓRICO"):
        supabase.table("movimentacao").delete().neq("id", 0).execute()
        st.rerun()

# --- 4. GESTÃO DE CADASTROS ---
with st.expander("⚙️ Gestão de Cadastros (Excluir Pessoa)"):
    st.warning("⚠️ Cuidado: Esta ação apagará permanentemente o colaborador da base.")
    todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
    if todos_colaboradores:
        lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
        selecionado = st.selectbox("Selecione o colaborador para excluir:", lista_nomes)
        cpf_selecionado = selecionado.split("(CPF: ")[1].replace(")", "")
        if st.button(f"Confirmar Exclusão"):
            supabase.table("Pessoas").delete().eq("cpf", cpf_selecionado).execute()
            st.success("Cadastro removido!")
            st.rerun()
