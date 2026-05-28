import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image
import base64

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(
    page_title="ACCESS GATE - SECURITY", 
    layout="wide", 
    page_icon="🔮", 
    initial_sidebar_state="expanded"
)

# ====================== FUNÇÃO PARA GERAR HTML PARA IMPRESSÃO/PDF ======================
def gerar_html_impressao(df, titulo):
    """Gera um HTML formatado para impressão/salvar como PDF."""
    if df.empty:
        return None
    
    colunas = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida']
    colunas_presentes = [c for c in colunas if c in df.columns]
    
    linhas_html = ""
    for _, row in df.iterrows():
        linhas_html += "<tr>"
        for col in colunas_presentes:
            valor = str(row[col]) if pd.notna(row[col]) else ''
            linhas_html += f"<td>{valor}</td>"
        linhas_html += "</tr>"
    
    cabecalho_html = "".join([f"<th>{col.upper()}</th>" for col in colunas_presentes])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                margin: 2cm;
                background: white;
            }}
            h1 {{
                text-align: center;
                color: #0a0e1a;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            .sub {{
                text-align: center;
                color: #555;
                font-size: 12px;
                margin-bottom: 30px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 10px;
            }}
            th {{
                background: #0a0e1a;
                color: white;
                padding: 8px;
                text-align: left;
                font-weight: bold;
            }}
            td {{
                border: 1px solid #ccc;
                padding: 6px;
                text-align: left;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            @media print {{
                body {{
                    margin: 1cm;
                }}
                .no-print {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>ACCESS GATE - {titulo}</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        <table>
            <thead>
                <tr>{cabecalho_html}</tr>
            </thead>
            <tbody>
                {linhas_html}
            </tbody>
        </table>
        <div class="no-print" style="text-align:center; margin-top:30px;">
            <button onclick="window.print();" style="padding:10px 20px; font-size:16px;">🖨️ Imprimir / Salvar como PDF</button>
            <p style="font-size:12px; color:#666;">Clique no botão ou pressione Ctrl+P e escolha "Salvar como PDF".</p>
        </div>
    </body>
    </html>
    """
    return html

# ====================== CARREGAR IMAGENS (OPCIONAL) ======================
def carregar_imagem(nome_arquivo, nome_descricao):
    try:
        return Image.open(nome_arquivo)
    except:
        return None

IMAGEM_LOGIN = carregar_imagem("login_image.png", "Login")
IMAGEM_SIDEBAR = carregar_imagem("sidebar_logo.png", "Sidebar")
IMAGEM_HEADER = carregar_imagem("header_logo.png", "Header")

# ====================== IMAGEM DE FUNDO (FUTURISTA) ======================
BACKGROUND_URL = "https://images.pexels.com/photos/5380642/security-guard-monitoring-cctv-footage-2021-08-26-21-47-58-utc.jpg"

# ====================== DESIGN FUTURISTA ======================
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* ========== BASE ========== */
    .stApp {{
        background: radial-gradient(circle at 20% 50%, rgba(0, 10, 20, 0.95), rgba(0, 0, 0, 0.98)), url("{BACKGROUND_URL}");
        background-size: cover;
        background-position: center 30%;
        background-attachment: fixed;
        font-family: 'Orbitron', 'Inter', monospace;
    }}
    
    /* ========== SIDEBAR NEON ========== */
    [data-testid="stSidebar"] {{
        background: linear-gradient(135deg, rgba(0, 5, 15, 0.95), rgba(0, 0, 0, 0.98));
        backdrop-filter: blur(15px);
        border-right: 2px solid rgba(0, 255, 255, 0.4);
        box-shadow: -5px 0 20px rgba(0, 255, 255, 0.2);
    }}
    
    .sidebar-header {{
        text-align: center;
        padding: 20px;
        border-bottom: 2px solid #0ff;
        box-shadow: 0 0 10px #0ff;
        margin-bottom: 20px;
    }}
    
    .sidebar-title {{
        font-size: 28px;
        font-weight: 900;
        background: linear-gradient(135deg, #0ff, #f0f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 3px;
        text-shadow: 0 0 5px #0ff;
    }}
    
    /* ========== CABEÇALHO ========== */
    .admin-header {{
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 15px 25px;
        margin-bottom: 25px;
        border: 1px solid rgba(0, 255, 255, 0.6);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        animation: glow 2s ease-in-out infinite alternate;
    }}
    
    @keyframes glow {{
        from {{ box-shadow: 0 0 10px rgba(0, 255, 255, 0.3); }}
        to {{ box-shadow: 0 0 25px rgba(0, 255, 255, 0.6); }}
    }}
    
    .badge-admin {{
        background: linear-gradient(135deg, #0ff, #f0f);
        padding: 8px 24px;
        border-radius: 40px;
        font-weight: 800;
        font-size: 14px;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.6);
        color: #000;
        text-transform: uppercase;
    }}
    
    /* ========== CARDS ========== */
    .admin-card {{
        background: rgba(0, 5, 15, 0.75);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0, 255, 255, 0.4);
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
    }}
    
    .admin-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
        border-color: #0ff;
    }}
    
    .card-title {{
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #0ff;
        font-weight: 600;
    }}
    
    .card-value {{
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(135deg, #ffffff, #0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 5px rgba(0, 255, 255, 0.5);
    }}
    
    /* ========== BOTÕES ========== */
    .stButton > button {{
        border-radius: 50px;
        font-weight: 700;
        transition: all 0.3s ease;
        border: none;
        font-family: 'Orbitron', monospace;
        letter-spacing: 1px;
    }}
    
    .stButton > button:not([key="sair_final"]):not([key="login_btn"]) {{
        background: linear-gradient(90deg, #0ff, #00aaff);
        color: #000;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.4);
    }}
    
    .stButton > button:not([key="sair_final"]):not([key="login_btn"]):hover {{
        transform: scale(1.03);
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.8);
        background: linear-gradient(90deg, #00aaff, #0ff);
    }}
    
    .stButton > button[key="sair_final"] {{
        background: linear-gradient(90deg, #f00, #ff4444);
        color: white;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
    }}
    
    /* ========== INPUTS ========== */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {{
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #0ff;
        border-radius: 20px;
        color: #0ff;
        font-family: 'Orbitron', monospace;
        box-shadow: 0 0 5px rgba(0, 255, 255, 0.3);
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: #f0f;
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
        color: #fff;
    }}
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {{
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(8px);
        border-radius: 20px;
        border: 1px solid #0ff;
        font-weight: 700;
        font-family: 'Orbitron', monospace;
        color: #0ff;
    }}
    
    /* ========== TABS ========== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: rgba(0, 0, 0, 0.5);
        padding: 8px;
        border-radius: 50px;
        border: 1px solid rgba(0, 255, 255, 0.3);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 40px;
        padding: 8px 25px;
        font-weight: 600;
        color: #ccc;
        font-family: 'Orbitron', monospace;
        transition: all 0.3s;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #0ff, #f0f);
        color: #000;
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
    }}
    
    /* ========== CHECKBOX ========== */
    .stCheckbox label {{
        color: #0ff;
        font-weight: 500;
    }}
    
    /* ========== DATAFRAME ========== */
    .stDataFrame {{
        background: rgba(0, 0, 0, 0.7);
        border-radius: 15px;
        border: 1px solid #0ff;
    }}
    
    /* ========== ALERTAS ========== */
    .stAlert {{
        background: rgba(0, 0, 0, 0.8);
        border-left: 4px solid #0ff;
        border-radius: 10px;
        color: #0ff;
    }}
    
    /* ========== FOOTER ========== */
    .footer {{
        text-align: center;
        padding: 20px;
        color: #0ff;
        font-size: 11px;
        border-top: 1px solid rgba(0, 255, 255, 0.3);
        margin-top: 30px;
        font-family: 'Orbitron', monospace;
        text-shadow: 0 0 5px #0ff;
    }}
    
    /* ========== TÍTULOS ========== */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Orbitron', monospace;
        color: #0ff;
        text-shadow: 0 0 5px #0ff;
    }}
    
    /* ========== POPOVER ========== */
    div[role="dialog"] {{
        background: rgba(0, 0, 0, 0.95);
        border: 2px solid #0ff;
        border-radius: 20px;
        color: #0ff;
    }}
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
if IMAGEM_SIDEBAR:
    st.sidebar.image(IMAGEM_SIDEBAR, use_container_width=True)
else:
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">🔮 ACCESS GATE</div>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ MENU")
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
st.sidebar.markdown("• 📦 **Versão:** 3.0.0")

# ====================== SESSÃO ======================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "perfil" not in st.session_state:
    st.session_state.perfil = ""
if "search_term_exclusao" not in st.session_state:
    st.session_state.search_term_exclusao = ""
if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = []
if "pending_delete_ids" not in st.session_state:
    st.session_state.pending_delete_ids = []
if "pending_clear_all" not in st.session_state:
    st.session_state.pending_clear_all = False

# ====================== LOGIN ======================
if not st.session_state.logado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
                <div style="
                    background: rgba(0, 0, 0, 0.85);
                    backdrop-filter: blur(20px);
                    border-radius: 40px;
                    padding: 50px 40px;
                    border: 2px solid #0ff;
                    box-shadow: 0 0 50px rgba(0, 255, 255, 0.5);
                ">
            """, unsafe_allow_html=True)
            if IMAGEM_LOGIN:
                st.image(IMAGEM_LOGIN, use_container_width=True)
            else:
                st.markdown("""
                    <div style='text-align:center; margin-bottom: 20px;'>
                        <div style="
                            width: 120px; height: 120px; margin: 0 auto;
                            background: linear-gradient(135deg, #0ff, #f0f);
                            border-radius: 50%;
                            display: flex; align-items: center; justify-content: center;
                            box-shadow: 0 0 30px #0ff;
                        ">
                            <span style="font-size: 60px;">🔮</span>
                        </div>
                        <h2 style="color:#0ff;">ACCESS GATE</h2>
                        <p style="color:#0ff;">Sistema de Segurança Futurista</p>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("<hr style='border-color:#0ff;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align:center; color:#0ff;'>🔐 ACESSO AUTORIZADO</h3>", unsafe_allow_html=True)
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
                <span style="font-size: 45px;">🔮</span>
                <div>
                    <h1 style="margin:0; font-size: 26px;">PAINEL ADMINISTRATIVO</h1>
                    <p style="margin:0; color: #0ff;">Monitoramento Inteligente de Acesso</p>
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
tipo = st.radio("👥 Tipo de Pessoa:", ["🏢 Prestador de serviços", "🔧 Terceirizados"], horizontal=True)

if tipo == "🏢 Prestador de serviços":
    destinos = ["🏥 C.C", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção", "🧪 Laboratório", "💊 Farmacia"]
else:
    destinos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

col_cpf, col_btn_confirma = st.columns([3, 1])
with col_cpf:
    cpf_input = st.text_input("📄 CPF:", key="cpf_entrada", placeholder="Digite o CPF")
with col_btn_confirma:
    if cpf_input and len(cpf_input.strip()) > 0:
        if st.button("✅ CONFIRMAR CPF", key="confirma_cpf"):
            pessoa = supabase.table("Pessoas").select("nome, empresa").eq("cpf", cpf_input.strip()).execute().data
            if pessoa:
                st.session_state.pessoa_confirmada = {
                    "cpf": cpf_input.strip(),
                    "nome": pessoa[0]['nome'],
                    "empresa": pessoa[0].get('empresa', '')
                }
                st.success(f"✅ **Pessoa confirmada:** 👤 {pessoa[0]['nome']} | 🏢 Empresa: {pessoa[0].get('empresa', 'N/A')}")
            else:
                st.error("❌ CPF não cadastrado")
                st.session_state.pessoa_confirmada = None
    else:
        st.button("✅ CONFIRMAR CPF", disabled=True, key="confirma_cpf_disabled")

setor_escolhido = st.selectbox("📍 Destino:", destinos, key="destino")

if st.button("✅ Registrar Entrada", type="primary", key="btn_entrada"):
    if 'pessoa_confirmada' in st.session_state and st.session_state.pessoa_confirmada:
        pessoa = st.session_state.pessoa_confirmada
        supabase.table("movimentacao").insert({
            "cpf": pessoa['cpf'],
            "nome": pessoa['nome'],
            "empresa": pessoa['empresa'],
            "setor_destino": setor_escolhido,
            "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "data_saida": ""
        }).execute()
        st.success(f"✅ Entrada registrada para **{setor_escolhido}**!")
        st.session_state.pessoa_confirmada = None
        st.rerun()
    else:
        st.warning("⚠️ Confirme o CPF antes de registrar a entrada.")

st.markdown("---")

# ====================== PESSOAS PRESENTES ======================
st.markdown("### 📍 Pessoas Presentes no Hospital")

dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    st.markdown("#### 🔍 Pesquisar por CPF para registrar saída")
    col_pesquisa, col_botao = st.columns([3, 1])
    with col_pesquisa:
        cpf_pesquisa = st.text_input("CPF:", key="cpf_saida", placeholder="Digite o CPF da pessoa")
    with col_botao:
        if st.button("🔎 Buscar", key="buscar_saida"):
            if cpf_pesquisa:
                pessoa_encontrada = None
                for p in dados:
                    if p['cpf'] == cpf_pesquisa.strip():
                        pessoa_encontrada = p
                        break
                if pessoa_encontrada:
                    st.session_state.pessoa_saida = pessoa_encontrada
                    st.success(f"✅ Pessoa encontrada: **{pessoa_encontrada['nome']}** (CPF: {pessoa_encontrada['cpf']})")
                else:
                    st.error("❌ CPF não encontrado entre as pessoas presentes.")
                    st.session_state.pessoa_saida = None
            else:
                st.warning("Digite um CPF para buscar.")
    
    if 'pessoa_saida' in st.session_state and st.session_state.pessoa_saida:
        with st.container():
            st.markdown("---")
            st.markdown("#### 🚪 Registrar Saída da pessoa encontrada:")
            col_info, col_sair = st.columns([4, 1])
            with col_info:
                p = st.session_state.pessoa_saida
                st.write(f"**👤 Nome:** {p['nome']}")
                st.write(f"**📄 CPF:** {p['cpf']}")
                st.write(f"**🏢 Empresa:** {p.get('empresa', 'N/A')}")
                st.write(f"**📍 Setor:** {p['setor_destino']}")
                st.write(f"**🕒 Entrada:** {p['data_entrada']}")
            with col_sair:
                if st.button("🚪 Registrar Saída", key="sair_pesquisado"):
                    supabase.table("movimentacao").update({
                        "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }).eq("id", p['id']).execute()
                    st.success(f"✅ Saída registrada para {p['nome']}")
                    st.session_state.pessoa_saida = None
                    st.rerun()
            st.markdown("---")
    
    st.markdown("#### 📋 Lista completa de presentes")
    tabs = st.tabs(["📊 Prestador de Serviço", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"])
    
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
            setor_normalizado = setor.split()[-1] if ' ' in setor else setor
            pessoas_setor = [r for r in dados if setor_normalizado in r['setor_destino']]
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

# ====================== HISTÓRICO COMPLETO ======================
with st.expander("🕒 Histórico Completo de Movimentações", expanded=True):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    
    if todos_dados:
        df = pd.DataFrame(todos_dados)
        
        st.markdown("### 📄 Gerar Relatório para Impressão/PDF")
        st.info("💡 Clique no botão, depois use **Ctrl+P** (ou **Cmd+P**) e escolha **'Salvar como PDF'**.")
        
        st.markdown("#### 🔹 Histórico Geral")
        if st.button("📑 Abrir relatório completo", key="html_all"):
            html = gerar_html_impressao(df, "RELATÓRIO COMPLETO DE MOVIMENTAÇÕES")
            if html:
                b64 = base64.b64encode(html.encode()).decode()
                href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Clique aqui para abrir o relatório (nova aba)</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.caption("Após abrir, pressione Ctrl+P e escolha 'Salvar como PDF'.")
        
        st.markdown("---")
        
        st.markdown("#### 🔹 Relatório por Setor (PDF separado para cada setor)")
        setores_unicos = df['setor_destino'].unique()
        setores_desejados = ["C.C", "GRSA", "Brasanitas"]
        mapa_setores = {}
        for setor in setores_desejados:
            encontrado = False
            for valor in setores_unicos:
                if setor.lower() in str(valor).lower():
                    mapa_setores[setor] = valor
                    encontrado = True
                    break
            if not encontrado:
                mapa_setores[setor] = setor
        
        col1, col2, col3 = st.columns(3)
        with col1:
            setor_nome = "C.C"
            valor_real = mapa_setores[setor_nome]
            df_setor = df[df['setor_destino'] == valor_real]
            if not df_setor.empty:
                if st.button(f"🏥 {setor_nome} ({len(df_setor)} registros) - PDF", key=f"pdf_setor_{setor_nome}"):
                    html = gerar_html_impressao(df_setor, f"RELATÓRIO - SETOR {setor_nome}")
                    if html:
                        b64 = base64.b64encode(html.encode()).decode()
                        href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir PDF do setor {setor_nome}</a>'
                        st.markdown(href, unsafe_allow_html=True)
            else:
                st.button(f"🏥 {setor_nome} (vazio)", disabled=True, key=f"btn_{setor_nome}_pdf")
        
        with col2:
            setor_nome = "GRSA"
            valor_real = mapa_setores[setor_nome]
            df_setor = df[df['setor_destino'] == valor_real]
            if not df_setor.empty:
                if st.button(f"🔧 {setor_nome} ({len(df_setor)} registros) - PDF", key=f"pdf_setor_{setor_nome}"):
                    html = gerar_html_impressao(df_setor, f"RELATÓRIO - SETOR {setor_nome}")
                    if html:
                        b64 = base64.b64encode(html.encode()).decode()
                        href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir PDF do setor {setor_nome}</a>'
                        st.markdown(href, unsafe_allow_html=True)
            else:
                st.button(f"🔧 {setor_nome} (vazio)", disabled=True, key=f"btn_{setor_nome}_pdf")
        
        with col3:
            setor_nome = "Brasanitas"
            valor_real = mapa_setores[setor_nome]
            df_setor = df[df['setor_destino'] == valor_real]
            if not df_setor.empty:
                if st.button(f"🏭 {setor_nome} ({len(df_setor)} registros) - PDF", key=f"pdf_setor_{setor_nome}"):
                    html = gerar_html_impressao(df_setor, f"RELATÓRIO - SETOR {setor_nome}")
                    if html:
                        b64 = base64.b64encode(html.encode()).decode()
                        href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir PDF do setor {setor_nome}</a>'
                        st.markdown(href, unsafe_allow_html=True)
            else:
                st.button(f"🏭 {setor_nome} (vazio)", disabled=True, key=f"btn_{setor_nome}_pdf")
        
        st.markdown("---")
        
        st.markdown("#### 🔹 Relatório por Empresa (Prestadores de Serviço)")
        empresas_excluir = ["BRASANITAS", "GRSA", "C.C"]
        todas_empresas = df['empresa'].dropna().unique()
        empresas_filtradas = [emp for emp in todas_empresas if emp.upper() not in [e.upper() for e in empresas_excluir]]
        
        if empresas_filtradas:
            if st.button("📑 Gerar PDF para TODOS os Prestadores de Serviço (todas as empresas)", key="html_todos_prestadores"):
                df_prestadores = df[df['empresa'].isin(empresas_filtradas)]
                if not df_prestadores.empty:
                    html = gerar_html_impressao(df_prestadores, "PRESTADORES DE SERVIÇO (TODAS AS EMPRESAS)")
                    if html:
                        b64 = base64.b64encode(html.encode()).decode()
                        href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir PDF de TODOS os Prestadores</a>'
                        st.markdown(href, unsafe_allow_html=True)
            
            empresa_selecionada = st.selectbox("Ou selecione uma empresa específica:", sorted(empresas_filtradas), key="select_empresa_html")
            if empresa_selecionada:
                df_empresa = df[df['empresa'] == empresa_selecionada]
                st.write(f"📌 **{len(df_empresa)} registros** para a empresa **{empresa_selecionada}**")
                if st.button(f"📑 Gerar PDF para {empresa_selecionada}", key="html_empresa"):
                    html = gerar_html_impressao(df_empresa, f"RELATÓRIO - EMPRESA {empresa_selecionada}")
                    if html:
                        b64 = base64.b64encode(html.encode()).decode()
                        href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir PDF da empresa {empresa_selecionada}</a>'
                        st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("Nenhuma empresa cadastrada (além das fixas: BRASANITAS, GRSA, C.C).")
        
        st.markdown("---")
        
        # SEÇÃO DE EXCLUSÃO (mantida exatamente igual)
        st.markdown("### 🗑️ Exclusão de Registros")
        st.markdown("#### Selecione os registros que deseja excluir:")
        
        for idx, row in df.iterrows():
            col_check, col_data = st.columns([0.5, 9.5])
            with col_check:
                is_checked = st.checkbox("", key=f"chk_{row['id']}", value=row['id'] in st.session_state.selected_ids)
                if is_checked and row['id'] not in st.session_state.selected_ids:
                    st.session_state.selected_ids.append(row['id'])
                elif not is_checked and row['id'] in st.session_state.selected_ids:
                    st.session_state.selected_ids.remove(row['id'])
            with col_data:
                st.markdown(f"""
                <div style="background: rgba(0,20,40,0.4); border-radius: 8px; padding: 5px 10px; margin-bottom: 5px;">
                    <b>ID {row['id']}</b> - {row['nome']} | CPF: {row['cpf']} | Empresa: {row.get('empresa','N/A')} | 
                    Entrada: {row['data_entrada']} | Saída: {row['data_saida'] if row['data_saida'] else 'Ainda presente'}
                </div>
                """, unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🗑️ Excluir Selecionados", use_container_width=True):
                if st.session_state.selected_ids:
                    st.session_state.pending_delete_ids = st.session_state.selected_ids.copy()
                    st.rerun()
                else:
                    st.warning("Nenhum registro selecionado.")
        with col_btn2:
            if st.button("📋 Limpar Seleção", use_container_width=True):
                st.session_state.selected_ids = []
                st.session_state.pending_delete_ids = []
                st.session_state.pending_clear_all = False
                st.rerun()
        with col_btn3:
            if st.button("⚠️ LIMPAR TODO O HISTÓRICO", use_container_width=True):
                st.session_state.pending_clear_all = True
                st.rerun()
        
        if st.session_state.pending_delete_ids:
            st.markdown("---")
            st.error(f"⚠️ **Confirmação necessária:** você está prestes a excluir {len(st.session_state.pending_delete_ids)} registro(s).")
            st.write("IDs:", ", ".join(map(str, st.session_state.pending_delete_ids)))
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("✅ SIM, EXCLUIR PERMANENTEMENTE", key="confirm_delete"):
                    try:
                        for id_excluir in st.session_state.pending_delete_ids:
                            supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
                        st.success(f"{len(st.session_state.pending_delete_ids)} registro(s) excluído(s)!")
                        st.session_state.selected_ids = []
                        st.session_state.pending_delete_ids = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
                        st.session_state.pending_delete_ids = []
            with col_cancel:
                if st.button("❌ Cancelar", key="cancel_delete"):
                    st.session_state.pending_delete_ids = []
                    st.rerun()
        
        if st.session_state.pending_clear_all:
            st.markdown("---")
            st.error("🚨 **ATENÇÃO – LIMPEZA TOTAL DO HISTÓRICO**")
            st.write("Esta ação apagará **TODOS** os registros da tabela de movimentação. É irreversível!")
            total_registros = len(df)
            st.write(f"Total de registros atuais: **{total_registros}**")
            confirm = st.text_input("Digite 'LIMPAR TUDO' para confirmar:", type="password")
            col_clear_confirm, col_clear_cancel = st.columns(2)
            with col_clear_confirm:
                if st.button("🔥 EXCLUIR TUDO PERMANENTEMENTE", key="confirm_clear_all"):
                    if confirm == "LIMPAR TUDO":
                        try:
                            supabase.table("movimentacao").delete().neq("id", 0).execute()
                            st.success("✅ Todo o histórico foi limpo!")
                            st.session_state.selected_ids = []
                            st.session_state.pending_delete_ids = []
                            st.session_state.pending_clear_all = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao limpar histórico: {e}")
                    else:
                        st.error("Confirmação incorreta. Digite exatamente 'LIMPAR TUDO'")
            with col_clear_cancel:
                if st.button("Cancelar", key="cancel_clear_all"):
                    st.session_state.pending_clear_all = False
                    st.rerun()
    else:
        st.info("📭 Nenhum registro encontrado no histórico.")

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
                        <div style="background:rgba(0,212,255,0.1); border-radius:12px; padding:12px; border-left:3px solid #0ff;">
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
                            try:
                                supabase.table("Pessoas").delete().eq("cpf", pessoa['cpf']).execute()
                                st.success("Cadastro excluído!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                else:
                    st.info("Marque a confirmação para habilitar a exclusão")
        else:
            st.info("Nenhum cadastro encontrado")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
    <div class="footer">
        🔮 ACCESS GATE - Segurança e Tecnologia Futurista<br>
        Monitoramento 24/7 - Sistema com Inteligência Artificial
    </div>
""", unsafe_allow_html=True)
