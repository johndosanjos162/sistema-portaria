import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔐 Acesso ao Sistema")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if user == "admin" and pwd == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos!")
    st.stop()

st.sidebar.title("Menu")
if st.sidebar.button("Sair"):
    st.session_state.logado = False
    st.rerun()

st.title("🏥 Controle de Acesso - Portaria")

with st.expander("⚙️ Gestão de Cadastros"):
    c_cpf = st.text_input("CPF do Funcionário:")
    c_nome = st.text_input("Nome do Funcionário:")
    c_vinculo = st.text_input("Setor de Destino/Vínculo:")
    if st.button("Salvar Novo Cadastro"):
        try:
            # Nota: Usando "Pessoas" com P maiúsculo como o banco pediu
            supabase.table("Pessoas").insert({"cpf": c_cpf, "nome": c_nome, "vinculo": c_vinculo}).execute()
            st.success("Funcionário cadastrado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao cadastrar: {e}")

with st.expander("🔵 Registrar Movimentação"):
    busca_cpf = st.text_input("Digite o CPF para movimentar:")
    if st.button("Buscar"):
        # Nota: Usando "Pessoas" com P maiúsculo como o banco pediu
        p = supabase.table("Pessoas").select("*").eq("cpf", busca_cpf).execute().data
        if p:
            st.write(f"Funcionário encontrado: {p[0]['nome']}")
            if st.button("Confirmar Entrada"):
                try:
                    # Nota: Usando "movimentacao" com tudo minúsculo
                    supabase.table("movimentacao").insert({
                        "cpf": busca_cpf,
                        "nome": p[0]['nome'],
                        "setor_destino": p[0]['vinculo'],
                        "entrada": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }).execute()
                    st.success("Movimentação registrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao registrar: {e}")
        else:
            st.warning("CPF não encontrado.")

st.subheader("📋 Histórico de Acessos")
try:
    # Nota: Usando "movimentacao" com tudo minúsculo
    dados = supabase.table("movimentacao").select("*").execute().data
    if dados:
        df = pd.DataFrame(dados)
        st.dataframe(df)
        
        id_del = st.number_input("ID para remover do histórico:", step=1)
        if st.button("Apagar registro selecionado"):
            supabase.table("movimentacao").delete().eq("id", id_del).execute()
            st.rerun()
    else:
        st.info("Nenhuma movimentação registrada até o momento.")
except Exception as e:
    st.error("Erro ao carregar histórico.")
