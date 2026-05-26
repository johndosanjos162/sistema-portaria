import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria", layout="wide")

st.title("🏥 Controle de Acesso - Portaria")

# 1. Registro de Movimentação
with st.expander("🔵 Registrar Entrada / Saída"):
    busca_cpf = st.text_input("CPF do colaborador:")
    if st.button("Buscar Pessoa"):
        p = supabase.table("Pessoas").select("*").eq("cpf", busca_cpf).execute().data
        if p:
            st.session_state.p_atual = p[0]
        else:
            st.warning("CPF não encontrado.")

    if "p_atual" in st.session_state:
        p = st.session_state.p_atual
        st.write(f"**Nome:** {p['nome']} | **Setor:** {p['vinculo']}")
        
        c1, c2 = st.columns(2)
        if c1.button("Registrar ENTRADA"):
            supabase.table("movimentacao").insert({
                "cpf": p['cpf'], "nome": p['nome'], "setor_destino": p['vinculo'],
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), "data_saida": ""
            }).execute()
            st.success("Entrada registrada!")
            
        if c2.button("Registrar SAÍDA"):
            reg = supabase.table("movimentacao").select("*").eq("cpf", p['cpf']).eq("data_saida", "").execute().data
            if reg:
                supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
                st.success("Saída registrada!")
            else:
                st.error("Nenhuma entrada aberta encontrada.")

# 2. Listagem por Setor (As "Pastas")
st.subheader("📋 Acessos por Setor")
dados = supabase.table("movimentacao").select("*").execute().data

if dados:
    df = pd.DataFrame(dados)
    # Lista de setores (incluindo Prestador)
    setores = ["Centro Cirúrgico", "Engenharia Clínica", "Manutenção", "Prestador de Serviço"]
    abas = st.tabs(setores)
    
    for i, setor in enumerate(abas):
        with setor:
            # Filtra o dataframe da aba atual
            df_setor = df[df['setor_destino'] == setores[i]]
            if not df_setor.empty:
                st.dataframe(df_setor[['nome', 'setor_destino', 'data_entrada', 'data_saida']])
                
                # Exclusão Manual
                id_del = st.number_input(f"ID para apagar em {setores[i]}:", key=f"id_{i}")
                if st.button(f"Apagar ID {id_del}", key=f"del_{i}"):
                    supabase.table("movimentacao").delete().eq("id", id_del).execute()
                    st.rerun()
            else:
                st.info(f"Nenhum registro em {setores[i]}")

    # Exclusão Geral
    if st.button("🚨 APAGAR TODO O HISTÓRICO"):
        for id_item in df['id']:
            supabase.table("movimentacao").delete().eq("id", id_item).execute()
        st.rerun()
