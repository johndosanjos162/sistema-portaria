import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐", initial_sidebar_state="expanded")

# ====================== DESIGN DB-SECURE ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: #0f172a;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e2937;
        border-right: 1px solid #334155;
    }
    
    .sidebar-title {
        font-size: 24px;
        font-weight: 700;
        color: #22d3ee;
        text-align: center;
        padding: 20px 0;
        border-bottom: 1px solid #334155;
    }
    
    h1 {
        color: #22d3ee !important;
        font-size: 28px !important;
        font-weight: 700;
    }
    
    /* Cards */
    .card {
        background-color: #1e2937;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .st-expander {
        background-color: #1e2937 !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    
    /* Botões */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: 0.3s;
    }
    
    div.stButton > button[key="sair_final"] {
        background-color: #b91c1c !important;
        color: white !important;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #1e2937;
        border: 1px solid #475569;
        color: white;
        border-radius: 8px;
    }
    
    .stDataFrame {
        background-color: #1e2937;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
st.sidebar.markdown("<div class='sidebar-title'>🔐 ACCESS GATE</div>", unsafe_allow_html=True)
st.sidebar.markdown("**MENU**")
st.sidebar.markdown("🏠 Dashboard")
st.sidebar.markdown("👥 Colaboradores")
st.sidebar.markdown("📍 Controle de Acesso")
st.sidebar.markdown("🕒 Histórico")
st.sidebar.markdown("⚙️ Configurações")

# ====================== HEADER ======================
col1, col2, col3 = st.columns([5, 2, 2])
with col1:
    st.markdown("<h1>ACCESS GATE - PAINEL DE CONTROLE</h1>", unsafe_allow_html=True)

with col2:
    st.markdown(f"**PERFIL:** <span style='color:#67e8f9; font-weight:600;'>{st.session_state.get('perfil', 'ADMIN')}</span>", unsafe_allow_html=True)

with col3:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# ====================== LOGIN ======================
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.title("🔐 ACCESS GATE")
    col_login = st.columns([1,3,1])[1]
    with col_login:
        senha = st.text_input("Digite a senha:", type="password")
        if st.button("🔓 ENTRAR NO SISTEMA", use_container_width=True):
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

# ====================== DASHBOARD COM 4 CARDS ======================
st.markdown("### 📊 Painel de Controle")

# Linha 1 - 2 Cards
col_card1, col_card2 = st.columns(2)

# Card 1: Adicionar Colaborador + Registrar Entrada
with col_card1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("➕ Gerenciamento de Cadastros")
    
    with st.expander("Adicionar Novo Colaborador"):
        col_a, col_b, col_c, col_d = st.columns(4)
        novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
        novo_nome = col_b.text_input("Nome:", key="novo_nome")
        novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
        novo_vinculo = col_d.selectbox("Vínculo:", setores_lista, key="novo_vinculo")
        
        if st.button("💾 Salvar Cadastro", key="salvar_cadastro"):
            if novo_cpf and novo_nome:
                supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
                st.success("✅ Salvo!")
                st.rerun()
    
    with st.expander("🔵 Registrar Nova Entrada"):
        c1, c2, c3 = st.columns([2,2,1])
        cpf_input = c1.text_input("CPF:", key="cpf_entrada")
        setor_escolhido = c2.selectbox("Destino:", setores_lista, key="destino_entrada")
        if c3.button("✅ Registrar Entrada", key="btn_entrada"):
            p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
            if p:
                supabase.table("movimentacao").insert({
                    "cpf": p[0]['cpf'], "nome": p[0]['nome'], "empresa": p[0].get('empresa',''),
                    "setor_destino": setor_escolhido,
                    "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), "data_saida": ""
                }).execute()
                st.success("Entrada registrada!")
                st.rerun()
            else:
                st.error("CPF não encontrado.")
    st.markdown("</div>", unsafe_allow_html=True)

# Card 2: Registrar Saída
with col_card2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔴 Registrar Saída")
    
    cpf_saida = st.text_input("CPF para Saída:", key="cpf_saida")
    if st.button("✅ Confirmar Saída", key="btn_saida"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_saida).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
            st.success("Saída registrada!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Linha 2 - Pessoas Presentes e Histórico
col_card3, col_card4 = st.columns(2)

with col_card3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📍 Pessoas Presentes no Hospital")
    dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
    
    if dados:
        aba_lista = st.tabs(setores_lista[:6])  # Limitando para melhor visual
        for i, nome_setor in enumerate(setores_lista[:6]):
            with aba_lista[i]:
                for p in [r for r in dados if r.get('setor_destino') == nome_setor]:
                    c1, c2, c3 = st.columns([3,3,2])
                    c1.write(f"**{p['nome']}**")
                    c2.write(f"{p.get('empresa', 'N/A')}")
                    if c3.button("🚪 Saída", key=f"saida_{p['id']}"):
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with col_card4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🕒 Histórico Completo")
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        st.dataframe(pd.DataFrame(todos_dados), use_container_width=True)
        
        id_excluir = st.number_input("ID para excluir:", min_value=1, step=1)
        if st.button("🗑️ Excluir Registro", key="del_reg"):
            supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Gestão Admin
if st.session_state.perfil == "ADMIN":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("⚙️ Gestão de Cadastros")
    todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
    if todos_colaboradores:
        lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
        selecionado = st.selectbox("Excluir Cadastro:", lista_nomes)
        if st.button("🗑️ Excluir Cadastro", key="del_cad"):
            cpf_excluir = selecionado.split("(CPF: ")[1].replace(")", "")
            supabase.table("Pessoas").delete().eq("cpf", cpf_excluir).execute()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
