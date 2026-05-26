import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO E CONEXÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")
st.title("🏥 Painel de Monitoramento - Portaria")

# --- 1. REGISTRO DE NOVA ENTRADA ---
with st.expander("🔵 Registrar Nova Entrada"):
    c1, c2 = st.columns([3, 1])
    cpf_input = c1.text_input("Digite o CPF do colaborador:")
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

# --- 2. PAINEL DE STATUS (QUEM ESTÁ DENTRO) ---
st.subheader("📋 Pessoas Presentes (Aguardando Saída)")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    setores = ["Centro Cirúrgico", "Engenharia Clínica", "Manutenção", "Prestador de Serviço"]
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

# --- 4. GESTÃO DE CADASTROS (EXCLUSÃO) ---
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
