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
    st
