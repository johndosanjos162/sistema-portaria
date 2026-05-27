import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐")

# ====================== DESIGN MODERNO TIPO DB-SECURE ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: #0f172a;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Cabeçalho */
    h1 {
        color: #22d3ee !important;
        font-size: 32px !important;
        font-weight: 700;
        text-shadow: 0 0 15px rgba(34, 211, 238, 0.5);
    }
    
    /* Cards / Expansores */
    .st-expander {
        background-color: #1e2937 !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 16px;
    }
    
    .st-expander header {
        background-color: #1e2937 !important;
        border-bottom: 1px solid #334155;
    }
    
    /* Botões */
    div.stButton > button {
        background-color: #1e40af;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
    }
    
    /* Botão Desconectar */
    div.stButton > button[key="sair_final"] {
        background-color: #b91c1c !important;
        color: white !important;
        border: 1px solid #f87171;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background-color: #1e2937 !important;
        border: 1px solid #475569 !important;
        color: #e2e8f0 !important;
        border-radius: 8px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e2937;
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #334155;
        color: #94a3b8;
        border-radius: 8px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #22d3ee !important;
        color: #0f172a !important;
        font-weight: 600;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: #1e2937;
        border: 1px solid #334155;
        border-radius: 10px;
    }
    
    /* Sidebar Style Simulation */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>🔐 ACCESS GATE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:22px; color:#67e8f9;'>🏥 Sistema de Controle de Portaria</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
            <div style='text-align:center; padding:30px; background:#1e2937; border-radius:16px; border:2px solid #22d3ee;'>
                <span style='font-size:90px;'>🔐</span><br><br>
                <h2 style='color:#22d3ee;'>BIOMETRIC LOGIN</h2>
                <p style='color:#67e8f9;'>SYSTEM READY</p>
            </div>
        """, unsafe_allow_html=True)
        
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
                st.error("Senha incorreta!")
    st.stop()

# ====================== PAINEL PRINCIPAL ======================
col_header1, col_header2 = st.columns([4, 1])
with col_header1:
    st.markdown("<h1>ACCESS GATE - PAINEL DE CONTROLE</h1>", unsafe_allow_html=True)

with col_header2:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()
    st.markdown(f"**PERFIL:** <span style='color:#67e8f9;'>{st.session_state.perfil}</span>", unsafe_allow_html=True)

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- 0. NOVO CADASTRO ---
with st.expander("➕ ADICIONAR NOVO COLABORADOR", expanded=False):
    col_a, col_b, col_c, col_d = st.columns(4)
    novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome Completo:", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
    novo_vinculo = col_d.selectbox("Vínculo:", setores_lista, key="novo_vinculo")
   
    if st.button("💾 SALVAR CADASTRO", key="salvar_cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
            st.success("✅ Cadastro salvo com sucesso!")
            st.rerun()

# --- 1. REGISTRO DE ENTRADA ---
with st.expander("🔵 REGISTRAR NOVA ENTRADA", expanded=False):
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

# --- 1.1 REGISTRO DE SAÍDA ---
with st.expander("🔴 REGISTRAR SAÍDA", expanded=False):
    c1, c2 = st.columns([3, 1])
    cpf_saida = c1.text_input("CPF para saída:", key="out_cpf")
    if c2.button("✅ CONFIRMAR SAÍDA", key="btn_saida_manual"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_saida).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
            st.success("✅ Saída registrada!")
            st.rerun()

# --- 2. PESSOAS PRESENTES ---
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

# --- 3. HISTÓRICO ---
with st.expander("🕒 HISTÓRICO COMPLETO", expanded=False):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        st.dataframe(pd.DataFrame(todos_dados), use_container_width=True)
        id_excluir = st.number_input("ID do registro para excluir:", min_value=1, step=1)
        if st.button("🗑️ EXCLUIR REGISTRO", key="del_reg"):
            supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
            st.rerun()

# --- 4. GESTÃO ADMIN ---
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ GESTÃO DE CADASTROS", expanded=False):
        todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
        if todos_colaboradores:
            lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
            selecionado = st.selectbox("Selecionar para excluir:", lista_nomes)
            if st.button("🗑️ EXCLUIR CADASTRO", key="del_cad"):
                cpf_excluir = selecionado.split("(CPF: ")[1].replace(")", "")
                supabase.table("Pessoas").delete().eq("cpf", cpf_excluir).execute()
                st.rerun()
