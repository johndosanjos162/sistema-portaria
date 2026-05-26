import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- CONTROLE DE ACESSO (LOGIN) ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.title("🔐 Login de Acesso")
    senha = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Entrar"):
        if senha == "fgxv4VP0/*":
            st.session_state.logado = True
            st.session_state.perfil = "ADMIN"
            st.rerun()
        elif senha == "JOHN123":
            st.session_state.logado = True
            st.session_state.perfil = "VIGILANTE"
            st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🏥 Painel de Monitoramento - Portaria")
if st.button("Sair do Sistema"):
    st.session_state.logado = False
    st.session_state.perfil = ""
    st.rerun()

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- 0. NOVO CADASTRO ---
with st.expander("➕ Adicionar Novo Colaborador"):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("CPF do Novo:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome do Novo:", key="novo_nome")
    novo_vinculo = col_c.selectbox("Setor/Vínculo:", setores_lista, key="novo_vinculo")
    
    if st.button("Salvar Novo Cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo}).execute()
            st.success("Cadastro salvo!")
            st.rerun()

# --- 1. REGISTRO DE ENTRADA ---
with st.expander("🔵 Registrar Nova Entrada"):
    c1, c2 = st.columns([3, 1])
    cpf_input = c1.text_input("Digite o CPF para entrada:")
    if c2.button("Adicionar Entrada"):
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'], "nome": p[0]['nome'], "setor_destino": p[0]['vinculo'],
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), "data_saida": ""
            }).execute()
            st.success(f"{p[0]['nome']} entrou!")
            st.rerun()
        else:
            st.error("CPF não cadastrado.")

# --- 2. PAINEL DE STATUS ---
st.subheader("📋 Pessoas Presentes")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
if dados:
    abas = st.tabs(setores_lista)
    for i, nome_setor in enumerate(setores_lista):
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
    st.info("Nenhum registro encontrado.")

# --- 3. HISTÓRICO ---
with st.expander("🕒 Histórico Geral"):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados: st.dataframe(pd.DataFrame(todos_dados))
    if st.button("🚨 APAGAR TODO O HISTÓRICO"):
        supabase.table("movimentacao").delete().neq("id", 0).execute()
        st.rerun()

# --- 4. GESTÃO (APENAS ADMIN) ---
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros (Exclusivo Admin)"):
        todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
        if todos_colaboradores:
            lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
            selecionado = st.selectbox("Selecione para excluir:", lista_nomes)
            if st.button("Confirmar Exclusão"):
                cpf_excluir = selecionado.split("(CPF: ")[1].replace(")", "")
                supabase.table("Pessoas").delete().eq("cpf", cpf_excluir).execute()
                st.success("Cadastro removido!")
                st.rerun()
