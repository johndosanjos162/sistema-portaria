import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(
    page_title="ACCESS GATE - ADMIN", 
    layout="wide", 
    page_icon="🏛️", 
    initial_sidebar_state="expanded"
)

# ====================== CARREGAR IMAGENS ======================
def carregar_imagem(nome_arquivo, nome_descricao):
    """Tenta carregar uma imagem e retorna None se não encontrar"""
    try:
        return Image.open(nome_arquivo)
    except:
        return None

IMAGEM_LOGIN = carregar_imagem("login_image.png", "Login")
IMAGEM_SIDEBAR = carregar_imagem("sidebar_logo.png", "Sidebar")
IMAGEM_HEADER = carregar_imagem("header_logo.png", "Header")

# ====================== DESIGN ADMIN ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* ========== BASE ========== */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0f1525 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* ========== SIDEBAR ADMIN ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e1a 0%, #0d1117 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .sidebar-header {
        text-align: center;
        padding: 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }
    
    .sidebar-title {
        font-size: 22px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }
    
    /* ========== CABEÇALHO ========== */
    .admin-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(13, 17, 23, 0.95));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .badge-admin {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 8px 20px;
        border-radius: 30px;
        display: inline-block;
        font-weight: 700;
        font-size: 14px;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    /* ========== CARDS ========== */
    .admin-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(13, 17, 23, 0.8));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .admin-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .card-title {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #64748b;
        margin-bottom: 10px;
    }
    
    .card-value {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #e2e8f0, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* ========== BOTÕES ========== */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:not([key="sair_final"]):not([key="login_btn"]) {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
    }
    
    .stButton > button:not([key="sair_final"]):not([key="login_btn"]):hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button[key="sair_final"] {
        background: linear-gradient(90deg, #ef4444, #dc2626);
        color: white;
    }
    
    /* ========== INPUTS ========== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #e2e8f0;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(13, 17, 23, 0.9));
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        font-weight: 600;
    }
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.5);
        padding: 5px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        color: #94a3b8;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    
    /* ========== SEARCH CONTAINER ========== */
    .search-container {
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* ========== RESULTADOS ========== */
    .results-count {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
if IMAGEM_SIDEBAR:
    st.sidebar.image(IMAGEM_SIDEBAR, use_container_width=True)
else:
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">🏛️ ACCESS GATE</div>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")

# Menu com ícones realistas
st.sidebar.markdown("### 📋 MENU")
st.sidebar.markdown("• 🏠 **Dashboard**")
st.sidebar.markdown("• 👤 **Colaboradores**")
st.sidebar.markdown("• 🔧 **Prestadores**")
st.sidebar.markdown("• 📅 **Histórico**")
st.sidebar.markdown("• ⚙️ **Configurações**")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ INFO")
st.sidebar.markdown(f"• 👑 **Perfil:** {st.session_state.perfil if 'perfil' in st.session_state else '---'}")
st.sidebar.markdown("• 🟢 **Status:** Online")
st.sidebar.markdown("• 📦 **Versão:** 2.0.0")

# ====================== SESSÃO ======================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "perfil" not in st.session_state:
    st.session_state.perfil = ""
if "search_term_exclusao" not in st.session_state:
    st.session_state.search_term_exclusao = ""

# ====================== LOGIN ======================
if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(13, 17, 23, 0.95));
                    backdrop-filter: blur(20px);
                    border-radius: 24px;
                    padding: 50px 40px;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
                ">
            """, unsafe_allow_html=True)
            
            if IMAGEM_LOGIN:
                st.image(IMAGEM_LOGIN, use_container_width=True)
            else:
                st.markdown("""
                    <div style='text-align:center; margin: 20px 0;'>
                        <div style='
                            width: 120px;
                            height: 120px;
                            margin: 0 auto;
                            background: linear-gradient(135deg, #667eea, #764ba2);
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        '>
                            <span style='font-size: 50px;'>🏛️</span>
                        </div>
                        <h2 style='margin-top: 20px;'>ACCESS GATE</h2>
                        <p style='color: #64748b;'>Sistema Administrativo</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center;'>🔐 Acesso Administrativo</h3>", unsafe_allow_html=True)
            
            senha = st.text_input("Senha de acesso:", type="password", key="senha_login", placeholder="••••••••")
            
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
                    st.error("❌ Acesso negado")
            
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ====================== HEADER ======================
st.markdown(f"""
    <div class="admin-header">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div style='display: flex; align-items: center; gap: 15px;'>
                {'<img src="data:image/png;base64,..." width="50">' if IMAGEM_HEADER else '<span style="font-size: 40px;">🏛️</span>'}
                <div>
                    <h1 style='margin: 0; font-size: 24px;'>PAINEL ADMINISTRATIVO</h1>
                    <p style='margin: 0; color: #64748b; font-size: 12px;'>Controle de Acesso Hospitalar</p>
                </div>
            </div>
            <div style='display: flex; align-items: center; gap: 20px;'>
                <div class="badge-admin">
                    👑 {st.session_state.perfil}
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([8, 1, 1])
with col3:
    if st.button("🚪 SAIR", key="sair_final", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

# ====================== DASHBOARD ======================
pessoas_presentes = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
total_presentes = len(pessoas_presentes)
total_colaboradores = len(supabase.table("Pessoas").select("*").execute().data)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="admin-card">
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div class="card-title">📍 PRESENTES</div>
                    <div class="card-value">{total_presentes}</div>
                </div>
                <div style='font-size: 35px;'>👥</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="admin-card">
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div class="card-title">📋 CADASTRADOS</div>
                    <div class="card-value">{total_colaboradores}</div>
                </div>
                <div style='font-size: 35px;'>📊</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="admin-card">
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div class="card-title">🏥 SETORES</div>
                    <div class="card-value">11</div>
                </div>
                <div style='font-size: 35px;'>🏛️</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="admin-card">
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <div class="card-title">🕒 HOJE</div>
                    <div class="card-value">---</div>
                </div>
                <div style='font-size: 35px;'>📅</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ====================== CADASTRO ======================
st.markdown("### ✚ Cadastro de Nova Pessoa")

with st.expander("📋 Formulário de Cadastro", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("📄 CPF *", key="novo_cpf", placeholder="000.000.000-00")
    novo_nome = col_b.text_input("👤 Nome Completo *", key="novo_nome", placeholder="Digite o nome completo")
    novo_empresa = col_c.text_input("🏢 Empresa", key="novo_empresa", placeholder="Empresa (opcional)")
    
    if st.button("💾 Salvar Cadastro", key="salvar_cadastro", type="primary"):
        if novo_cpf and novo_nome:
            try:
                supabase.table("Pessoas").insert({
                    "cpf": novo_cpf.strip(),
                    "nome": novo_nome.strip().upper(),
                    "empresa": novo_empresa.strip().upper() if novo_empresa else ""
                }).execute()
                st.success("✅ Cadastro salvo com sucesso!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {e}")
        else:
            st.error("❌ CPF e Nome Completo são obrigatórios.")

st.markdown("---")

# ====================== REGISTRO DE ENTRADA ======================
st.markdown("### 📋 Registrar Movimentação")

tipo = st.radio("👥 Tipo de Pessoa:", ["👨‍💼 Colaborador Interno", "🔧 Prestador de Serviço"], horizontal=True)

if tipo == "👨‍💼 Colaborador Interno":
    destinos = ["🏥 C.C", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção", "🧪 Laboratório", "💊 Farmacia"]
else:
    destinos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

c1, c2, c3 = st.columns([2, 2, 1])
cpf_input = c1.text_input("📄 CPF:", key="cpf_entrada", placeholder="Digite o CPF")
setor_escolhido = c2.selectbox("📍 Destino:", destinos, key="destino")

if c3.button("✅ Registrar Entrada", type="primary", key="btn_entrada"):
    if cpf_input:
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input.strip()).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'],
                "nome": p[0]['nome'],
                "empresa": p[0].get('empresa', ''),
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "data_saida": ""
            }).execute()
            st.success(f"✅ Entrada registrada para **{setor_escolhido}**!")
            st.rerun()
        else:
            st.error("❌ CPF não cadastrado")
    else:
        st.warning("⚠️ Digite o CPF")

st.markdown("---")

# ====================== PESSOAS PRESENTES ======================
st.markdown("### 📍 Pessoas Presentes no Hospital")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    tabs = st.tabs(["📊 Todos", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"])
    
    with tabs[0]:
        for p in dados:
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
                col1.write(f"**👤 {p['nome']}**")
                col2.write(f"📍 {p['setor_destino']}")
                col3.write(f"🏢 {p.get('empresa', 'N/A')}")
                if col4.button("🚪 Saída", key=f"saida_{p['id']}"):
                    supabase.table("movimentacao").update({
                        "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }).eq("id", p['id']).execute()
                    st.success(f"✅ Saída registrada")
                    st.rerun()
                st.markdown("<hr style='margin: 5px 0; opacity: 0.1;'>", unsafe_allow_html=True)

    for i, setor in enumerate(["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"], 1):
        with tabs[i]:
            pessoas_setor = [r for r in dados if r.get('setor_destino') == setor]
            if pessoas_setor:
                for p in pessoas_setor:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
                        col1.write(f"**👤 {p['nome']}**")
                        col2.write(f"🏢 {p.get('empresa', 'N/A')}")
                        col3.write(f"🕒 {p['data_entrada']}")
                        if col4.button("🚪 Saída", key=f"saida2_{p['id']}"):
                            supabase.table("movimentacao").update({
                                "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            }).eq("id", p['id']).execute()
                            st.rerun()
                        st.markdown("<hr style='margin: 5px 0; opacity: 0.1;'>", unsafe_allow_html=True)
            else:
                st.info(f"📭 Nenhuma pessoa no setor {setor}")
else:
    st.info("🏢 Nenhuma pessoa presente no momento")

st.markdown("---")

# ====================== HISTÓRICO ======================
with st.expander("🕒 Histórico Completo de Movimentações"):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        df = pd.DataFrame(todos_dados)
        st.dataframe(df, use_container_width=True, height=400)
        
        st.markdown("---")
        col_del1, col_del2, col_del3 = st.columns([1, 2, 1])
        with col_del2:
            id_excluir = st.number_input("ID para excluir:", min_value=1, step=1, key="id_excluir")
            if st.button("🗑️ Excluir Registro", key="del_reg", use_container_width=True):
                try:
                    supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
                    st.success(f"✅ Registro {id_excluir} excluído!")
                    st.rerun()
                except:
                    st.error("❌ Erro ao excluir")
    else:
        st.info("📭 Nenhum registro encontrado")

# ====================== GESTÃO DE CADASTROS COM LUPA INTEGRADA ======================
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        
        todos_colaboradores = supabase.table("Pessoas").select("id, nome, cpf, empresa").order("nome").execute().data
        
        if todos_colaboradores:
            
            st.markdown("### 🔍 Pesquisar e Excluir Cadastro")
            
            # Container para pesquisa e resultados lado a lado
            col_search, col_results = st.columns([1, 1])
            
            with col_search:
                st.markdown("#### 🔎 Barra de Pesquisa")
                search_term = st.text_input(
                    "🔍",
                    placeholder="Digite nome, CPF ou empresa...",
                    key="search_term_exclusao",
                    label_visibility="collapsed"
                )
                
                if search_term:
                    search_lower = search_term.lower()
                    resultados_filtrados = [
                        p for p in todos_colaboradores 
                        if search_lower in p['nome'].lower() 
                        or search_lower in p['cpf'].lower() 
                        or search_lower in p.get('empresa', '').lower()
                    ]
                    st.markdown(f"""
                        <div class="results-count">
                            📊 {len(resultados_filtrados)} resultado(s) encontrado(s) para: <strong>{search_term}</strong>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    resultados_filtrados = todos_colaboradores
                    st.markdown(f"""
                        <div class="results-count">
                            📋 Total de cadastros: <strong>{len(resultados_filtrados)}</strong> pessoas
                        </div>
                    """, unsafe_allow_html=True)
            
            with col_results:
                st.markdown("#### 👤 Selecione para Excluir")
                
                if resultados_filtrados:
                    # Lista para o selectbox
                    lista_nomes = [
                        f"{p['nome']} - CPF: {p['cpf']} {f'| Emp: {p["empresa"]}' if p.get('empresa') else ''}" 
                        for p in resultados_filtrados
                    ]
                    
                    # Selectbox com os resultados
                    selecionado = st.selectbox(
                        "👤 Pessoa selecionada:",
                        lista_nomes,
                        key="select_excluir",
                        label_visibility="collapsed"
                    )
                    
                    # Encontrar a pessoa selecionada
                    idx_selecionado = lista_nomes.index(selecionado)
                    pessoa_selecionada = resultados_filtrados[idx_selecionado]
                    
                    # Card com informações da pessoa selecionada
                    st.markdown(f"""
                        <div style='
                            background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
                            border-radius: 10px;
                            padding: 12px;
                            margin-top: 10px;
                            border-left: 3px solid #667eea;
                        '>
                            <div style='font-size: 13px; color: #94a3b8;'>PESSOA SELECIONADA</div>
                            <div style='font-weight: 700; margin-top: 5px;'>👤 {pessoa_selecionada['nome']}</div>
                            <div style='font-size: 12px; color: #64748b;'>📄 CPF: {pessoa_selecionada['cpf']}</div>
                            {f"<div style='font-size: 12px; color: #64748b;'>🏢 Empresa: {pessoa_selecionada['empresa']}</div>" if pessoa_selecionada.get('empresa') else ""}
                        </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    st.warning(f"⚠️ Nenhum resultado encontrado para: {search_term}")
                    if st.button("🔄 Mostrar todos", key="show_all"):
                        st.session_state.search_term_exclusao = ""
                        st.rerun()
            
            # Área de exclusão (abaixo das duas colunas)
            if resultados_filtrados and 'pessoa_selecionada' in locals():
                st.markdown("---")
                st.markdown("#### 🗑️ Confirmar Exclusão")
                
                col_confirm1, col_confirm2 = st.columns(2)
                
                with col_confirm1:
                    confirmar = st.checkbox("✅ Confirmo que desejo excluir este cadastro PERMANENTEMENTE")
                
                with col_confirm2:
                    if confirmar:
                        with st.popover("⚠️ CLIQUE PARA EXCLUIR", use_container_width=True):
                            st.error("🚨 **ATENÇÃO!** Esta ação é IRREVERSÍVEL!")
                            st.write(f"Você está prestes a excluir:")
                            st.write(f"**{pessoa_selecionada['nome']}**")
                            st.write(f"CPF: {pessoa_selecionada['cpf']}")
                            st.markdown("---")
                            if st.button("🗑️ SIM, EXCLUIR PERMANENTEMENTE", key="del_cad", use_container_width=True):
                                try:
                                    supabase.table("Pessoas").delete().eq("cpf", pessoa_selecionada['cpf']).execute()
                                    st.success(f"✅ Cadastro de **{pessoa_selecionada['nome']}** excluído com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro ao excluir: {e}")
                    else:
                        st.info("🔒 **Marque a confirmação** para habilitar a exclusão")
        
        else:
            st.info("📭 Nenhum cadastro encontrado no sistema")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #64748b; font-size: 12px;'>
        <p>🏛️ ACCESS GATE - Sistema Administrativo de Controle de Acesso</p>
        <p>© 2024 - Todos os direitos reservados</p>
    </div>
""", unsafe_allow_html=True)
