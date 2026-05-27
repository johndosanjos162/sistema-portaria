import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Access Gate", layout="wide", page_icon="🔐")

# ====================== NOVO DESIGN FUTURISTA ======================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0A1F2E 0%, #05131F 100%);
        color: #ffffff;
    }
    
    /* Título Principal */
    h1 {
        color: #00f5ff !important;
        text-align: center;
        font-size: 42px !important;
        text-shadow: 0 0 20px #00f5ff;
        letter-spacing: 3px;
    }
    
    /* Estilo dos Expander */
    .st-expander {
        background-color: rgba(10, 31, 46, 0.85) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
    }
    
    .st-expander header {
        background-color: rgba(0, 20, 40, 0.9) !important;
    }
    
    /* Botões */
    div.stButton > button {
        background-color: #003344;
        color: #00f5ff;
        border: 2px solid #00f5ff;
        border-radius: 12px;
        font-weight: bold;
        padding: 12px 24px;
        transition: all 0.3s;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.4);
    }
    
    div.stButton > button:hover {
        background-color: #00f5ff;
        color: #000;
        box-shadow: 0 0 25px #00f5ff;
        transform: scale(1.05);
    }
    
    /* Campos de texto */
    .stTextInput > div > div > input {
        background-color: rgba(10, 31, 46, 0.8) !important;
        border: 1px solid #00f5ff !important;
        color: white !important;
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(10, 31, 46, 0.7);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #00f5ff !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: black !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 1px solid #00f5ff;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    # === TELA DE LOGIN ESTILIZADA ===
    st.markdown("""
        <h1 style='text-align:center; margin-bottom:10px;'>🔐 ACCESS GATE</h1>
        <p style='text-align:center; font-size:20px; color:#00f5ff;'>🏥 Portaria Hospitalar</p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; margin: 30px 0;'>
                <div style='border: 3px solid #00f5ff; border-radius: 50%; width: 220px; height: 220px; margin: 0 auto; 
                            display: flex; align-items: center; justify-content: center; box-shadow: 0 0 40px #00f5ff;'>
                    <div style='text-align:center;'>
                        <span style='font-size: 70px;'>🔑</span><br>
                        <span style='font-size: 22px; color:#00f5ff; font-weight:bold;'>BIOMETRIC<br>LOGIN</span><br>
                        <span style='color:#00ff9d;'>READY</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center;'>OU USE CREDENCIAIS</h3>", unsafe_allow_html=True)
        
        senha = st.text_input("Digite a senha de acesso:", type="password", key="senha_login")
        
        if st.button("🔓 ENTRAR NO SISTEMA", key="login_btn", use_container_width=True):
            if senha == "fgxv4VP0/*":
                st.session_state.logado = True
                st.session_state.perfil = "ADMIN"
                st.success("🔓 Acesso Autorizado - ADMIN")
                st.rerun()
            elif senha == "JOHN123":
                st.session_state.logado = True
                st.session_state.perfil = "VIGILANTE"
                st.success("🔓 Acesso Autorizado - Vigilante")
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🏥 ACCESS GATE - Painel de Monitoramento")

col_sair, col_perfil = st.columns([4, 1])
with col_sair:
    if st.button("🚪 Sair do Sistema", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

with col_perfil:
    st.markdown(f"**Perfil:** `{st.session_state.perfil}`")

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- 0. NOVO CADASTRO ---
with st.expander("➕ Adicionar Novo Colaborador"):
    col_a, col_b, col_c, col_d = st.columns(4)
    novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome:", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
    novo_vinculo = col_d.selectbox("Vínculo Original:", setores_lista, key="novo_vinculo")
   
    if st.button("💾 Salvar Novo Cadastro", key="salvar_cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
            st.success("✅ Cadastro salvo com sucesso!")
            st.rerun()

# --- 1. REGISTRO DE ENTRADA ---
with st.expander("🔵 Registrar Nova Entrada"):
    c1, c2, c3 = st.columns([2, 2, 1])
    cpf_input = c1.text_input("CPF do colaborador:")
    setor_escolhido = c2.selectbox("Selecione o destino agora:", setores_lista, key="sel_destino")
   
    if c3.button("✅ Adicionar Entrada", key="btn_entrada"):
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
            st.success("Entrada registrada!")
            st.rerun()
        else:
            st.error("CPF não cadastrado.")

# --- 1.1 REGISTRO DE SAÍDA ---
with st.expander("🔴 Registrar Saída (Busca por CPF)"):
    c1, c2 = st.columns([3, 1])
    cpf_saida = c1.text_input("Digite o CPF para saída:", key="out_cpf")
    if c2.button("✅ Confirmar Saída", key="btn_saida_manual"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_saida).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id
