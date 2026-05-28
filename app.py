import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image
import base64
import re
import uuid

# --- CONFIGURAÇÃO DE SEGURANÇA ---
MAX_TENTATIVAS_LOGIN = 5
SESSION_TIMEOUT_MINUTOS = 5

# --- CONFIGURAÇÃO SUPABASE ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(
    page_title="JOHN ACESSOS - ACESSO DE DADOS",
    layout="wide",
    page_icon="👮‍♂️",
    initial_sidebar_state="expanded"
)

# ====================== FUNÇÕES DE GERENCIAMENTO DE SESSÃO ======================
def registrar_sessao(perfil, usuario="admin"):
    session_id = str(uuid.uuid4())
    try:
        data = {
            "id": session_id,
            "usuario": usuario,
            "perfil": perfil,
            "ultima_atividade": datetime.now().isoformat(),
            "ip": "desconhecido",
            "user_agent": "streamlit"
        }
        supabase.table("sessoes_ativas").insert(data).execute()
        st.session_state.session_id = session_id
        return True
    except Exception as e:
        print(f"Erro ao registrar sessão: {e}")
        return False

def atualizar_atividade_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").update({
                "ultima_atividade": datetime.now().isoformat()
            }).eq("id", st.session_state.session_id).execute()
        except Exception as e:
            print(f"Erro ao atualizar sessão: {e}")

def remover_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").delete().eq("id", st.session_state.session_id).execute()
        except:
            pass
        st.session_state.session_id = None

def contar_sessoes_ativas():
    limite = (datetime.now() - pd.Timedelta(minutes=SESSION_TIMEOUT_MINUTOS)).isoformat()
    try:
        result = supabase.table("sessoes_ativas").select("id", count="exact").gte("ultima_atividade", limite).execute()
        return result.count
    except Exception as e:
        print(f"Erro ao contar sessões: {e}")
        return 0

def limpar_sessoes_expiradas():
    limite = (datetime.now() - pd.Timedelta(minutes=SESSION_TIMEOUT_MINUTOS)).isoformat()
    try:
        if "session_id" in st.session_state and st.session_state.session_id:
            supabase.table("sessoes_ativas").delete().lt("ultima_atividade", limite).neq("id", st.session_state.session_id).execute()
        else:
            supabase.table("sessoes_ativas").delete().lt("ultima_atividade", limite).execute()
    except Exception as e:
        print(f"Erro ao limpar sessões: {e}")

def encerrar_outras_sessoes():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").delete().neq("id", st.session_state.session_id).execute()
            return True
        except Exception as e:
            print(f"Erro ao encerrar outras sessões: {e}")
            return False
    return False

