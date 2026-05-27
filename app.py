import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# ====================== CONFIGURAÇÃO ======================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐", initial_sidebar_state="expanded")

# ====================== ESTILO ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(10, 20, 40, 0.88), rgba(15, 23, 42, 0.95));
        color: #e0f2fe;
        font-family: 'Inter', sans-serif;
    }
    
    .sidebar-title {
        font-size: 26px;
        font-weight: 700;
        color: #67e8f9;
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #334155;
    }
    
    h1 {
        color: #67e8f9 !important;
        font-size: 34px !important;
        font-weight: 700;
    }
    
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:not([key="sair_final"]) {
        background: linear-gradient(90deg, #10b981, #34d399);
        color: #0f172a;
        border: 2px solid #34d399;
    }
    
    div.stButton > button:not([key="sair_final"]):hover {
        background: linear-gradient(90deg, #34d399, #6ee7b7);
        transform: translateY(-3px);
    }
    
    div.stButton > button[key="sair_final"] {
        background: linear-gradient(90deg, #ef4444, #f87171);
        color: white;
    }
    
    .prestador-box {
        background-color: rgba(30, 41, 59, 0.9);
        border: 2px solid #00f5ff;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
st.sidebar.markdown("<div class='sidebar-title'>🔐 ACCESS GATE</div>", unsafe_allow_html=True)
st.sidebar.markdown("**MENU PRINCIPAL**")
st.sidebar.markdown("🏠 Dashboard")
st.sidebar.markdown("👥 Colaboradores")
st.sidebar.markdown("🔧 Prestadores de Serviço")
st.sidebar.markdown("🕒 Histórico")
st.sidebar.markdown("⚙️ Configurações")

# ====================== CONTROLE DE SESSÃO ======================
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center; margin:40px 0 30px 0;'>🔐 ACCESS GATE</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; margin:30px 0;'>
                <div style='width: 320px; height: 320px; margin: 0 auto; 
                            border: 8px solid #00f5ff; 
                            border-radius: 50%; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            box-shadow: 0 0 90px #00f5ff, inset 0 0 60px rgba(0, 245, 255, 0.7);'>
                    <div style='text-align:center;'>
                        <div style='font-size: 110px; margin-bottom: 10px;'>🔑</div>
                        <span style='font-size: 32px; font-weight: 900; color:#00f5ff;'>BIOMETRIC</span><br>
                        <span style='font-size: 32px; font-weight: 900; color:#00f5ff;'>LOGIN</span><br>
                        <span style='color:#00ff9d; font-size: 24px; font-weight: bold;'>READY</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center; color:#00f5ff;'>OU USE CREDENCIAIS</h3>", unsafe_allow_html=True)
        
        senha = st.text_input("Digite a senha de acesso:", type="password", key="senha_login")
        
        if st.button("🔓 ENTRAR NO SISTEMA", key="login_btn", use_container_width=True):
            if senha == "fgxv4VP0/*":
                st.session_state.logado = True
                st.session_state.perfil = "ADMIN"
                st.rerun()
            elif senha == "JOHN123":
                st.session_state.logado = True
                st.session_state.perfil = "VIGILANTE"
                st.rerun()
            else:
                st.error("❌ Senha incorreta!")
    st.stop()

# ====================== HEADER ======================
col1, col2, col3 = st.columns([5, 2, 2])
with col1:
    st.title("ACCESS GATE - PAINEL DE CONTROLE")
with col2:
    st.markdown(f"**PERFIL:** <span style='color:#67e8f9;'>{st.session_state.perfil}</span>", unsafe_allow_html=True)
with col3:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

st.markdown("### 📊 Painel de Controle")

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# ====================== REGISTRO DE ENTRADA ======================
st.subheader("📋 Registrar Entrada")

tipo = st.radio("Tipo de Entrada:", ["Colaborador Interno", "Prestador de Serviço"], horizontal=True)

if tipo == "Colaborador Interno":
    destinos = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Laboratório", "Farmacia"]
else:
    destinos = ["C.C", "GRSA", "Brasanitas"]

c1, c2, c3 = st.columns([2, 2, 1])
cpf = c1.text_input("CPF do colaborador / prestador:")
destino = c2.selectbox("Destino:", destinos)

if c3.button("✅ Registrar Entrada", type="primary"):
    if cpf:
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'],
                "nome": p[0]['nome'],
                "empresa": p[0].get('empresa', ''),
                "setor_destino": destino,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "data_saida": ""
            }).execute()
            st.success(f"✅ Entrada registrada com sucesso para **{destino}**!")
            st.rerun()
        else:
            st.error("❌ CPF não encontrado no cadastro.")
    else:
        st.warning("Digite o CPF.")

# ====================== PESSOAS PRESENTES ======================
st.subheader("📍 Pessoas Presentes no Hospital")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    tabs = st.tabs(["Todos"] + ["C.C", "GRSA", "Brasanitas"])
    
    with tabs[0]:
        for p in dados:
            c1, c2, c3 = st.columns([3, 3, 2])
            c1.write(f"**{p['nome']}** - {p['setor_destino']}")
            c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
            if c3.button("🚪 Saída", key=f"saida_{p['id']}"):
                supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                st.rerun()
    
    for i, setor in enumerate(["C.C", "GRSA", "Brasanitas"], 1):
        with tabs[i]:
            for p in [r for r in dados if r.get('setor_destino') == setor]:
                c1, c2, c3 = st.columns([3, 3, 2])
                c1.write(f"**{p['nome']}**")
                c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
                if c3.button("🚪 Saída", key=f"saida2_{p['id']}"):
                    supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                    st.rerun()

# ====================== HISTÓRICO E GESTÃO ======================
with st.expander("🕒 Histórico Completo"):
    todos = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos:
        st.dataframe(pd.DataFrame(todos), use_container_width=True)
        id_del = st.number_input("ID para excluir:", min_value=1, step=1)
        if st.button("🗑️ Excluir Registro"):
            supabase.table("movimentacao").delete().eq("id", id_del).execute()
            st.rerun()

if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros"):
        pessoas = supabase.table("Pessoas").select("nome, cpf").execute().data
        if pessoas:
            lista = [f"{p['nome']} (CPF: {p['cpf']})" for p in pessoas]
            sel = st.selectbox("Excluir Cadastro:", lista)
            if st.button("🗑️ Excluir Cadastro"):
                cpf_del = sel.split("(CPF: ")[1].replace(")", "")
                supabase.table("Pessoas").delete().eq("cpf", cpf_del).execute()
                st.rerun()

st.success("✅ Sistema atualizado com sucesso!")
