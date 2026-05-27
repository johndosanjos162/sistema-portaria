import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)
st.set_page_config(page_title="Portaria Hospitalar", layout="wide")

# --- DESIGN "TOP" COM FUNDO TECNOLÓGICO ---
st.markdown("""
    <style>
    :root { --primary-color: #00ff41; --bg-color: #000000; }
    .stApp { 
        background-image: url("https://raw.githubusercontent.com/sua-conta/seu-repositorio/main/fghy.jpg"); 
        background-size: cover; 
        background-attachment: fixed;
    }
    h1, h3, p, label, .stMarkdown { color: #00ff41 !important; text-shadow: 1px 1px 2px black; }
    
    .st-expander { 
        background-color: rgba(0, 20, 0, 0.8) !important; 
        border: 1px solid #00ff41 !important; 
        border-radius: 12px !important; 
    }
    
    div.stButton > button { 
        background-color: #003300; color: #00ff41; border: 1px solid #00ff41; 
        border-radius: 8px; font-weight: bold; 
    }
    div.stButton > button:hover { background-color: #00ff41; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.title("🔐 Login de Acesso")
    senha = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar"):
        if senha == "fgxv4VP0/*":
            st.session_state.logado = True; st.session_state.perfil = "ADMIN"; st.rerun()
        elif senha == "JOHN123":
            st.session_state.logado = True; st.session_state.perfil = "VIGILANTE"; st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🏥 Painel de Monitoramento")
if st.button("Sair do Sistema"):
    st.session_state.logado = False; st.rerun()

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- 0. NOVO CADASTRO ---
with st.expander("➕ Adicionar Novo Colaborador"):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome:", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
    if st.button("Salvar Novo Cadastro"):
        supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "empresa": novo_empresa}).execute()
        st.success("Salvo!"); st.rerun()

# --- 1. ENTRADA E 1.1 SAÍDA ---
with st.expander("🔵 Registrar Entrada"):
    c1, c2, c3 = st.columns([2, 2, 1])
    cpf_in = c1.text_input("CPF:")
    setor = c2.selectbox("Destino:", setores_lista)
    if c3.button("Confirmar Entrada"):
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_in).execute().data
        if p:
            supabase.table("movimentacao").insert({"cpf": p[0]['cpf'], "nome": p[0]['nome'], "empresa": p[0].get('empresa', ''), "setor_destino": setor, "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), "data_saida": ""}).execute()
            st.rerun()

with st.expander("🔴 Registrar Saída"):
    c1, c2 = st.columns([3, 1])
    cpf_out = c1.text_input("CPF para saída:", key="out")
    if c2.button("Confirmar Saída"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_out).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
            st.rerun()

# --- 2. PAINEL DE STATUS ---
st.subheader("📋 Pessoas Presentes")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
if dados:
    aba_lista = st.tabs(setores_lista)
    for i, nome_setor in enumerate(setores_lista):
        with aba_lista[i]:
            for p in [r for r in dados if r['setor_destino'] == nome_setor]:
                c1, c2, c3 = st.columns([3, 3, 2])
                c1.write(f"**{p['nome']}**"); c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
                if c3.button("SAÍDA", key=f"s_{p['id']}"):
                    supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute(); st.rerun()

# --- 3. HISTÓRICO E GESTÃO ---
with st.expander("🕒 Histórico"):
    if st.button("🚨 APAGAR HISTÓRICO"):
        supabase.table("movimentacao").delete().neq("id", 0).execute(); st.rerun()