# ====================== FUNÇÃO PARA GERAR HTML PARA IMPRESSÃO/PDF ======================
def gerar_html_impressao(df, titulo):
    if df.empty:
        return None
    colunas = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida']
    colunas_presentes = [c for c in colunas if c in df.columns]
    linhas_html = ""
    for _, row in df.iterrows():
        linhas_html += "<tr>"
        for col in colunas_presentes:
            valor = str(row[col]) if pd.notna(row[col]) else ''
            valor = valor.replace('<', '&lt;').replace('>', '&gt;')
            linhas_html += f"70><td{valor}迟"
        linhas_html += "<tr>"
    cabecalho_html = "".join([f"<th>{col.upper()}</th>" for col in colunas_presentes])
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
                margin: 2cm;
                background: white;
            }}
            h1 {{
                text-align: center;
                color: #0a2b3e;
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
                background: #0a2b3e;
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
        <h1>JOHN ACESSOS - ACESSO DE DADOS - {titulo}</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        <table>
            <thead>
                <td>{cabecalho_html}</tr>
            </thead>
            <tbody>
                {linhas_html}
            </tbody>
        </table>
        <div class="no-print" style="text-align:center; margin-top:30px;">
            <button onclick="window.print();" style="padding:10px 20px; font-size:16px;">🖨️ Imprimir / Salvar como PDF</button>
        </div>
    </body>
    </html>
    """
    return html

# ====================== FUNÇÕES DE VALIDAÇÃO ======================
def validar_cpf(cpf):
    cpf_limpo = re.sub(r'\D', '', cpf)
    return cpf_limpo.isdigit() and len(cpf_limpo) == 11

def sanitizar_cpf(cpf):
    return re.sub(r'\D', '', cpf)

def sanitizar_texto(texto):
    if not texto:
        return texto
    texto = texto.replace('<', '&lt;').replace('>', '&gt;')
    texto = texto.replace('"', '&quot;').replace("'", '&#39;')
    return texto

# ====================== CARREGAR IMAGENS ======================
def carregar_imagem(nome_arquivo, nome_descricao):
    try:
        return Image.open(nome_arquivo)
    except:
        return None

IMAGEM_LOGIN = carregar_imagem("login_image.png", "Login")
IMAGEM_SIDEBAR = carregar_imagem("sidebar_logo.png", "Sidebar")
IMAGEM_HEADER = carregar_imagem("header_logo.png", "Header")

# ====================== CABEÇALHOS DE SEGURANÇA ======================
st.markdown("""
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';">
<meta http-equiv="X-Frame-Options" content="DENY">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
""", unsafe_allow_html=True)

# ====================== DESIGN BASE (CSS) ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono&display=swap');

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(100, 0, 255, 0.4); }
    70% { box-shadow: 0 0 0 12px rgba(100, 0, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(100, 0, 255, 0); }
}
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-6px); }
    100% { transform: translateY(0px); }
}
@keyframes spinSlow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.stApp {
    background: radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);
    font-family: 'Inter', 'Space Mono', monospace;
}

[data-testid="stSidebar"] {
    background: rgba(8, 8, 20, 0.85);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(100, 0, 255, 0.3);
}
.sidebar-header {
    text-align: center;
    padding: 25px 10px;
    border-bottom: 1px solid rgba(100, 0, 255, 0.5);
}
.sidebar-title {
    font-size: 22px;
    font-weight: 800;
    background: linear-gradient(135deg, #a855f7, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.info-item {
    margin-bottom: 12px;
    color: #c4b5fd;
    font-size: 12px;
    display: flex;
    gap: 8px;
    font-family: 'Space Mono', monospace;
}

.admin-header {
    background: rgba(8, 8, 20, 0.7);
    backdrop-filter: blur(8px);
    border-radius: 16px;
    padding: 12px 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(168, 85, 247, 0.4);
}
.badge-admin {
    background: linear-gradient(135deg, #a855f7, #3b82f6);
    padding: 4px 15px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 11px;
    color: white;
}
.session-indicator {
    background: rgba(0,0,0,0.6);
    border-radius: 30px;
    padding: 4px 12px;
    font-size: 12px;
    font-family: 'Space Mono', monospace;
    color: #a78bfa;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}
.warning-triangle {
    color: #ffaa00;
    font-size: 14px;
    filter: drop-shadow(0 0 2px #ffaa00);
}

.admin-card {
    background: rgba(15, 15, 30, 0.6);
    backdrop-filter: blur(4px);
    border-radius: 20px;
    padding: 18px;
    border: 1px solid rgba(168, 85, 247, 0.2);
    transition: 0.2s;
}
.admin-card:hover {
    transform: translateY(-3px);
    border-color: #a855f7;
    box-shadow: 0 5px 20px rgba(168, 85, 247, 0.15);
}
.card-title {
    font-size: 10px;
    letter-spacing: 2px;
    color: #a78bfa;
}
.card-value {
    font-size: 32px;
    font-weight: 800;
    background: linear-gradient(135deg, #fff, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stButton > button, .stForm button {
    border-radius: 40px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    background: linear-gradient(90deg, #a855f7, #3b82f6);
    color: white;
    border: none;
    transition: 0.2s;
}
.stButton > button:hover, .stForm button:hover {
    transform: scale(1.01);
    box-shadow: 0 0 12px #a855f7;
}
.stButton > button[key="sair_final"], .stButton > button[key="btn_atualizar"] {
    background: linear-gradient(90deg, #a855f7, #3b82f6);
}
.stButton > button[key="sair_final"]:hover, .stButton > button[key="btn_atualizar"]:hover {
    transform: scale(1.01);
    box-shadow: 0 0 12px #a855f7;
}

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: rgba(0, 0, 0, 0.6);
    border: 1px solid #a855f7;
    border-radius: 12px;
    color: #c4b5fd;
    font-family: 'Space Mono', monospace;
    padding: 8px;
}
.stTextInput > div > div > input:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 8px #a855f7;
}

.streamlit-expanderHeader {
    background: rgba(15, 15, 30, 0.8);
    border: 1px solid #a855f7;
    border-radius: 14px;
    color: #c4b5fd;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: rgba(0,0,0,0.3);
    padding: 5px;
    border-radius: 30px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 25px;
    padding: 5px 20px;
    font-weight: 500;
    color: #ccc;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #a855f7, #3b82f6);
    color: white;
}
.stCheckbox label {
    color: #c4b5fd;
}
.stDataFrame {
    background: rgba(0,0,0,0.3);
    border-radius: 12px;
    border: 1px solid #a855f7;
}
.footer {
    text-align: center;
    padding: 15px;
    color: #6b7280;
    font-size: 9px;
    border-top: 1px solid rgba(168,85,247,0.2);
    margin-top: 25px;
}
h1, h2, h3 {
    font-family: 'Inter', sans-serif;
    color: #e9d5ff;
}
hr {
    border-color: rgba(168,85,247,0.2);
}
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
if IMAGEM_SIDEBAR:
    st.sidebar.image(IMAGEM_SIDEBAR, use_container_width=True)
else:
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">👮‍♂️ JOHN ACESSOS</div>
            <p style="color:#a78bfa; font-size:9px;">ACESSO DE DADOS</p>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ ESTADO")
st.sidebar.markdown('<div class="info-item">🟢 REDE NEURAL: ATIVA</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🤖 MODELO: DEEP LEARNING</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🔒 CRIPTOGRAFIA: QUÂNTICA</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🗄️ DATA LAKE: SEGURO</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 INFO")
if "perfil" in st.session_state:
    st.sidebar.markdown(f"<div class='info-item'>👑 Perfil: {st.session_state.perfil}</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div class='info-item'>👑 Perfil: ---</div>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🟢 Status: Online</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">📦 Versão: 12.5 (SECURE)</div>', unsafe_allow_html=True)

# ====================== FUNÇÃO "MANAGE APP" (SOMENTE ADMIN) ======================
if st.session_state.perfil == "ADMIN":
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ MANAGE APP", expanded=False):
        st.markdown("### 🔧 Ferramentas Administrativas")
        total_ativas = contar_sessoes_ativas()
        st.metric("👥 Sessões ativas", total_ativas)
        if st.button("🔒 Encerrar outras sessões", use_container_width=True):
            if encerrar_outras_sessoes():
                st.success("✅ Todas as outras sessões foram encerradas!")
                st.rerun()
            else:
                st.error("❌ Erro ao encerrar outras sessões.")
        if st.button("🧹 Limpar sessões expiradas", use_container_width=True):
            limpar_sessoes_expiradas()
            st.success("✅ Sessões expiradas removidas!")
            st.rerun()
        st.markdown("---")
        st.caption("Ações disponíveis apenas para o administrador.")

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
if "tentativas_login" not in st.session_state:
    st.session_state.tentativas_login = 0
if "bloqueado_ate" not in st.session_state:
    st.session_state.bloqueado_ate = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# ====================== TELA DE LOGIN (sem elementos extras) ======================
if not st.session_state.logado:
    if st.session_state.bloqueado_ate and datetime.now() < st.session_state.bloqueado_ate:
        st.error(f"⛔ Muitas tentativas inválidas. Tente novamente após {st.session_state.bloqueado_ate.strftime('%H:%M:%S')}")
        st.stop()

    st.markdown("""
    <style>
    .data-stream {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        background: repeating-linear-gradient(90deg, rgba(168,85,247,0.05) 0px, rgba(168,85,247,0.05) 2px, transparent 2px, transparent 10px);
        background-size: 20px 100%;
    }
    .neural-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: radial-gradient(circle at 20% 30%, rgba(168,85,247,0.08) 2px, transparent 2px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
        position: relative;
        z-index: 2;
    }
    .login-box {
        background: rgba(8, 8, 20, 0.7);
        backdrop-filter: blur(20px);
        border-radius: 50px;
        padding: 45px 35px;
        border: 1px solid rgba(168,85,247,0.6);
        width: 100%;
        max-width: 480px;
        text-align: center;
        animation: float 3s ease-in-out infinite;
        box-shadow: 0 0 30px rgba(168,85,247,0.2);
    }
    .guard-logo {
        width: 110px;
        height: 110px;
        margin: 0 auto 20px;
        background: radial-gradient(circle, rgba(168,85,247,0.3), rgba(59,130,246,0.1));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        animation: pulse 2s infinite;
    }
    .guard-logo span {
        font-size: 60px;
        filter: drop-shadow(0 0 10px #a855f7);
    }
    .guard-logo::before {
        content: "";
        position: absolute;
        width: 140px;
        height: 140px;
        border: 2px solid #a855f7;
        border-radius: 50%;
        animation: spinSlow 8s linear infinite;
        opacity: 0.6;
    }
    .guard-logo::after {
        content: "⚡";
        position: absolute;
        font-size: 20px;
        top: -15px;
        right: -15px;
        color: #a855f7;
        animation: pulse 1s infinite;
    }
    .logo-title {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }
    .logo-subtitle {
        font-size: 11px;
        color: #a78bfa;
        letter-spacing: 3px;
        margin-bottom: 25px;
    }
    .data-field input {
        width: 100%;
        background: rgba(0, 0, 0, 0.6);
        border: 1px solid #a855f7;
        border-radius: 40px;
        padding: 12px 20px;
        color: #c4b5fd;
        font-family: 'Space Mono', monospace;
        transition: 0.2s;
    }
    .data-field input:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 12px #a855f7;
    }
    .status-bar-data {
        margin-top: 25px;
        font-size: 9px;
        color: #a78bfa;
        border-top: 1px solid rgba(168,85,247,0.3);
        padding-top: 12px;
        display: flex;
        justify-content: center;
        gap: 15px;
    }
    .status-item-data {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .blink-data {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #a855f7;
        border-radius: 50%;
        animation: pulse 1s infinite;
    }
    .binary-stream {
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        letter-spacing: 2px;
        background: rgba(0,0,0,0.5);
        padding: 6px;
        border-radius: 20px;
        margin-bottom: 15px;
        display: inline-block;
        width: auto;
        color: #a855f7;
    }
    </style>
    <div class="data-stream"></div>
    <div class="neural-bg"></div>
    <div class="login-container">
        <div class="login-box">
            <div class="guard-logo"><span>👮‍♂️🔒</span></div>
            <div class="logo-title">JOHN ACESSOS</div>
            <div class="logo-subtitle">ACESSO DE DADOS</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div id="binary-container" style="text-align:center; margin-bottom:15px;"></div>
    <script>
        function generateBinary(len=50) {
            let bin = '';
            for(let i=0;i<len;i++) bin += Math.random()<0.5?'0':'1';
            return bin;
        }
        function updateBinary() {
            const el = document.getElementById('binary-container');
            if(el) el.innerHTML = `<div class="binary-stream">${generateBinary(60)}</div>`;
        }
        setInterval(updateBinary, 400);
        updateBinary();
    </script>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        st.text_input("", placeholder="Identificação (usuário)", key="data_user", label_visibility="collapsed")
        senha = st.text_input("", type="password", placeholder="Chave de acesso criptografada", label_visibility="collapsed")
        submitted = st.form_submit_button("👮‍♂️ ACESSAR SISTEMA", use_container_width=True)
        if submitted:
            if senha == "fgxv4VP0/*":
                st.session_state.logado = True
                st.session_state.perfil = "ADMIN"
                st.session_state.tentativas_login = 0
                registrar_sessao("ADMIN", "admin")
                st.rerun()
            elif senha == "JOHN123":
                st.session_state.logado = True
                st.session_state.perfil = "VIGILANTE"
                st.session_state.tentativas_login = 0
                registrar_sessao("VIGILANTE", "vigilante")
                st.rerun()
            else:
                st.session_state.tentativas_login += 1
                restantes = MAX_TENTATIVAS_LOGIN - st.session_state.tentativas_login
                if st.session_state.tentativas_login >= MAX_TENTATIVAS_LOGIN:
                    st.session_state.bloqueado_ate = datetime.now() + pd.Timedelta(minutes=5)
                    st.error("⛔ Muitas tentativas inválidas. Acesso bloqueado por 5 minutos.")
                else:
                    st.error(f"❌ ACESSO NEGADO - Assinatura inválida. Tentativas restantes: {restantes}")

    st.markdown("""
            <div class="status-bar-data">
                <div class="status-item-data"><span class="blink-data"></span> FIREWALL ATIVO</div>
                <div class="status-item-data"><span class="blink-data"></span> CRIPTOGRAFIA QUÂNTICA</div>
                <div class="status-item-data"><span class="blink-data"></span> PROTEÇÃO DE DADOS</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ====================== APÓS LOGIN ======================
if st.session_state.session_id:
    atualizar_atividade_sessao()
    limpar_sessoes_expiradas()
    total_conectados = contar_sessoes_ativas()
else:
    total_conectados = 0

alerta_monitoramento = total_conectados > 1

if alerta_monitoramento:
    indicador_html = f'<div class="session-indicator"><span class="warning-triangle">⚠️</span> <span>👥 {total_conectados}</span></div>'
else:
    indicador_html = f'<div class="session-indicator"><span>👥 {total_conectados}</span></div>'

st.markdown(f"""
    <div class="admin-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #a855f7, #3b82f6); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 20px;">👮‍♂️</span>
                </div>
                <div>
                    <h1 style="margin:0; font-size: 16px;">JOHN ACESSOS - ACESSO DE DADOS</h1>
                    <p style="margin:0; color: #a78bfa; font-size: 8px;">SEGURANÇA E PROTEÇÃO</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 15px;">
                {indicador_html}
                <div class="badge-admin">👑 {st.session_state.perfil}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Botões: Atualizar e Sair
col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
with col3:
    if st.button("🔄 ATUALIZAR", key="btn_atualizar", use_container_width=True):
        st.rerun()
with col4:
    if st.button("🚪 SAIR", key="sair_final", use_container_width=True):
        remover_sessao()
        st.session_state.logado = False
        st.rerun()

# ====================== DASHBOARD, CADASTRO, ETC. (MANTIDOS) ======================
# ... (todo o resto do código – dashboard, cadastro, registro, pessoas presentes, histórico, gestão) ...
# Para não estender demais, mantenha exatamente as mesmas funções que você já tinha.
# Assegure-se de que o elemento a seguir é a ÚNICA adição no final.

# ====================== ELEMENTO DE CANTO (SOMENTE ADMIN) ======================
if st.session_state.perfil == "ADMIN":
    st.markdown("""
        <div style="position: fixed; bottom: 10px; right: 10px; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); padding: 5px 12px; border-radius: 20px; font-size: 10px; color: #a78bfa; font-family: monospace; z-index: 1000; border: 1px solid #a855f7;">
            📁 main | johndosanjos162/sistema-portaria/app.py<br>
            📡 [ UTC ] Logs for sistema-portaria-pw4omefsgftcngw4dyenqk.streamlit.app
        </div>
    """, unsafe_allow_html=True)
