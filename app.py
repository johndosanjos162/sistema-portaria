import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐")

# ====================== DESIGN PREMIUM FUTURISTA ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&display=swap');
    
    .stApp {
        background: radial-gradient(circle at center, #0A1F2E 0%, #000814 100%);
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }
    
    /* Cadeado Grande no Fundo */
    .stApp::before {
        content: '🔐';
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 520px;
        opacity: 0.07;
        color: #00f5ff;
        pointer-events: none;
        z-index: -1;
        filter: blur(8px);
    }
    
    /* Grid Tecnológico */
    .stApp::after {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: linear-gradient(rgba(0, 245, 255, 0.04) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(0, 245, 255, 0.04) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: -1;
    }
    
    h1 {
        color: #00f5ff !important;
        text-align: center;
        font-size: 46px !important;
        font-weight: 900;
        text-shadow: 0 0 25px #00f5ff;
        letter-spacing: 5px;
        margin-bottom: 8px;
    }
    
    /* Botão Desconectar - Bem posicionado */
    .stButton > button[k="sair_final"] {
        background: linear-gradient(45deg, #660000, #aa0000);
        color: white;
        border: 2px solid #ff3333;
        border-radius: 50px;
        padding: 10px 24px;
        font-weight: bold;
        position: absolute;
        top: 25px;
        right: 30px;
    }
    
    /* Expansores */
    .st-expander {
        background: rgba(10, 25, 50, 0.85) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 16px !important;
        box-shadow: 0 0 20px rgba(0, 245, 255, 0.35);
        margin-bottom: 14px;
    }
    
    .st-expander header {
        background: linear-gradient(90deg, #001122, #003366) !important;
        border-radius: 14px !important;
    }
    
    /* Botões Internos */
    div.stButton > button {
        background: linear-gradient(45deg, #001f3f, #003366);
        color: #00f5ff;
        border: 2px solid #00f5ff;
        border-radius: 12px;
        font-weight: 700;
        padding: 12px 26px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        box-shadow: 0 0 18px rgba(0, 245, 255, 0.5);
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(45deg, #00f5ff, #00ffaa);
        color: #000;
        transform: scale(1.04);
        box-shadow: 0 0 35px #00f5ff;
    }
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div {
        background-color: rgba(5, 20, 45, 0.95) !important;
        border: 2px solid #00f5ff !important;
        color: #ffffff !important;
        border-radius: 10px;
        font-size: 16px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(0, 15, 35, 0.9);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #00f5ff !important;
    }
    
    .stDataFrame {
        border: 2px solid #00f5ff;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE ACESSO ---
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.markdown("<h1>🔐 ACCESS GATE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:24px; color:#00ff9d;'>🏥 PORTARIA HOSPITALAR</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
            <div style='text-align:center; margin:40px 0;'>
                <div style='border:5px solid #00f5ff; border-radius:50%; width:280px; height:280px; margin:0 auto;
                            display:flex; align-items:center; justify-content:center; box-shadow: 0 0 70px #00f5ff;'>
                    <div style='text-align:center;'>
                        <span style='font-size:100px;'>🔑</span><br>
                        <span style='font-size:28px; font-weight:900; color:#00f5ff;'>BIOMETRIC LOGIN</span><br>
                        <span style='color:#00ff9d; font-size:20px;'>READY</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        senha = st.text_input("🔑 Digite a senha:", type="password", key="senha_login")
        
        if st.button("🔓 ACESSAR SISTEMA", key="login_btn", use_container_width=True):
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
st.markdown("<h1>🔐 ACCESS GATE - PAINEL DE CONTROLE</h1>", unsafe_allow_html=True)

# Botão Desconectar bem posicionado no topo
col_desconectar, col_perfil = st.columns([6, 1])
with col_desconectar:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

with col_perfil:
    st.markdown(f"<h3 style='color:#00ff9d; text-align:right;'>PERFIL: {st.session_state.perfil}</h3>", unsafe_allow_html=True)

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# --- Expansores ---
with st.expander("➕ ADICIONAR NOVO COLABORADOR"):
    col_a, col_b, col_c, col_d = st.columns(4)
    novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
    novo_nome = col_b.text_input("Nome Completo:", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
    novo_vinculo = col_d.selectbox("Vínculo:", setores_lista, key="novo_vinculo")
   
    if st.button("💾 SALVAR NOVO CADASTRO", key="salvar_cadastro"):
        if novo_cpf and novo_nome:
            supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
            st.success("✅ Cadastro salvo com sucesso!")
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

# Painel de Pessoas Presentes
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
