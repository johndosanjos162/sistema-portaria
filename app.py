import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐")

# ====================== DESIGN FUTURISTA AVANÇADO ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    .stApp {
        background: radial-gradient(circle at center, #0A1F2E 0%, #000000 100%);
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }
    
    /* Efeito de Grid Tecnológico */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: -1;
    }
    
    h1 {
        color: #00f5ff !important;
        text-align: center;
        font-size: 48px !important;
        font-weight: 900;
        text-shadow: 0 0 30px #00f5ff, 0 0 60px #00f5ff;
        letter-spacing: 6px;
        margin-bottom: 10px;
    }
    
    /* LOGIN SCREEN */
    .biometric-circle {
        width: 260px;
        height: 260px;
        border: 4px solid #00f5ff;
        border-radius: 50%;
        margin: 20px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: 0 0 60px #00f5ff,
                    inset 0 0 40px rgba(0, 245, 255, 0.6);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 60px #00f5ff, inset 0 0 40px rgba(0, 245, 255, 0.6); }
        50% { box-shadow: 0 0 80px #00f5ff, inset 0 0 60px rgba(0, 245, 255, 0.8); }
        100% { box-shadow: 0 0 60px #00f5ff, inset 0 0 40px rgba(0, 245, 255, 0.6); }
    }
    
    /* Expansores */
    .st-expander {
        background: rgba(10, 25, 45, 0.85) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 16px !important;
        box-shadow: 0 0 25px rgba(0, 245, 255, 0.4);
        margin-bottom: 12px;
    }
    
    .st-expander header {
        background: linear-gradient(90deg, #001122, #003355) !important;
    }
    
    /* Botões Principais */
    div.stButton > button {
        background: linear-gradient(45deg, #001122, #003355);
        color: #00f5ff;
        border: 2px solid #00f5ff;
        border-radius: 12px;
        font-weight: 700;
        padding: 14px 28px;
        font-size: 16px;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 0 20px #00f5ff;
        transition: all 0.4s ease;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(45deg, #00f5ff, #00ff9d);
        color: #000;
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 0 40px #00f5ff;
    }
    
    /* Campos de Input */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: rgba(10, 30, 50, 0.9) !important;
        border: 2px solid #00f5ff !important;
        color: white !important;
        border-radius: 10px;
        font-size: 16px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(0, 20, 40, 0.8);
        border-bottom: 2px solid #00f5ff;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #00f5ff !important;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00f5ff !important;
        color: #000 !important;
        border-radius: 8px;
    }
    
    /* Dataframe */
    .stDataFrame {
        border: 2px solid #00f5ff;
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.markdown("<h1>🔐 ACCESS GATE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:24px; color:#00ff9d; margin-bottom:30px;'>🏥 SISTEMA DE SEGURANÇA HOSPITALAR</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class='biometric-circle'>
                <div style='text-align:center;'>
                    <span style='font-size: 85px;'>🔑</span><br>
                    <span style='font-size: 26px; font-weight:900; color:#00f5ff;'>BIOMETRIC</span><br>
                    <span style='font-size: 26px; font-weight:900; color:#00f5ff;'>LOGIN</span><br>
                    <span style='color:#00ff9d; font-size:18px;'>SYSTEM READY</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center; color:#00f5ff; margin:25px 0 15px 0;'>OU USE CREDENCIAIS</h3>", unsafe_allow_html=True)
        
        senha = st.text_input("🔑 Digite a senha de acesso:", type="password", key="senha_login")
        
        if st.button("🔓 ACESSAR SISTEMA", key="login_btn", use_container_width=True):
            if senha == "fgxv4VP0/*":
                st.session_state.logado = True
                st.session_state.perfil = "ADMIN"
                st.success("🔓 ACESSO AUTORIZADO - ADMINISTRADOR")
                st.rerun()
            elif senha == "JOHN123":
                st.session_state.logado = True
                st.session_state.perfil = "VIGILANTE"
                st.success("🔓 ACESSO AUTORIZADO - VIGILANTE")
                st.rerun()
            else:
                st.error("❌ SENHA INCORRETA!")
    st.stop()

# --- INTERFACE PRINCIPAL ---
st.title("🏥 ACCESS GATE - PAINEL DE CONTROLE")

col_sair, col_perfil = st.columns([5, 1])
with col_sair:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

with col_perfil:
    st.markdown(f"**PERFIL:** <span style='color:#00ff9d; font-weight:bold;'>{st.session_state.perfil}</span>", unsafe_allow_html=True)

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- 0. NOVO CADASTRO ---
with st.expander("➕ ADICIONAR NOVO COLABORADOR"):
    col_a, col_b, col_c, col_d = st.columns(4)
    novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome Completo:", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
    novo_vinculo = col_d.selectbox("Vínculo:", setores_lista, key="novo_vinculo")
   
    if st.button("💾 SALVAR CADASTRO", key="salvar_cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
            st.success("✅ Cadastro realizado com sucesso!")
            st.rerun()

# --- 1. REGISTRO DE ENTRADA ---
with st.expander("🔵 REGISTRAR NOVA ENTRADA"):
    c1, c2, c3 = st.columns([2, 2, 1])
    cpf_input = c1.text_input("CPF do Colaborador:")
    setor_escolhido = c2.selectbox("Destino:", setores_lista, key="sel_destino")
   
    if c3.button("✅ REGISTRAR ENTRADA", key="btn_entrada"):
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
            st.success("✅ Entrada registrada com sucesso!")
            st.rerun()
        else:
            st.error("❌ CPF não encontrado.")

# --- 1.1 REGISTRO DE SAÍDA ---
with st.expander("🔴 REGISTRAR SAÍDA"):
    c1, c2 = st.columns([3, 1])
    cpf_saida = c1.text_input("CPF para Saída:", key="out_cpf")
    if c2.button("✅ CONFIRMAR SAÍDA", key="btn_saida_manual"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_saida).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
            st.success("✅ Saída registrada!")
            st.rerun()

# --- 2. PAINEL DE STATUS ---
st.subheader("📍 PESSOAS PRESENTES NO HOSPITAL")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    aba_lista = st.tabs(setores_lista)
    for i, nome_setor in enumerate(setores_lista):
        with aba_lista[i]:
            setor_pessoas = [r for r in dados if r['setor_destino'] == nome_setor]
            if setor_pessoas:
                for p in setor_pessoas:
                    c1, c2, c3 = st.columns([3, 3, 2])
                    c1.write(f"**{p['nome']}**")
                    c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
                    if c3.button("🚪 REGISTRAR SAÍDA", key=f"s_{p['id']}"):
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                        st.rerun()
            else:
                st.info("Nenhuma pessoa presente neste setor.")

# --- 3. HISTÓRICO ---
with st.expander("🕒 HISTÓRICO COMPLETO"):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        st.dataframe(pd.DataFrame(todos_dados), use_container_width=True)
        
        id_excluir = st.number_input("ID do registro para excluir:", min_value=1, step=1)
        if st.button("🗑️ EXCLUIR REGISTRO", key="del_reg"):
            supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
            st.rerun()

# --- 4. GESTÃO (ADMIN) ---
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ GESTÃO DE CADASTROS"):
        todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
        if todos_colaboradores:
            lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
            selecionado = st.selectbox("Selecionar para excluir:", lista_nomes)
            if st.button("🗑️ EXCLUIR CADASTRO", key="del_cad"):
                cpf_excluir = selecionado.split("(CPF: ")[1].replace(")", "")
                supabase.table("Pessoas").delete().eq("cpf", cpf_excluir).execute()
                st.rerun()
