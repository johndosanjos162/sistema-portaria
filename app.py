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
    try:
        return Image.open(nome_arquivo)
    except:
        return None

IMAGEM_LOGIN = carregar_imagem("login_image.png", "Login")
IMAGEM_SIDEBAR = carregar_imagem("sidebar_logo.png", "Sidebar")
IMAGEM_HEADER = carregar_imagem("header_logo.png", "Header")

# ====================== IMAGEM DE FUNDO (VIGILANTE TECNOLÓGICO) ======================
# URL da imagem (Pexels - gratuita para uso comercial)
BACKGROUND_URL = "https://images.pexels.com/photos/5380642/security-guard-monitoring-cctv-footage-2021-08-26-21-47-58-utc.jpg"

# ====================== DESIGN ADMIN COM FUNDO ======================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Fundo com imagem de vigilante + tecnologia */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.8)), url("{BACKGROUND_URL}");
        background-size: cover;
        background-position: center 30%;
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Sidebar com leve transparência para dar destaque ao fundo */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(0, 20, 40, 0.92), rgba(0, 10, 25, 0.96));
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }}
    
    .sidebar-header {{
        text-align: center;
        padding: 20px;
        border-bottom: 1px solid rgba(0, 212, 255, 0.3);
        margin-bottom: 20px;
    }}
    
    .sidebar-title {{
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff, #667eea);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }}
    
    /* Cabeçalho com efeito vidro */
    .admin-header {{
        background: linear-gradient(135deg, rgba(0, 20, 40, 0.85), rgba(0, 10, 25, 0.9));
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 15px 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }}
    
    .badge-admin {{
        background: linear-gradient(135deg, #00d4ff, #667eea);
        padding: 8px 24px;
        border-radius: 40px;
        font-weight: 700;
        font-size: 14px;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
    }}
    
    /* Cards com transparência e borda neon */
    .admin-card {{
        background: rgba(0, 20, 40, 0.75);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0, 212, 255, 0.25);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}
    
    .admin-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(0, 212, 255, 0.2);
        border-color: rgba(0, 212, 255, 0.5);
    }}
    
    .card-title {{
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #a0c4ff;
    }}
    
    .card-value {{
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff, #90e0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    
    /* Botões principais */
    .stButton > button {{
        border-radius: 40px;
        font-weight: 600;
        transition: all 0.2s;
        border: none;
    }}
    
    .stButton > button:not([key="sair_final"]):not([key="login_btn"]) {{
        background: linear-gradient(90deg, #00d4ff, #667eea);
        color: white;
        box-shadow: 0 2px 8px rgba(0, 212, 255, 0.3);
    }}
    
    .stButton > button:not([key="sair_final"]):not([key="login_btn"]):hover {{
        transform: scale(1.02);
        box-shadow: 0 4px 16px rgba(0, 212, 255, 0.5);
    }}
    
    /* Inputs com fundo escuro e borda sutil */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {{
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid rgba(0, 212, 255, 0.4);
        border-radius: 16px;
        color: #f0f0f0;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: #00d4ff;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.3);
    }}
    
    /* Expander e Tabs estilizados */
    .streamlit-expanderHeader {{
        background: rgba(0, 20, 40, 0.85);
        backdrop-filter: blur(8px);
        border-radius: 16px;
        border: 1px solid rgba(0, 212, 255, 0.3);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: rgba(0, 0, 0, 0.4);
        padding: 6px;
        border-radius: 40px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 32px;
        padding: 6px 20px;
        font-weight: 600;
        color: #cbd5e1;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #00d4ff, #667eea);
        color: white;
    }}
    
    /* Contador de resultados */
    .results-count {{
        background: rgba(0, 212, 255, 0.1);
        border-radius: 16px;
        padding: 8px 12px;
        font-size: 13px;
        color: #b0e0ff;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 20px;
        color: #64748b;
        font-size: 12px;
        border-top: 1px solid rgba(0, 212, 255, 0.2);
        margin-top: 30px;
    }}
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
if IMAGEM_SIDEBAR:
    st.sidebar.image(IMAGEM_SIDEBAR, use_container_width=True)
else:
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">🔐 ACCESS GATE</div>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 MENU")
st.sidebar.markdown("• 🏠 **Dashboard**")
st.sidebar.markdown("• 👤 **Colaboradores**")
st.sidebar.markdown("• 🔧 **Prestadores**")
st.sidebar.markdown("• 📅 **Histórico**")
st.sidebar.markdown("• ⚙️ **Configurações**")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ INFO")
if "perfil" in st.session_state:
    st.sidebar.markdown(f"• 👑 **Perfil:** {st.session_state.perfil}")
else:
    st.sidebar.markdown("• 👑 **Perfil:** ---")
st.sidebar.markdown("• 🟢 **Status:** Online 24/7")
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
                    background: rgba(0, 20, 40, 0.85);
                    backdrop-filter: blur(20px);
                    border-radius: 32px;
                    padding: 40px 30px;
                    border: 1px solid rgba(0, 212, 255, 0.4);
                    box-shadow: 0 20px 40px rgba(0,0,0,0.5);
                ">
            """, unsafe_allow_html=True)
            if IMAGEM_LOGIN:
                st.image(IMAGEM_LOGIN, use_container_width=True)
            else:
                st.markdown("""
                    <div style='text-align:center; margin-bottom: 20px;'>
                        <div style="
                            width: 100px; height: 100px; background: linear-gradient(135deg, #00d4ff, #667eea);
                            border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto;">
                            <span style="font-size: 48px;">🛡️</span>
                        </div>
                        <h2>ACCESS GATE</h2>
                        <p style="color:#94a3b8;">Controle de Acesso com Tecnologia</p>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
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
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 15px;">
                <span style="font-size: 40px;">🛡️</span>
                <div>
                    <h1 style="margin:0; font-size: 26px;">PAINEL ADMINISTRATIVO</h1>
                    <p style="margin:0; color: #00d4ff;">Monitoramento Inteligente de Acesso</p>
                </div>
            </div>
            <div class="badge-admin">👑 {st.session_state.perfil}</div>
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
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">📍 PRESENTES</div><div class="card-value">{total_presentes}</div></div>
                <div style="font-size:36px;">👥</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">📋 CADASTRADOS</div><div class="card-value">{total_colaboradores}</div></div>
                <div style="font-size:36px;">📊</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">🏥 SETORES</div><div class="card-value">11</div></div>
                <div style="font-size:36px;">🏛️</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">🎥 CFTV</div><div class="card-value">24/7</div></div>
                <div style="font-size:36px;">📹</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ====================== CADASTRO ======================
st.markdown("### ✚ Cadastro de Nova Pessoa")
with st.expander("📋 Formulário de Cadastro", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("📄 CPF *", placeholder="000.000.000-00")
    novo_nome = col_b.text_input("👤 Nome Completo *")
    novo_empresa = col_c.text_input("🏢 Empresa")
    if st.button("💾 Salvar Cadastro", type="primary"):
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
                st.error(f"❌ Erro: {e}")
        else:
            st.error("❌ CPF e Nome são obrigatórios.")

st.markdown("---")

# ====================== REGISTRO DE ENTRADA ======================
st.markdown("### 📋 Registrar Movimentação")
tipo = st.radio("👥 Tipo de Pessoa:", ["👨‍💼 Colaborador Interno", "🔧 Prestador de Serviço"], horizontal=True)
if tipo == "👨‍💼 Colaborador Interno":
    destinos = ["🏥 C.C", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção", "🧪 Laboratório", "💊 Farmacia"]
else:
    destinos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

c1, c2, c3 = st.columns([2,2,1])
cpf_input = c1.text_input("📄 CPF:", key="cpf_entrada", placeholder="Digite o CPF")
setor_escolhido = c2.selectbox("📍 Destino:", destinos)

if c3.button("✅ Registrar Entrada", type="primary"):
    if cpf_input:
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input.strip()).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'], "nome": p[0]['nome'], "empresa": p[0].get('empresa',''),
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
            col1, col2, col3, col4 = st.columns([4,3,2,2])
            col1.write(f"**👤 {p['nome']}**")
            col2.write(f"📍 {p['setor_destino']}")
            col3.write(f"🏢 {p.get('empresa','N/A')}")
            if col4.button("🚪 Saída", key=f"saida_{p['id']}"):
                supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                st.rerun()
            st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
    for i, setor in enumerate(["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"], 1):
        with tabs[i]:
            pessoas_setor = [r for r in dados if r['setor_destino'] == setor]
            if pessoas_setor:
                for p in pessoas_setor:
                    col1, col2, col3, col4 = st.columns([4,3,2,2])
                    col1.write(f"**👤 {p['nome']}**")
                    col2.write(f"🏢 {p.get('empresa','N/A')}")
                    col3.write(f"🕒 {p['data_entrada']}")
                    if col4.button("🚪 Saída", key=f"saida2_{p['id']}"):
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                        st.rerun()
                    st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
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
        id_excluir = st.number_input("ID para excluir:", min_value=1, step=1)
        if st.button("🗑️ Excluir Registro"):
            try:
                supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
                st.success(f"Registro {id_excluir} excluído!")
                st.rerun()
            except:
                st.error("Erro ao excluir")
    else:
        st.info("Nenhum registro encontrado")

# ====================== GESTÃO DE CADASTROS (COM LUPA) ======================
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        todos = supabase.table("Pessoas").select("id, nome, cpf, empresa").order("nome").execute().data
        if todos:
            col_search, col_results = st.columns([1,1])
            with col_search:
                search_term = st.text_input("🔍 Pesquisar", placeholder="Nome, CPF ou empresa...", key="search_exclusao", label_visibility="collapsed")
                if search_term:
                    filtrados = [p for p in todos if search_term.lower() in p['nome'].lower() or search_term.lower() in p['cpf'].lower() or search_term.lower() in p.get('empresa','').lower()]
                    st.markdown(f"📊 {len(filtrados)} resultado(s) para: **{search_term}**")
                else:
                    filtrados = todos
                    st.markdown(f"📋 Total: **{len(filtrados)}** pessoas")
            with col_results:
                lista = [f"{p['nome']} - CPF: {p['cpf']}" + (f" | {p['empresa']}" if p.get('empresa') else "") for p in filtrados]
                if lista:
                    selecionado = st.selectbox("Selecione para excluir:", lista, label_visibility="collapsed")
                    idx = lista.index(selecionado)
                    pessoa = filtrados[idx]
                    st.markdown(f"""
                        <div style="background:rgba(0,212,255,0.1); border-radius:12px; padding:12px; border-left:3px solid #00d4ff;">
                            <b>👤 {pessoa['nome']}</b><br>
                            📄 CPF: {pessoa['cpf']}<br>
                            🏢 Empresa: {pessoa.get('empresa','N/A')}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Nenhum resultado encontrado")
            if 'pessoa' in locals():
                st.markdown("---")
                confirmar = st.checkbox("✅ Confirmar exclusão permanente")
                if confirmar:
                    with st.popover("⚠️ CLIQUE PARA EXCLUIR", use_container_width=True):
                        st.error("Ação irreversível!")
                        if st.button("🗑️ SIM, EXCLUIR", key="del_cad"):
                            supabase.table("Pessoas").delete().eq("cpf", pessoa['cpf']).execute()
                            st.success("Cadastro excluído!")
                            st.rerun()
                else:
                    st.info("Marque a confirmação para habilitar a exclusão")
        else:
            st.info("Nenhum cadastro encontrado")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
    <div class="footer">
        🛡️ ACCESS GATE - Segurança e Tecnologia em Controle de Acesso<br>
        Monitoramento 24/7 - Sistema com CFTV Integrado
    </div>
""", unsafe_allow_html=True)
