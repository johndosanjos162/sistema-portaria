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
# SUBSTITUA O LINK ABAIXO PELO LINK REAL DA SUA IMAGEM NO GITHUB
link_fundo = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/fghy.jpg"

st.markdown(f"""
    <style>
    .stApp {{ 
        background-image: url("{link_fundo}"); 
        background-size: cover; 
        background-attachment: fixed;
        background-position: center;
    }}
    h1, h2, h3, p, label, .stMarkdown {{ color: #00ff41 !important; text-shadow: 1px 1px 2px #000; }}
    
    .st-expander {{ 
        background-color: rgba(0, 20, 0, 0.8) !important; 
        border: 1px solid #00ff41 !important; 
        border-radius: 12px !important; 
    }}
    
    div.stButton > button {{ 
        background-color: #003300; color: #00ff41; border: 1px solid #00ff41; 
        border-radius: 8px; font-weight: bold; 
    }}
    div.stButton > button:hover {{ background-color: #00ff41; color: black; }}
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.title("🔐 Login de Acesso")
    senha = st.text_input("Digite a senha:", type="password")
    if st.button("Entrar", key="login_btn"):
        if senha == "fgxv4VP0/*":
            st.session_state.logado = True; st.session_state.perfil = "ADMIN"; st.rerun()
        elif senha == "JOHN123":
            st.session_state.logado = True; st.session_state.perfil = "VIGILANTE"; st.rerun()
        else:
            st.error("Senha incorreta!")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🏥 Painel de Monitoramento")
if st.button("Sair do Sistema", key="sair_final"):
    st.session_state.logado = False; st.rerun()

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- 0. NOVO CADASTRO ---
with st.expander("➕ Adicionar Novo Colaborador"):
    col_a, col_b, col_c, col_d = st.columns(4)
    novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome:", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
    novo_vinculo = col_d.selectbox("Vínculo Original:", setores_lista, key="novo_vinculo")
    
    if st.button("Salvar Novo Cadastro", key="salvar_cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
            st.success("Salvo!"); st.rerun()

# --- 1. REGISTRO DE ENTRADA (DESTINO MANUAL) ---
with st.expander("🔵 Registrar Nova Entrada"):
    c1, c2, c3 = st.columns([2, 2, 1])
    cpf_input = c1.text_input("CPF do colaborador:")
    setor_escolhido = c2.selectbox("Selecione o destino agora:", setores_lista, key="sel_destino")
    
    if c3.button("Adicionar Entrada", key="btn_entrada"):
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'], 
                "nome": p[0]['nome'], 
                "empresa": p[0].get('empresa', ''),
                "setor_destino": setor_escolhido, 
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "data_saida": ""
            }).execute()
            st.rerun()
        else:
            st.error("CPF não cadastrado.")

# --- 1.1 REGISTRO DE SAÍDA MANUAL ---
with st.expander("🔴 Registrar Saída (Busca por CPF)"):
    c1, c2 = st.columns([3, 1])
    cpf_saida = c1.text_input("Digite o CPF para saída:", key="out_cpf")
    if c2.button("Confirmar Saída", key="btn_saida_manual"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_saida).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
            st.rerun()

# --- 2. PAINEL DE STATUS ---
st.subheader("📋 Pessoas Presentes")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
if dados:
    aba_lista = st.tabs(setores_lista)
    for i, nome_setor in enumerate(setores_lista):
