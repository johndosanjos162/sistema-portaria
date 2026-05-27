import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐", initial_sidebar_state="expanded")

# ====================== DESIGN PRÓXIMO DA IMAGEM ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    .stApp {
        background: #0a1428;
        color: #e0f2fe;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1e2937;
        border-right: 1px solid #334155;
    }
    
    .sidebar-title {
        font-size: 22px;
        font-weight: 700;
        color: #67e8f9;
        padding: 20px 0 10px 0;
        text-align: center;
        border-bottom: 1px solid #334155;
    }
    
    /* Header */
    h1 {
        color: #67e8f9 !important;
        font-size: 32px !important;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    /* Expansores estilo lista */
    .st-expander {
        background-color: rgba(30, 41, 59, 0.6) !important;
        border: none !important;
        border-radius: 8px !important;
        margin-bottom: 8px;
    }
    
    .st-expander header {
        background-color: transparent !important;
        padding: 14px 20px !important;
        font-size: 17px;
        font-weight: 500;
    }
    
    /* Botão Desconectar */
    div.stButton > button[key="sair_final"] {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 10px 24px;
        border: none;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: #1e2937;
        border: 1px solid #475569;
        color: white;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2937;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #67e8f9;
        color: #0a1428;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
st.sidebar.markdown("<div class='sidebar-title'>🔐 ACCESS GATE</div>", unsafe_allow_html=True)
st.sidebar.markdown("**MENU PRINCIPAL**")
st.sidebar.markdown("🏠 Dashboard")
st.sidebar.markdown("👥 Colaboradores")
st.sidebar.markdown("📍 Controle de Acesso")
st.sidebar.markdown("🕒 Histórico")
st.sidebar.markdown("⚙️ Configurações")

# ====================== HEADER ======================
col_title, col_perfil, col_btn = st.columns([5, 2, 2])

with col_title:
    st.markdown("<h1>ACCESS GATE - PAINEL DE CONTROLE</h1>", unsafe_allow_html=True)

with col_perfil:
    st.markdown(f"**PERFIL:** <span style='color:#67e8f9; font-size:18px;'>{st.session_state.get('perfil', 'ADMIN')}</span>", unsafe_allow_html=True)

with col_btn:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

# ====================== CONTEÚDO ======================
setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- Login ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.title("🔐 ACCESS GATE")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        senha = st.text_input("Digite a senha de acesso:", type="password", key="senha_login")
        if st.button("🔓 ENTRAR", key="login_btn", use_container_width=True):
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

# --- Expansores (estilo da imagem) ---
with st.expander("➕ ADICIONAR NOVO COLABORADOR"):
    col_a, col_b, col_c, col_d = st.columns(4)
    novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome Completo:", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
    novo_vinculo = col_d.selectbox("Vínculo:", setores_lista, key="novo_vinculo")
   
    if st.button("💾 SALVAR CADASTRO", key="salvar_cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
            st.success("✅ Cadastro salvo!")
            st.rerun()

with st.expander("🔵 REGISTRAR NOVA ENTRADA"):
    c1, c2, c3 = st.columns([2, 2, 1])
    cpf_input = c1.text_input("CPF do colaborador:")
    setor_escolhido = c2.selectbox("Destino:", setores_lista, key="sel_destino")
   
    if c3.button("✅ REGISTRAR ENTRADA", key="btn_entrada"):
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'], "nome": p[0]['nome'], "empresa": p[0].get('empresa', ''),
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), "data_saida": ""
            }).execute()
            st.success("✅ Entrada registrada!")
            st.rerun()
        else:
            st.error("CPF não cadastrado.")

with st.expander("🔴 REGISTRAR SAÍDA"):
    c1, c2 = st.columns([3, 1])
    cpf_saida = c1.text_input("CPF para saída:", key="out_cpf")
    if c2.button("✅ CONFIRMAR SAÍDA", key="btn_saida_manual"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_saida).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
            st.success("✅ Saída registrada!")
            st.rerun()

# Pessoas Presentes
st.subheader("📍 PESSOAS PRESENTES NO HOSPITAL")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    aba_lista = st.tabs(setores_lista)
    for i, nome_setor in enumerate(setores_lista):
        with aba_lista[i]:
            for p in [r for r in dados if r.get('setor_destino') == nome_setor]:
                c1, c2, c3 = st.columns([3, 3, 2])
                c1.write(f"**{p['nome']}**")
                c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
                if c3.button("🚪 SAÍDA", key=f"s_{p['id']}"):
                    supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                    st.rerun()

# Histórico e Gestão
with st.expander("🕒 HISTÓRICO COMPLETO"):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        st.dataframe(pd.DataFrame(todos_dados), use_container_width=True)
        id_excluir = st.number_input("ID para excluir:", min_value=1, step=1)
        if st.button("🗑️ EXCLUIR REGISTRO", key="del_reg"):
            supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
            st.rerun()

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
