import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# Lógica de Login simplificada
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    u = st.text_input("Usuário"); p = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin": st.session_state.auth = True; st.rerun()
    st.stop()

st.title("🏥 Controle de Acesso")

# --- CADASTRO E GESTÃO (ADMIN) ---
with st.expander("⚙️ Gestão de Pessoas (Admin)"):
    tab1, tab2 = st.tabs(["Novo Cadastro", "Excluir Cadastro"])
    with tab1:
        c_cpf = st.text_input("CPF:"); c_nome = st.text_input("Nome:"); c_vin = st.text_input("Setor/Vínculo")
        if st.button("Salvar Pessoa"):
            supabase.table("pessoas").insert({"cpf": c_cpf, "nome": c_nome, "vinculo": c_vin}).execute()
            st.success("Cadastrado!")
    with tab2:
        d_cpf = st.text_input("Digite o CPF para excluir:")
        if st.button("Confirmar Exclusão"):
            supabase.table("pessoas").delete().eq("cpf", d_cpf).execute()
            st.warning("Cadastro removido!")

# --- REGISTRO DE MOVIMENTAÇÃO ---
with st.expander("🔵 Registrar Movimentação"):
    busca = st.text_input("Buscar CPF:")
    if busca:
        p = supabase.table("pessoas").select("*").eq("cpf", busca).execute().data
        if p:
            st.write(f"Usuário: {p[0]['nome']}")
            destino = st.selectbox("Destino", ["UTI", "C.C", "CME"])
            if st.button("Registrar Entrada"):
                supabase.table("movimentacao").insert({
                    "cpf": busca, "nome": p[0]['nome'], "setor_destino": destino, 
                    "entrada": datetime.now().strftime("%d/%m/%Y %H:%M")
                }).execute()
                st.success("Entrada salva!")

# --- HISTÓRICO ---
st.subheader("📋 Histórico de Movimentações")
hist = supabase.table("movimentacao").select("*").execute().data
if hist:
    df = pd.DataFrame(hist)
    st.dataframe(df)
    
    del_id = st.text_input("ID do registro para deletar do histórico:")
    if st.button("Apagar este registro"):
        supabase.table("movimentacao").delete().eq("id", int(del_id)).execute()
        st.rerun()
