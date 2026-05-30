import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image
import base64
import re
import uuid
import json

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

# ====================== FUNÇÕES DE CONFIGURAÇÃO DE TEMA (BACKGROUND) ======================
def get_background_config():
    """Retorna a configuração atual do background (dict). Se não existir, cria padrão."""
    try:
        result = supabase.table("app_config").select("value").eq("key", "background_config").execute()
        if result.data:
            return json.loads(result.data[0]['value'])
    except Exception as e:
        print(f"Erro ao ler config: {e}")
    # Configuração padrão (gradiente original)
    return {
        "type": "gradient",
        "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)",
        "apply_to_login": False
    }

def save_background_config(config):
    """Salva a configuração do background no Supabase."""
    try:
        # Tenta atualizar se existe
        supabase.table("app_config").update({
            "value": json.dumps(config),
            "updated_at": datetime.now().isoformat()
        }).eq("key", "background_config").execute()
    except:
        # Se não existe, insere
        try:
            supabase.table("app_config").insert({
                "key": "background_config",
                "value": json.dumps(config),
                "updated_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            st.error(f"Erro ao salvar configuração de tema: {e}")
            print(f"Erro ao salvar config: {e}")
    st.session_state.background_config = config

def image_to_base64(file):
    """Converte imagem para base64 data URL."""
    bytes_data = file.getvalue()
    content_type = file.type
    base64_str = base64.b64encode(bytes_data).decode('utf-8')
    return f"data:{content_type};base64,{base64_str}"

# Carregar configuração no session_state (se ainda não)
if "background_config" not in st.session_state:
    st.session_state.background_config = get_background_config()

# ====================== FUNÇÕES PARA GERAR HTML E PDF ======================
def gerar_html_impressao(df, titulo):
    if df.empty:
        return None

    colunas_desejadas = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida']
    colunas_existentes = [col for col in colunas_desejadas if col in df.columns]
    df_relatorio = df[colunas_existentes].copy()
    df_relatorio = df_relatorio.fillna('')
    tabela_html = df_relatorio.to_html(escape=True, index=False, classes='dataframe')

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
        {tabela_html}
        <div class="no-print" style="text-align:center; margin-top:30px;">
            <button onclick="window.print();" style="padding:10px 20px; font-size:16px;">🖨️ Imprimir / Salvar como PDF</button>
        </div>
    </body>
    </html>
    """
    return html

def gerar_secao_html(df, titulo_secao):
    if df.empty:
        return f"""
        <div class="section">
            <h2>{titulo_secao}</h2>
            <p>Nenhum registro encontrado.</p>
        </div>
        """
    colunas = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida']
    colunas_existentes = [c for c in colunas if c in df.columns]
    df_secao = df[colunas_existentes].fillna('')
    tabela_html = df_secao.to_html(escape=True, index=False, classes='dataframe')
    return f"""
    <div class="section">
        <h2>{titulo_secao} <span class="count-badge">{len(df)} registros</span></h2>
        {tabela_html}
    </div>
    """

def gerar_html_consolidado(df):
    if df.empty:
        return None

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>RELATÓRIO CONSOLIDADO - TODOS OS SETORES</title>
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
            .section {{
                margin-top: 40px;
                page-break-inside: avoid;
            }}
            .section h2 {{
                background: #0a2b3e;
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                font-size: 18px;
                margin-bottom: 15px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 10px;
                margin-bottom: 20px;
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
            .count-badge {{
                display: inline-block;
                background: #a855f7;
                color: white;
                border-radius: 20px;
                padding: 2px 10px;
                font-size: 12px;
                margin-left: 10px;
            }}
            @media print {{
                body {{
                    margin: 1cm;
                }}
                .no-print {{
                    display: none;
                }}
                .section {{
                    page-break-inside: avoid;
                }}
            }}
        </style>
    </head>
    <body>
        <h1>JOHN ACESSOS - RELATÓRIO CONSOLIDADO</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
    """

    df_grsa = df[df['setor_destino'].str.contains('GRSA', case=False, na=False)]
    html += gerar_secao_html(df_grsa, "🔧 GRSA")

    df_bras = df[df['setor_destino'].str.contains('Brasanitas', case=False, na=False)]
    html += gerar_secao_html(df_bras, "🏭 Brasanitas")

    df_cc = df[df['setor_destino'].str.contains('C.C', case=False, na=False)]
    html += gerar_secao_html(df_cc, "🏥 C.C")

    empresas_excluir = ["BRASANITAS", "GRSA", "C.C"]
    todas_empresas = df['empresa'].dropna().unique()
    empresas_prestadores = [emp for emp in todas_empresas if emp.upper() not in [e.upper() for e in empresas_excluir]]
    if empresas_prestadores:
        df_prestadores = df[df['empresa'].isin(empresas_prestadores)]
        html += gerar_secao_html(df_prestadores, "🏢 Prestadores de Serviços (Demais Empresas)")
    else:
        html += f"""
        <div class="section">
            <h2>🏢 Prestadores de Serviços</h2>
            <p>Nenhum registro para esta categoria.</p>
        </div>
        """

    html += """
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

# ====================== CSS DINÂMICO PARA BACKGROUND ======================
def apply_background_css(config=None):
    if config is None:
        config = st.session_state.get("background_config", get_background_config())
    bg_style = config.get("value", "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)")
    css = f"""
    <style>
    .stApp {{
        background: {bg_style};
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ====================== CABEÇALHOS DE SEGURANÇA ======================
st.markdown("""
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';">
<meta http-equiv="X-Frame-Options" content="DENY">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
""", unsafe_allow_html=True)

# ====================== DESIGN BASE (CSS) - EXCETO BACKGROUND (que será dinâmico) ======================
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
@keyframes scan {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes glowPulse {
    0% { box-shadow: 0 0 5px #a855f7; }
    50% { box-shadow: 0 0 20px #a855f7; }
    100% { box-shadow: 0 0 5px #a855f7; }
}
@keyframes buttonGlow {
    0% { box-shadow: 0 0 5px #0ff; }
    50% { box-shadow: 0 0 20px #0ff; }
    100% { box-shadow: 0 0 5px #0ff; }
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
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    z-index: 1;
}
.stButton > button::before, .stForm button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.5s ease;
    z-index: -1;
}
.stButton > button:hover::before, .stForm button:hover::before {
    left: 100%;
}
.stButton > button:hover, .stForm button:hover {
    transform: scale(1.02);
    box-shadow: 0 0 20px #a855f7;
    animation: buttonGlow 0.8s infinite alternate;
}
.stButton > button[key="btn_atualizar"] {
    background: linear-gradient(90deg, #0ff, #0080ff);
}
.stButton > button[key="sair_final"] {
    background: linear-gradient(90deg, #f44, #a00);
}
.stButton > button[key="confirma_cpf"] {
    background: linear-gradient(90deg, #f0f, #a0f);
}
.stButton > button[key="btn_entrada"] {
    background: linear-gradient(90deg, #0f0, #0a0);
}
.stButton > button[key="salvar_cadastro"] {
    background: linear-gradient(90deg, #ffa500, #ff6600);
}
.stButton > button[key="del_cad"], .stButton > button[key="del_reg"], .stButton > button[key="confirm_delete"] {
    background: linear-gradient(90deg, #ff3333, #990000);
}
.stButton > button[key="clear_all_confirm"] {
    background: linear-gradient(90deg, #ff0000, #660000);
}
.stButton > button[key="cancel_delete"], .stButton > button[key="cancel_clear_all"] {
    background: linear-gradient(90deg, #666, #333);
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(0, 0, 0, 0.8);
    border: 1px solid #a855f7;
    border-radius: 12px;
    color: #0ff !important;
    font-family: 'Space Mono', monospace;
    padding: 8px;
}
.stSelectbox > div > div {
    background: rgba(0, 0, 0, 0.8) !important;
    border: 1px solid #a855f7 !important;
    border-radius: 12px !important;
    color: #0ff !important;
    font-family: 'Space Mono', monospace;
}
.stSelectbox [data-baseweb="select"] span {
    color: #0ff !important;
}
div[data-baseweb="select"] ul {
    background-color: #0a0a1a !important;
    border: 1px solid #a855f7 !important;
}
div[data-baseweb="select"] li {
    color: #0ff !important;
    background-color: #0a0a1a !important;
}
div[data-baseweb="select"] li:hover {
    background-color: #a855f7 !important;
    color: black !important;
}
.stSelectbox label {
    color: #0ff !important;
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
if st.session_state.get("perfil"):
    st.sidebar.markdown(f"<div class='info-item'>👑 Perfil: {st.session_state.perfil}</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div class='info-item'>👑 Perfil: ---</div>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🟢 Status: Online</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">📦 Versão: 13.1 (TECH)</div>', unsafe_allow_html=True)

# ====================== FUNÇÃO "MANAGE APP" (SOMENTE ADMIN) ======================
if st.session_state.get("perfil") == "ADMIN" and st.session_state.get("logado"):
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

    # Ícone de configurações de tema (engrenagem) - agora fora do expander para fácil acesso
    st.sidebar.markdown("---")
    if st.sidebar.button("⚙️ Configurar Tema (Background)", use_container_width=True):
        # Abrir popover para configurações
        with st.popover("🎨 Configurações de Fundo", use_container_width=True):
            config_atual = st.session_state.background_config.copy()
            tipo_opcoes = ["Gradiente (padrão)", "Cor sólida", "Imagem via URL", "Imagem do computador"]
            tipo_map = {"gradient": 0, "solid": 1, "url": 2, "upload": 3}
            idx_atual = tipo_map.get(config_atual.get('type', 'gradient'), 0)
            tipo = st.selectbox("Tipo de fundo:", tipo_opcoes, index=idx_atual)
            
            novo_valor = config_atual.get('value', '')
            novo_tipo = config_atual.get('type', 'gradient')
            
            if tipo == "Gradiente (padrão)":
                novo_valor = "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
                novo_tipo = "gradient"
            elif tipo == "Cor sólida":
                cor = st.color_picker("Escolha uma cor", value=config_atual.get('value', '#0a0a1a') if config_atual['type']=='solid' else '#0a0a1a')
                novo_valor = cor
                novo_tipo = "solid"
            elif tipo == "Imagem via URL":
                url_img = st.text_input("URL da imagem (ex: https://exemplo.com/fundo.jpg)", value=config_atual.get('value', '') if config_atual['type']=='url' else '')
                if url_img:
                    novo_valor = f"url('{url_img}') center/cover no-repeat fixed"
                else:
                    novo_valor = config_atual.get('value', 'radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)')
                novo_tipo = "url"
            else:  # Imagem do computador
                uploaded_file = st.file_uploader("Escolha uma imagem (PNG, JPG, JPEG, GIF)", type=['png', 'jpg', 'jpeg', 'gif'])
                if uploaded_file is not None:
                    try:
                        data_url = image_to_base64(uploaded_file)
                        novo_valor = f"url('{data_url}') center/cover no-repeat fixed"
                        novo_tipo = "url"
                        st.success("Imagem carregada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao processar imagem: {e}")
                        novo_valor = config_atual.get('value', 'radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)')
                        novo_tipo = config_atual.get('type', 'gradient')
                else:
                    # Nenhuma nova imagem, manter a anterior se for do tipo upload/url
                    if config_atual['type'] == 'url' and 'data:image' in config_atual.get('value', ''):
                        novo_valor = config_atual.get('value')
                        novo_tipo = 'url'
                    else:
                        novo_valor = config_atual.get('value', 'radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)')
                        novo_tipo = config_atual.get('type', 'gradient')
            
            aplicar_login = st.checkbox("Aplicar também na tela de login", value=config_atual.get('apply_to_login', False))
            
            if st.button("💾 Salvar configuração", key="save_theme"):
                if not novo_valor:
                    st.error("Configuração inválida. Preencha corretamente.")
                else:
                    nova_config = {
                        "type": novo_tipo,
                        "value": novo_valor,
                        "apply_to_login": aplicar_login
                    }
                    save_background_config(nova_config)
                    st.success("✅ Configuração salva! Recarregando para aplicar...")
                    st.rerun()

# ====================== SESSÃO (INICIALIZAÇÃO) ======================
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
if "pessoa_confirmada" not in st.session_state:
    st.session_state.pessoa_confirmada = None
if "pessoa_saida" not in st.session_state:
    st.session_state.pessoa_saida = None

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    # Aplica background na tela de login se a configuração permitir
    if st.session_state.background_config.get("apply_to_login", False):
        apply_background_css(st.session_state.background_config)
    else:
        # Fundo padrão
        st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);
        }
        </style>
        """, unsafe_allow_html=True)

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
# Aplica o background configurado para o app (após login)
apply_background_css(st.session_state.background_config)

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

# ====================== DASHBOARD ======================
st.markdown("---")
pessoas_presentes = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
total_presentes = len(pessoas_presentes)
total_colaboradores = len(supabase.table("Pessoas").select("*").execute().data)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">📍 PRESENTES</div><div class="card-value">{total_presentes}</div></div>
                <div style="font-size:22px;">👥</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">📋 CADASTRADOS</div><div class="card-value">{total_colaboradores}</div></div>
                <div style="font-size:22px;">📊</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">🏥 SETORES</div><div class="card-value">11</div></div>
                <div style="font-size:22px;">🏛️</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">🎥 CFTV</div><div class="card-value">24/7</div></div>
                <div style="font-size:22px;">📹</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ====================== CADASTRO (COM VALIDAÇÃO DE CPF DUPLICADO) ======================
st.markdown("---")
st.markdown("### ✚ Cadastro de Nova Pessoa")
with st.expander("📋 Formulário de Cadastro", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("📄 CPF *", placeholder="000.000.000-00")
    novo_nome = col_b.text_input("👤 Nome Completo *")
    novo_empresa = col_c.text_input("🏢 Empresa")
    if st.button("💾 Salvar Cadastro", key="salvar_cadastro", type="primary"):
        if novo_cpf and novo_nome:
            if not validar_cpf(novo_cpf):
                st.error("❌ CPF inválido. Digite um CPF válido (11 dígitos).")
            else:
                cpf_limpo = sanitizar_cpf(novo_cpf)
                # Verificar se CPF já existe
                existe = supabase.table("Pessoas").select("id, empresa").eq("cpf", cpf_limpo).execute().data
                if existe:
                    empresa_existente = existe[0].get('empresa', 'N/A')
                    st.error(f"❌ Pessoa já cadastrada com este CPF (Empresa atual: {empresa_existente}). Utilize a gestão de cadastros para editar ou excluir.")
                else:
                    nome_limpo = sanitizar_texto(novo_nome).strip().upper()
                    empresa_limpa = sanitizar_texto(novo_empresa).strip().upper() if novo_empresa else ""
                    try:
                        supabase.table("Pessoas").insert({
                            "cpf": cpf_limpo,
                            "nome": nome_limpo,
                            "empresa": empresa_limpa
                        }).execute()
                        st.success("✅ Cadastro salvo com sucesso!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {e}")
        else:
            st.error("❌ CPF e Nome são obrigatórios.")

# ====================== REGISTRO DE ENTRADA ======================
st.markdown("---")
st.markdown("### 📋 Registrar Movimentação")

tipo = st.radio("👥 Tipo de Pessoa:", ["🏢 Prestador de serviços", "🔧 Terceirizados / Instrumentadores"], horizontal=True)

if tipo == "🏢 Prestador de serviços":
    destinos = [
        "🏥 C.C", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia",
        "🔧 Manutenção", "🧪 Laboratório", "💊 Farmacia", "🏥 P.A",
        "👶 PEDIATRIA P.A", "🔧 ENG.CLINICA", "🧹 HORTELARIA", "📦 OPME 6°AND",
        "📦 OPME 9°AND", "🔒 SSGA", "🏥 CDU", "⚕️ ONCOLOGIA"
    ]
else:
    destinos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

col_cpf, col_btn_confirma = st.columns([3, 1])
with col_cpf:
    cpf_input = st.text_input("📄 CPF:", key="cpf_entrada", placeholder="Digite o CPF")
with col_btn_confirma:
    if cpf_input and len(cpf_input.strip()) > 0:
        if st.button("✅ CONFIRMAR CPF", key="confirma_cpf"):
            cpf_limpo = sanitizar_cpf(cpf_input)
            if not validar_cpf(cpf_limpo):
                st.error("❌ CPF inválido. Digite um CPF com 11 dígitos.")
            else:
                pessoa = supabase.table("Pessoas").select("nome, empresa").eq("cpf", cpf_limpo).execute().data
                if pessoa:
                    st.session_state.pessoa_confirmada = {
                        "cpf": cpf_limpo,
                        "nome": sanitizar_texto(pessoa[0]['nome']),
                        "empresa": sanitizar_texto(pessoa[0].get('empresa', ''))
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
        try:
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
        except Exception as e:
            st.error(f"❌ Erro ao registrar entrada: {e}")
    else:
        st.warning("⚠️ Confirme o CPF antes de registrar a entrada.")

# ====================== PESSOAS PRESENTES ======================
st.markdown("---")
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
                cpf_limpo = sanitizar_cpf(cpf_pesquisa)
                pessoa_encontrada = None
                for p in dados:
                    if p['cpf'] == cpf_limpo:
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
                    try:
                        supabase.table("movimentacao").update({
                            "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        }).eq("id", p['id']).execute()
                        st.success(f"✅ Saída registrada para {p['nome']}")
                        st.session_state.pessoa_saida = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao registrar saída: {e}")
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
                try:
                    supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao registrar saída: {e}")
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
                        try:
                            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao registrar saída: {e}")
                    st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
            else:
                st.info(f"📭 Nenhuma pessoa no setor {setor}")
else:
    st.info("🏢 Nenhuma pessoa presente no momento")

# ====================== HISTÓRICO ======================
st.markdown("---")
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
        st.markdown("#### 🔹 Relatório por Setor (PDF separado)")
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
        st.markdown("#### 📑 Relatório Consolidado (Todos os Setores em uma folha)")
        if st.button("📑 Gerar PDF Consolidado (GRSA + Brasanitas + C.C + Prestadores)", key="btn_consolidado"):
            if not todos_dados:
                st.warning("Nenhum dado disponível para gerar o relatório consolidado.")
            else:
                html_consolidado = gerar_html_consolidado(df)
                if html_consolidado:
                    b64 = base64.b64encode(html_consolidado.encode()).decode()
                    href = f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Clique aqui para abrir o relatório consolidado (nova aba)</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    st.caption("Após abrir, pressione Ctrl+P e escolha 'Salvar como PDF'.")
                else:
                    st.error("Erro ao gerar o HTML consolidado.")

        st.markdown("---")
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

# ====================== GESTÃO DE CADASTROS DE PESSOAS (COM EDIÇÃO) ======================
st.markdown("---")
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        todos = supabase.table("Pessoas").select("id, nome, cpf, empresa").order("nome").execute().data

        if not todos:
            st.info("Nenhum cadastro encontrado.")
        else:
            # Separar por empresa
            funcionarios_brasanitas = [p for p in todos if p.get('empresa', '').upper() == "BRASANITAS"]
            funcionarios_grsa = [p for p in todos if p.get('empresa', '').upper() == "GRSA"]
            funcionarios_outros = [p for p in todos if p.get('empresa', '').upper() not in ["BRASANITAS", "GRSA"]]

            # Abas para cada categoria
            aba1, aba2, aba3 = st.tabs(["🏭 BRASANITAS", "🔧 GRSA", "🏢 OUTROS (Prestadores/Serviços)"])

            with aba1:
                st.markdown(f"**Total:** {len(funcionarios_brasanitas)} funcionários")
                if funcionarios_brasanitas:
                    for pessoa in funcionarios_brasanitas:
                        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                        col1.markdown(f"**👤 {pessoa['nome']}**")
                        col2.markdown(f"📄 CPF: {pessoa['cpf']}")
                        with col3:
                            with st.popover("✏️ Editar", use_container_width=True):
                                with st.form(key=f"edit_brasanitas_{pessoa['id']}"):
                                    novo_nome = st.text_input("Nome", value=pessoa['nome'])
                                    novo_cpf = st.text_input("CPF", value=pessoa['cpf'])
                                    nova_empresa = st.text_input("Empresa", value=pessoa.get('empresa', ''))
                                    if st.form_submit_button("💾 Salvar alterações"):
                                        if not novo_nome or not novo_cpf:
                                            st.error("Nome e CPF são obrigatórios.")
                                        elif not validar_cpf(novo_cpf):
                                            st.error("CPF inválido.")
                                        else:
                                            cpf_limpo = sanitizar_cpf(novo_cpf)
                                            # Verificar se o novo CPF já pertence a outro registro
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", cpf_limpo).neq("id", pessoa['id']).execute().data
                                            if conflito:
                                                st.error("Este CPF já está cadastrado para outra pessoa.")
                                            else:
                                                try:
                                                    supabase.table("Pessoas").update({
                                                        "nome": sanitizar_texto(novo_nome).strip().upper(),
                                                        "cpf": cpf_limpo,
                                                        "empresa": sanitizar_texto(nova_empresa).strip().upper() if nova_empresa else ""
                                                    }).eq("id", pessoa['id']).execute()
                                                    st.success("✅ Cadastro atualizado!")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Erro ao atualizar: {e}")
                        with col4:
                            with st.popover("🗑️ Excluir", use_container_width=True):
                                st.warning(f"Tem certeza que deseja excluir **{pessoa['nome']}**?")
                                if st.button("✅ Confirmar exclusão", key=f"del_brasanitas_{pessoa['id']}"):
                                    try:
                                        supabase.table("Pessoas").delete().eq("id", pessoa['id']).execute()
                                        st.success(f"✅ {pessoa['nome']} excluído com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao excluir: {e}")
                        st.divider()
                else:
                    st.info("Nenhum funcionário cadastrado para BRASANITAS.")

            with aba2:
                st.markdown(f"**Total:** {len(funcionarios_grsa)} funcionários")
                if funcionarios_grsa:
                    for pessoa in funcionarios_grsa:
                        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                        col1.markdown(f"**👤 {pessoa['nome']}**")
                        col2.markdown(f"📄 CPF: {pessoa['cpf']}")
                        with col3:
                            with st.popover("✏️ Editar", use_container_width=True):
                                with st.form(key=f"edit_grsa_{pessoa['id']}"):
                                    novo_nome = st.text_input("Nome", value=pessoa['nome'])
                                    novo_cpf = st.text_input("CPF", value=pessoa['cpf'])
                                    nova_empresa = st.text_input("Empresa", value=pessoa.get('empresa', ''))
                                    if st.form_submit_button("💾 Salvar alterações"):
                                        if not novo_nome or not novo_cpf:
                                            st.error("Nome e CPF são obrigatórios.")
                                        elif not validar_cpf(novo_cpf):
                                            st.error("CPF inválido.")
                                        else:
                                            cpf_limpo = sanitizar_cpf(novo_cpf)
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", cpf_limpo).neq("id", pessoa['id']).execute().data
                                            if conflito:
                                                st.error("Este CPF já está cadastrado para outra pessoa.")
                                            else:
                                                try:
                                                    supabase.table("Pessoas").update({
                                                        "nome": sanitizar_texto(novo_nome).strip().upper(),
                                                        "cpf": cpf_limpo,
                                                        "empresa": sanitizar_texto(nova_empresa).strip().upper() if nova_empresa else ""
                                                    }).eq("id", pessoa['id']).execute()
                                                    st.success("✅ Cadastro atualizado!")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Erro ao atualizar: {e}")
                        with col4:
                            with st.popover("🗑️ Excluir", use_container_width=True):
                                st.warning(f"Tem certeza que deseja excluir **{pessoa['nome']}**?")
                                if st.button("✅ Confirmar exclusão", key=f"del_grsa_{pessoa['id']}"):
                                    try:
                                        supabase.table("Pessoas").delete().eq("id", pessoa['id']).execute()
                                        st.success(f"✅ {pessoa['nome']} excluído com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao excluir: {e}")
                        st.divider()
                else:
                    st.info("Nenhum funcionário cadastrado para GRSA.")

            with aba3:
                st.markdown(f"**Total:** {len(funcionarios_outros)} pessoas")
                if funcionarios_outros:
                    search = st.text_input("🔍 Pesquisar por nome, CPF ou empresa", key="search_outros")
                    filtrados = funcionarios_outros
                    if search:
                        search_lower = search.lower()
                        filtrados = [p for p in funcionarios_outros if search_lower in p['nome'].lower() or search_lower in p['cpf'].lower() or search_lower in p.get('empresa', '').lower()]
                        st.caption(f"Mostrando {len(filtrados)} de {len(funcionarios_outros)} resultados")

                    for pessoa in filtrados:
                        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])
                        col1.markdown(f"**👤 {pessoa['nome']}**")
                        col2.markdown(f"📄 CPF: {pessoa['cpf']}")
                        col3.markdown(f"🏢 Empresa: {pessoa.get('empresa', 'N/A')}")
                        with col4:
                            with st.popover("✏️ Editar", use_container_width=True):
                                with st.form(key=f"edit_outros_{pessoa['id']}"):
                                    novo_nome = st.text_input("Nome", value=pessoa['nome'])
                                    novo_cpf = st.text_input("CPF", value=pessoa['cpf'])
                                    nova_empresa = st.text_input("Empresa", value=pessoa.get('empresa', ''))
                                    if st.form_submit_button("💾 Salvar alterações"):
                                        if not novo_nome or not novo_cpf:
                                            st.error("Nome e CPF são obrigatórios.")
                                        elif not validar_cpf(novo_cpf):
                                            st.error("CPF inválido.")
                                        else:
                                            cpf_limpo = sanitizar_cpf(novo_cpf)
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", cpf_limpo).neq("id", pessoa['id']).execute().data
                                            if conflito:
                                                st.error("Este CPF já está cadastrado para outra pessoa.")
                                            else:
                                                try:
                                                    supabase.table("Pessoas").update({
                                                        "nome": sanitizar_texto(novo_nome).strip().upper(),
                                                        "cpf": cpf_limpo,
                                                        "empresa": sanitizar_texto(nova_empresa).strip().upper() if nova_empresa else ""
                                                    }).eq("id", pessoa['id']).execute()
                                                    st.success("✅ Cadastro atualizado!")
                                                    st.rerun()
                                                except Exception as e:
                                                    st.error(f"Erro ao atualizar: {e}")
                        with col5:
                            with st.popover("🗑️ Excluir", use_container_width=True):
                                st.warning(f"Tem certeza que deseja excluir **{pessoa['nome']}**?")
                                if st.button("✅ Confirmar exclusão", key=f"del_outros_{pessoa['id']}"):
                                    try:
                                        supabase.table("Pessoas").delete().eq("id", pessoa['id']).execute()
                                        st.success(f"✅ {pessoa['nome']} excluído com sucesso!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erro ao excluir: {e}")
                        st.divider()
                else:
                    st.info("Nenhum cadastro encontrado na categoria 'Outros'.")

st.markdown("---")
st.markdown("""
    <div class="footer">
        👮‍♂️ JOHN ACESSOS - ACESSO DE DADOS | Segurança e Proteção de Dados | Monitoramento de Sessões
    </div>
""", unsafe_allow_html=True)
