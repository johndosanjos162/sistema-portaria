import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image
import base64
import re
import uuid
import json
import io

# --- CONFIGURAÇÃO DE SEGURANÇA ---
MAX_TENTATIVAS_LOGIN = 5
SESSION_TIMEOUT_MINUTOS = 5

# --- CONFIGURAÇÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    supabase.table("sessoes_ativas").select("id", count="exact").limit(1).execute()
except Exception as e:
    st.error(f"❌ Erro de conexão com Supabase: {e}")
    st.stop()

st.set_page_config(
    page_title="JOHN ACESSOS - ACESSO DE DADOS",
    layout="wide",
    page_icon="👮‍♂️",
    initial_sidebar_state="expanded"
)

# ====================== CSS: TORNAR A TOP BAR TRANSPARENTE ======================
st.markdown("""
<style>
    /* Torna o fundo do header transparente */
    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
    }
    /* Ajusta a cor dos ícones para branco (para contraste em fundos escuros) */
    header[data-testid="stHeader"] button {
        color: white !important;
    }
    /* Garante que o conteúdo do app não fique sobreposto pelo header */
    .stApp {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

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
        st.error(f"Erro ao registrar sessão: {e}")
        return False

def atualizar_atividade_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").update({
                "ultima_atividade": datetime.now().isoformat()
            }).eq("id", st.session_state.session_id).execute()
        except:
            pass

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
    except:
        return 0

def limpar_sessoes_expiradas():
    limite = (datetime.now() - pd.Timedelta(minutes=SESSION_TIMEOUT_MINUTOS)).isoformat()
    try:
        if "session_id" in st.session_state and st.session_state.session_id:
            supabase.table("sessoes_ativas").delete().lt("ultima_atividade", limite).neq("id", st.session_state.session_id).execute()
        else:
            supabase.table("sessoes_ativas").delete().lt("ultima_atividade", limite).execute()
    except:
        pass

def encerrar_outras_sessoes():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").delete().neq("id", st.session_state.session_id).execute()
            return True
        except:
            return False
    return False

# ====================== FUNÇÕES DE CONFIGURAÇÃO DE TEMA ======================
def compress_image_to_base64(uploaded_file, max_size_kb=500):
    img = Image.open(uploaded_file)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    max_width = 1920
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    quality = 85
    while True:
        buffer.seek(0)
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality <= 20:
            break
        quality -= 10
    b64_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64_str}"

def get_theme_config():
    padrao = {
        "type": "gradient",
        "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)",
        "apply_to_login": False,
        "image_adjust": "cover",
        "image_position": "center",
        "video_loop": True
    }
    try:
        result = supabase.table("app_config").select("value").eq("key", "background_config").execute()
        if result.data:
            config = json.loads(result.data[0]['value'])
            config.setdefault("image_adjust", "cover")
            config.setdefault("image_position", "center")
            config.setdefault("video_loop", True)
            return config
        else:
            save_theme_config(padrao)
            return padrao
    except Exception as e:
        st.error(f"Erro ao carregar tema: {e}")
        return padrao

def save_theme_config(config):
    try:
        supabase.table("app_config").upsert({
            "key": "background_config",
            "value": json.dumps(config),
            "updated_at": datetime.now().isoformat()
        }).execute()
        st.session_state.theme_config = config
        return True
    except Exception as e:
        st.error(f"Erro ao salvar tema global: {e}")
        return False

def apply_theme_css():
    config = st.session_state.get("theme_config", get_theme_config())
    bg_type = config.get("type", "gradient")
    
    if bg_type == "gradient":
        bg_value = config.get("value", "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)")
        css = f"""
        <style>
        html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{
            background: {bg_value} !important;
            background-attachment: fixed !important;
            background-size: cover !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif bg_type == "solid":
        bg_value = config.get("value", "#0a0a1a")
        css = f"""
        <style>
        html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{
            background: {bg_value} !important;
            background-attachment: fixed !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif bg_type == "url":
        bg_value = config.get("value", "")
        if not bg_value or bg_value.startswith("radial"):
            bg_value = "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
        adjust = config.get("image_adjust", "cover")
        position = config.get("image_position", "center")
        css = f"""
        <style>
        html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{
            background: {bg_value} !important;
            background-attachment: fixed !important;
            background-size: {adjust} !important;
            background-repeat: no-repeat !important;
            background-position: {position} !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif bg_type == "video":
        media_url = config.get("value", "")
        adjust = config.get("image_adjust", "cover")
        mime_type = config.get("mime_type", "video/mp4")
        video_loop = config.get("video_loop", True)
        loop_attr = "loop" if video_loop else ""
        if not media_url:
            st.markdown("""
            <style>
            .stApp { background: radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%); }
            </style>
            """, unsafe_allow_html=True)
            return
        
        container_div = "<div style='position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -9999; pointer-events: none;'>"
        if mime_type == "image/gif":
            media_html = f'<img src="{media_url}" style="width: 100%; height: 100%; object-fit: {adjust};">'
        else:
            media_html = f'<video autoplay muted playsinline {loop_attr} style="width: 100%; height: 100%; object-fit: {adjust};"><source src="{media_url}" type="{mime_type}"></video>'
        st.markdown(container_div + media_html + "</div>", unsafe_allow_html=True)
        
        st.markdown("""
        <style>
        .stApp {
            background: transparent !important;
        }
        .admin-card, .admin-header, .stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div, .stTabs [data-baseweb="tab-list"], .stTabs [data-baseweb="tab"] {
            background: rgba(20, 20, 40, 0.7) !important;
            backdrop-filter: blur(6px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        h1, h2, h3, p, label, .card-title, .card-value, .info-item, .stMarkdown, .stRadio label, .stCheckbox label, .stTextInput label, .stSelectbox label {
            color: #ffffff !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        [data-testid="stSidebar"] {
            background: rgba(8, 8, 20, 0.75) !important;
            backdrop-filter: blur(8px);
        }
        </style>
        """, unsafe_allow_html=True)

# ====================== FUNÇÕES DE RELATÓRIOS (PDF) ======================
def gerar_html_impressao(df, titulo):
    if df.empty:
        return None
    colunas = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida']
    colunas_existentes = [c for c in colunas if c in df.columns]
    df_rel = df[colunas_existentes].copy().fillna('')
    tabela = df_rel.to_html(escape=True, index=False)
    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>{titulo}</title>
    <style>
        body{{font-family:'Segoe UI',Arial,sans-serif;margin:2cm;}}
        h1{{text-align:center;color:#0a2b3e;}}
        .sub{{text-align:center;color:#555;margin-bottom:30px;}}
        table{{width:100%;border-collapse:collapse;font-size:10px;}}
        th{{background:#0a2b3e;color:white;padding:8px;}}
        td{{border:1px solid #ccc;padding:6px;}}
        tr:nth-child(even){{background:#f9f9f9;}}
        @media print{{body{{margin:1cm;}}.no-print{{display:none;}}}}
    </style></head>
    <body>
        <h1>JOHN ACESSOS - {titulo}</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        {tabela}
        <div class="no-print" style="text-align:center;margin-top:30px;"><button onclick="window.print();">🖨️ Imprimir / PDF</button></div>
    </body></html>
    """

def gerar_html_consolidado(df):
    if df.empty:
        return None
    def secao(df_filtro, titulo):
        df_filtro = df_filtro.copy().fillna('')
        if df_filtro.empty:
            return f"<div class='section'><h2>{titulo}</h2><p>Nenhum registro.</p></div>"
        colunas = ['id','nome','cpf','empresa','setor_destino','data_entrada','data_saida']
        existentes = [c for c in colunas if c in df_filtro.columns]
        tabela = df_filtro[existentes].to_html(escape=True, index=False)
        return f"<div class='section'><h2>{titulo} <span class='count-badge'>{len(df_filtro)}</span></h2>{tabela}</div>"
    html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>RELATÓRIO CONSOLIDADO</title>
    <style>
        body{{font-family:'Segoe UI',Arial,sans-serif;margin:2cm;}}
        h1{{text-align:center;color:#0a2b3e;}}
        .sub{{text-align:center;color:#555;margin-bottom:30px;}}
        .section{{margin-top:40px;page-break-inside:avoid;}}
        .section h2{{background:#0a2b3e;color:white;padding:8px;border-radius:8px;}}
        table{{width:100%;border-collapse:collapse;font-size:10px;margin-bottom:20px;}}
        th{{background:#0a2b3e;color:white;padding:8px;}}
        td{{border:1px solid #ccc;padding:6px;}}
        .count-badge{{display:inline-block;background:#a855f7;color:white;border-radius:20px;padding:2px 10px;margin-left:10px;}}
        @media print{{body{{margin:1cm;}}.no-print{{display:none;}}}}
    </style></head>
    <body>
        <h1>JOHN ACESSOS - RELATÓRIO CONSOLIDADO</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
    """
    html += secao(df[df['setor_destino'].str.contains('GRSA', case=False, na=False)], "🔧 GRSA")
    html += secao(df[df['setor_destino'].str.contains('Brasanitas', case=False, na=False)], "🏭 Brasanitas")
    html += secao(df[df['setor_destino'].str.contains('C.C', case=False, na=False)], "🏥 C.C")
    empresas_excluir = ["BRASANITAS", "GRSA", "C.C"]
    todas_empresas = df['empresa'].dropna().unique()
    prestadores = [e for e in todas_empresas if e.upper() not in [x.upper() for x in empresas_excluir]]
    if prestadores:
        html += secao(df[df['empresa'].isin(prestadores)], "🏢 Prestadores de Serviços")
    else:
        html += "<div class='section'><h2>🏢 Prestadores de Serviços</h2><p>Nenhum registro.</p></div>"
    html += '<div class="no-print" style="text-align:center;margin-top:30px;"><button onclick="window.print();">🖨️ Imprimir / PDF</button></div></body></html>'
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
    return texto.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# ====================== CARREGAR IMAGENS ======================
def carregar_imagem(nome):
    try:
        return Image.open(nome)
    except:
        return None

IMAGEM_SIDEBAR = carregar_imagem("sidebar_logo.png")

# ====================== CSS BASE (SEM BACKGROUND FIXO) ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono&display=swap');
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(100,0,255,0.4); } 70% { box-shadow: 0 0 0 12px rgba(100,0,255,0); } 100% { box-shadow: 0 0 0 0 rgba(100,0,255,0); } }
@keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-6px); } 100% { transform: translateY(0px); } }
@keyframes buttonGlow { 0% { box-shadow: 0 0 5px #0ff; } 50% { box-shadow: 0 0 20px #0ff; } 100% { box-shadow: 0 0 5px #0ff; } }
[data-testid="stSidebar"] { background: rgba(8,8,20,0.85); backdrop-filter: blur(12px); border-right: 1px solid rgba(100,0,255,0.3); }
.sidebar-header { text-align: center; padding: 25px 10px; border-bottom: 1px solid rgba(100,0,255,0.5); }
.sidebar-title { font-size: 22px; font-weight: 800; background: linear-gradient(135deg, #a855f7, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.info-item { margin-bottom: 12px; color: #c4b5fd; font-size: 12px; display: flex; gap: 8px; font-family: 'Space Mono', monospace; }
.admin-header { background: rgba(8,8,20,0.7); backdrop-filter: blur(8px); border-radius: 16px; padding: 12px 20px; margin-bottom: 20px; border: 1px solid rgba(168,85,247,0.4); }
.badge-admin { background: linear-gradient(135deg, #a855f7, #3b82f6); padding: 4px 15px; border-radius: 30px; font-weight: 700; font-size: 11px; color: white; }
.session-indicator { background: rgba(0,0,0,0.6); border-radius: 30px; padding: 4px 12px; font-size: 12px; font-family: 'Space Mono', monospace; color: #a78bfa; display: inline-flex; align-items: center; gap: 5px; }
.admin-card { background: rgba(15,15,30,0.6); backdrop-filter: blur(4px); border-radius: 20px; padding: 18px; border: 1px solid rgba(168,85,247,0.2); transition: 0.2s; }
.admin-card:hover { transform: translateY(-3px); border-color: #a855f7; box-shadow: 0 5px 20px rgba(168,85,247,0.15); }
.card-title { font-size: 10px; letter-spacing: 2px; color: #a78bfa; }
.card-value { font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #fff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stButton>button, .stForm button { border-radius: 40px; font-weight: 600; background: linear-gradient(90deg, #a855f7, #3b82f6); color: white; border: none; transition: all 0.3s ease; position: relative; overflow: hidden; z-index: 1; }
.stButton>button::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent); transition: left 0.5s ease; z-index: -1; }
.stButton>button:hover::before { left: 100%; }
.stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 20px #a855f7; animation: buttonGlow 0.8s infinite alternate; }
.stTextInput>div>div>input, .stNumberInput>div>div>input { background: rgba(0,0,0,0.8); border: 1px solid #a855f7; border-radius: 12px; color: #0ff !important; font-family: 'Space Mono', monospace; }
.stSelectbox>div>div { background: rgba(0,0,0,0.8) !important; border: 1px solid #a855f7 !important; border-radius: 12px !important; color: #0ff !important; }
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: rgba(0,0,0,0.3); padding: 5px; border-radius: 30px; }
.stTabs [data-baseweb="tab"] { border-radius: 25px; padding: 5px 20px; color: #ccc; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, #a855f7, #3b82f6); color: white; }
.footer { text-align: center; padding: 15px; color: #6b7280; font-size: 9px; border-top: 1px solid rgba(168,85,247,0.2); margin-top: 25px; }
h1, h2, h3 { font-family: 'Inter', sans-serif; color: #e9d5ff; }
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
if IMAGEM_SIDEBAR:
    st.sidebar.image(IMAGEM_SIDEBAR, use_container_width=True)
else:
    st.sidebar.markdown('<div class="sidebar-header"><div class="sidebar-title">👮‍♂️ JOHN ACESSOS</div><p style="color:#a78bfa; font-size:9px;">ACESSO DE DADOS</p></div>', unsafe_allow_html=True)

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

# ====================== INICIALIZAÇÃO ======================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "perfil" not in st.session_state:
    st.session_state.perfil = ""
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

st.session_state.theme_config = get_theme_config()

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    theme = st.session_state.theme_config
    if theme.get("apply_to_login", False):
        apply_theme_css()
    else:
        st.markdown('<style>.stApp{background:radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);}</style>', unsafe_allow_html=True)
    if st.session_state.bloqueado_ate and datetime.now() < st.session_state.bloqueado_ate:
        st.error(f"⛔ Bloqueado até {st.session_state.bloqueado_ate.strftime('%H:%M:%S')}")
        st.stop()
    st.markdown("""
    <style>
    .login-container{display:flex;justify-content:center;align-items:center;min-height:80vh;}
    .login-box{background:rgba(8,8,20,0.7);backdrop-filter:blur(20px);border-radius:50px;padding:45px 35px;border:1px solid rgba(168,85,247,0.6);width:100%;max-width:480px;text-align:center;animation:float 3s ease-in-out infinite;}
    .guard-logo{width:110px;height:110px;margin:0 auto 20px;background:radial-gradient(circle,rgba(168,85,247,0.3),rgba(59,130,246,0.1));border-radius:50%;display:flex;align-items:center;justify-content:center;position:relative;animation:pulse 2s infinite;}
    .guard-logo span{font-size:60px;filter:drop-shadow(0 0 10px #a855f7);}
    .logo-title{font-size:32px;font-weight:800;background:linear-gradient(135deg,#fff,#a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .logo-subtitle{font-size:11px;color:#a78bfa;letter-spacing:3px;margin-bottom:25px;}
    .binary-stream{font-family:'Space Mono',monospace;font-size:10px;background:rgba(0,0,0,0.5);padding:6px;border-radius:20px;display:inline-block;color:#a855f7;margin-bottom:15px;}
    </style>
    <div class="login-container"><div class="login-box">
    <div class="guard-logo"><span>👮‍♂️🔒</span></div>
    <div class="logo-title">JOHN ACESSOS</div>
    <div class="logo-subtitle">ACESSO DE DADOS</div>
    <div id="binary-container" style="text-align:center; margin-bottom:15px;"></div>
    <script>function generateBinary(){let b='';for(let i=0;i<60;i++)b+=Math.random()<0.5?'0':'1';return b;}
    setInterval(()=>{let el=document.getElementById('binary-container');if(el)el.innerHTML=`<div class="binary-stream">${generateBinary()}</div>`;},400);</script>
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
                    st.error("⛔ Acesso bloqueado por 5 minutos.")
                else:
                    st.error(f"❌ ACESSO NEGADO - Tentativas restantes: {restantes}")
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ====================== APÓS LOGIN ======================
apply_theme_css()

if st.session_state.session_id:
    atualizar_atividade_sessao()
    limpar_sessoes_expiradas()
    total_conectados = contar_sessoes_ativas()
else:
    total_conectados = 0

# ====================== CABEÇALHO PERSONALIZADO (OPCIONAL) ======================
# Se quiser manter o título e badge, pode deixar; se não, remova este bloco.
st.markdown(f"""
<div class="admin-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; gap:10px; align-items:center;">
            <div style="width:36px;height:36px;background:linear-gradient(135deg,#a855f7,#3b82f6);border-radius:50%;display:flex;align-items:center;justify-content:center;"><span style="font-size:20px;">👮‍♂️</span></div>
            <div><h1 style="margin:0;font-size:16px;">JOHN ACESSOS - ACESSO DE DADOS</h1><p style="margin:0;color:#a78bfa;font-size:8px;">SEGURANÇA E PROTEÇÃO</p></div>
        </div>
        <div style="display:flex; gap:15px; align-items:center;">{f'<div class="session-indicator">{"⚠️" if total_conectados > 1 else ""} 👥 {total_conectados}</div>'}<div class="badge-admin">👑 {st.session_state.perfil}</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([6,1,1,1])
with col3:
    if st.button("🔄 ATUALIZAR", key="btn_atualizar", use_container_width=True):
        st.rerun()
with col4:
    if st.button("🚪 SAIR", key="sair_final", use_container_width=True):
        remover_sessao()
        st.session_state.logado = False
        st.rerun()

# ====================== ADMIN: MANAGE APP E TEMA GLOBAL ======================
if st.session_state.perfil == "ADMIN":
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ MANAGE APP", expanded=False):
        st.markdown("### 🔧 Ferramentas Administrativas")
        total_ativas = contar_sessoes_ativas()
        st.metric("👥 Sessões ativas", total_ativas)
        if st.button("🔒 Encerrar outras sessões", use_container_width=True, key="encerrar_sessoes"):
            if encerrar_outras_sessoes():
                st.success("✅ Todas as outras sessões foram encerradas!")
                st.rerun()
            else:
                st.error("❌ Erro ao encerrar outras sessões.")
        if st.button("🧹 Limpar sessões expiradas", use_container_width=True, key="limpar_sessoes"):
            limpar_sessoes_expiradas()
            st.success("✅ Sessões expiradas removidas!")
            st.rerun()
        st.caption("Ações disponíveis apenas para o administrador.")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("🎨 Configurar Tema (Global)", expanded=False):
        st.markdown("### Personalizar Fundo - Aplica para todos os usuários")
        config_atual = st.session_state.theme_config
        tipo_atual = config_atual.get("type", "gradient")
        opcoes = ["Gradiente padrão", "Cor sólida", "Imagem (URL)", "Imagem (upload)", "Animação (URL)"]
        idx_map = {"gradient":0, "solid":1, "url":2, "image_upload":3, "video":4}
        idx = idx_map.get(tipo_atual, 0)
        tipo = st.radio("Tipo de fundo:", opcoes, index=idx, key="tipo_fundo_radio")
        
        novo_valor = config_atual.get("value", "")
        novo_tipo = tipo_atual
        novo_mime = config_atual.get("mime_type", "")
        video_loop = config_atual.get("video_loop", True)
        
        if tipo == "Gradiente padrão":
            novo_valor = "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
            novo_tipo = "gradient"
        elif tipo == "Cor sólida":
            cor_padrao = config_atual.get("value", "#0a0a1a") if tipo_atual == "solid" else "#0a0a1a"
            cor = st.color_picker("Escolha a cor", value=cor_padrao, key="cor_picker")
            novo_valor = cor
            novo_tipo = "solid"
        elif tipo == "Imagem (URL)":
            url_padrao = ""
            if tipo_atual == "url" and config_atual.get("value", "").startswith("url('"):
                match = re.search(r"url\('([^']+)'", config_atual.get("value", ""))
                if match:
                    url_padrao = match.group(1)
            url_img = st.text_input("URL da imagem", value=url_padrao, key="url_img", placeholder="https://exemplo.com/imagem.jpg")
            if url_img and (url_img.startswith('http://') or url_img.startswith('https://')):
                novo_valor = url_img
                novo_tipo = "url"
            elif url_img:
                st.error("URL inválida. Use http:// ou https://")
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
            else:
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
        elif tipo == "Imagem (upload)":
            uploaded_file = st.file_uploader("Escolha uma imagem (PNG, JPG, JPEG, GIF)", type=["png","jpg","jpeg","gif"], key="upload_img")
            if uploaded_file:
                with st.spinner("Processando imagem..."):
                    try:
                        imagem_data_url = compress_image_to_base64(uploaded_file)
                        novo_valor = imagem_data_url
                        novo_tipo = "url"
                        st.success("✅ Imagem carregada e comprimida com sucesso!")
                        st.image(uploaded_file, width=200, caption="Imagem carregada")
                    except Exception as e:
                        st.error(f"Erro ao processar imagem: {e}")
                        novo_valor = config_atual.get("value", "")
                        novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
            else:
                if tipo_atual == "url" and config_atual.get("value", "").startswith("data:image"):
                    novo_valor = config_atual.get("value")
                    novo_tipo = "url"
                else:
                    novo_valor = config_atual.get("value", "")
                    novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
        else:  # Animação (URL)
            url_padrao = ""
            if tipo_atual == "video":
                url_padrao = config_atual.get("value", "")
            url_media = st.text_input("URL do vídeo/GIF (MP4/GIF)", value=url_padrao, key="url_video", placeholder="https://exemplo.com/video.mp4")
            video_loop = st.checkbox("Reproduzir em loop infinito", value=config_atual.get("video_loop", True), key="video_loop")
            if url_media and (url_media.startswith('http://') or url_media.startswith('https://')):
                novo_valor = url_media
                novo_tipo = "video"
                if url_media.lower().endswith('.gif'):
                    novo_mime = "image/gif"
                else:
                    novo_mime = "video/mp4"
                st.success("✅ URL de mídia configurada!")
            elif url_media:
                st.error("URL inválida. Use http:// ou https://")
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
            else:
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
        
        ajuste_opcoes = ["cover", "contain", "stretch"]
        if novo_tipo in ["url", "video"]:
            st.markdown("---")
            st.markdown("#### Ajustes da mídia")
            ajuste_atual = config_atual.get("image_adjust", "cover")
            posicao_atual = config_atual.get("image_position", "center")
            novo_ajuste = st.selectbox("Modo de ajuste:", ajuste_opcoes, index=ajuste_opcoes.index(ajuste_atual) if ajuste_atual in ajuste_opcoes else 0, key="ajuste_imagem")
            nova_posicao = st.selectbox("Posição (para imagens fixas):", ["center", "top", "bottom", "left", "right", "top left", "top right", "bottom left", "bottom right"], index=3 if posicao_atual == "center" else 0, key="posicao_imagem")
        else:
            novo_ajuste = "cover"
            nova_posicao = "center"
        
        st.markdown("**Prévia:**")
        if novo_tipo == "gradient":
            preview_style = novo_valor
            st.markdown(f'<div style="width:100%; height:50px; background:{preview_style}; border-radius:8px; border:1px solid #fff;"></div>', unsafe_allow_html=True)
        elif novo_tipo == "solid":
            preview_style = novo_valor
            st.markdown(f'<div style="width:100%; height:50px; background:{preview_style}; border-radius:8px; border:1px solid #fff;"></div>', unsafe_allow_html=True)
        elif novo_tipo == "url":
            preview_style = f"url('{novo_valor}') {nova_posicao}/{novo_ajuste} no-repeat fixed" if novo_valor else "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
            st.markdown(f'<div style="width:100%; height:50px; background:{preview_style}; border-radius:8px; border:1px solid #fff;"></div>', unsafe_allow_html=True)
        else:  # video
            if novo_valor:
                if novo_mime == "image/gif":
                    st.markdown(f'<img src="{novo_valor}" style="width:100%; max-height:100px; object-fit:cover; border-radius:8px;">', unsafe_allow_html=True)
                else:
                    st.video(novo_valor, format="video/mp4")
            else:
                st.info("Informe uma URL para prévia")
        
        aplicar_login = st.checkbox("Aplicar também na tela de login", value=config_atual.get("apply_to_login", False), key="aplicar_login_check")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("💾 Salvar e Aplicar Tema (Global)", key="salvar_tema_global"):
                if novo_tipo == "gradient":
                    valor_final = novo_valor
                elif novo_tipo == "solid":
                    valor_final = novo_valor
                elif novo_tipo == "url":
                    if novo_valor:
                        valor_final = f"url('{novo_valor}') {nova_posicao}/{novo_ajuste} no-repeat fixed"
                    else:
                        valor_final = "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
                        novo_tipo = "gradient"
                else:  # video
                    valor_final = novo_valor if novo_valor else "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
                    if not novo_valor:
                        novo_tipo = "gradient"
                
                nova_config = {
                    "type": novo_tipo,
                    "value": valor_final,
                    "apply_to_login": aplicar_login,
                    "image_adjust": novo_ajuste,
                    "image_position": nova_posicao,
                    "mime_type": novo_mime if novo_tipo == "video" else "",
                    "video_loop": video_loop if novo_tipo == "video" else True
                }
                if save_theme_config(nova_config):
                    apply_theme_css()
                    st.success("✅ Tema global salvo e aplicado! Todos os usuários verão este tema.")
                else:
                    st.error("Erro ao salvar tema global.")
        with col_btn2:
            if st.button("↺ Restaurar Padrão", key="reset_tema_global"):
                padrao = {
                    "type": "gradient",
                    "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)",
                    "apply_to_login": False,
                    "image_adjust": "cover",
                    "image_position": "center",
                    "mime_type": "",
                    "video_loop": True
                }
                if save_theme_config(padrao):
                    apply_theme_css()
                    st.success("Tema restaurado para o padrão global!")
        with col_btn3:
            if st.button("🔄 Recarregar Tema do Banco", key="reload_tema"):
                st.session_state.theme_config = get_theme_config()
                apply_theme_css()
                st.success("Tema recarregado do Supabase!")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("📤 Compartilhar Dados de Pessoas", expanded=False):
        st.markdown("### Exportar Cadastros")
        try:
            todas_pessoas = supabase.table("Pessoas").select("nome, cpf, empresa").execute().data
            if not todas_pessoas:
                st.info("Nenhuma pessoa cadastrada ainda.")
            else:
                df_todas = pd.DataFrame(todas_pessoas)
                empresas = sorted([e for e in df_todas['empresa'].unique() if e and e.strip()])
                opcoes_empresa = ["Todos"] + empresas
                empresa_selecionada = st.selectbox("Filtrar por unidade (empresa):", opcoes_empresa, key="export_empresa")
                if empresa_selecionada == "Todos":
                    df_export = df_todas.copy()
                    st.write(f"Total de registros: {len(df_export)}")
                else:
                    df_export = df_todas[df_todas['empresa'] == empresa_selecionada].copy()
                    st.write(f"Total de registros para {empresa_selecionada}: {len(df_export)}")
                if not df_export.empty:
                    csv = df_export.to_csv(index=False, encoding='utf-8-sig')
                    nome_arquivo = f"cadastros_{empresa_selecionada.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    st.download_button(
                        label="📥 Baixar CSV",
                        data=csv,
                        file_name=nome_arquivo,
                        mime="text/csv",
                        key="download_csv_pessoas"
                    )
                else:
                    st.warning("Nenhum registro para o filtro selecionado.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")

# ====================== DASHBOARD ======================
st.markdown("---")
try:
    pessoas_presentes = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
    total_presentes = len(pessoas_presentes)
    total_colaboradores = len(supabase.table("Pessoas").select("*").execute().data)
except:
    total_presentes = 0
    total_colaboradores = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="admin-card"><div style="display:flex;justify-content:space-between;"><div><div class="card-title">📍 PRESENTES</div><div class="card-value">{total_presentes}</div></div><div style="font-size:22px;">👥</div></div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="admin-card"><div><div class="card-title">📋 CADASTRADOS</div><div class="card-value">{total_colaboradores}</div></div><div style="font-size:22px;">📊</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="admin-card"><div><div class="card-title">🏥 SETORES</div><div class="card-value">11</div></div><div style="font-size:22px;">🏛️</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="admin-card"><div><div class="card-title">🎥 CFTV</div><div class="card-value">24/7</div></div><div style="font-size:22px;">📹</div></div>', unsafe_allow_html=True)

# ====================== CADASTRO ======================
st.markdown("---")
st.markdown("### ✚ Cadastro de Nova Pessoa")
with st.expander("📋 Formulário de Cadastro", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("📄 CPF *", placeholder="000.000.000-00", key="novo_cpf")
    novo_nome = col_b.text_input("👤 Nome Completo *", key="novo_nome")
    novo_empresa = col_c.text_input("🏢 Empresa", key="novo_empresa")
    if st.button("💾 Salvar Cadastro", key="salvar_cadastro", type="primary"):
        if novo_cpf and novo_nome:
            if not validar_cpf(novo_cpf):
                st.error("❌ CPF inválido.")
            else:
                cpf_limpo = sanitizar_cpf(novo_cpf)
                try:
                    existe = supabase.table("Pessoas").select("id, empresa").eq("cpf", cpf_limpo).execute().data
                    if existe:
                        st.error(f"❌ Pessoa já cadastrada (Empresa: {existe[0].get('empresa', 'N/A')})")
                    else:
                        supabase.table("Pessoas").insert({
                            "cpf": cpf_limpo,
                            "nome": sanitizar_texto(novo_nome).strip().upper(),
                            "empresa": sanitizar_texto(novo_empresa).strip().upper() if novo_empresa else ""
                        }).execute()
                        st.success("✅ Cadastro salvo!")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.error("CPF e Nome obrigatórios.")

# ====================== REGISTRO DE ENTRADA ======================
st.markdown("---")
st.markdown("### 📋 Registrar Movimentação")
tipo = st.radio("👥 Tipo de Pessoa:", ["🏢 Prestador de serviços", "🔧 Terceirizados / Instrumentadores"], horizontal=True, key="tipo_pessoa")
if tipo == "🏢 Prestador de serviços":
    destinos = ["🏥 C.C", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção", "🧪 Laboratório", "💊 Farmacia", "🏥 P.A", "👶 PEDIATRIA P.A", "🔧 ENG.CLINICA", "🧹 HORTELARIA", "📦 OPME 6°AND", "📦 OPME 9°AND", "🔒 SSGA", "🏥 CDU", "⚕️ ONCOLOGIA"]
else:
    destinos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

col_cpf, col_btn = st.columns([3,1])
with col_cpf:
    cpf_input = st.text_input("📄 CPF:", key="cpf_entrada", placeholder="Digite o CPF")
with col_btn:
    if cpf_input:
        if st.button("✅ CONFIRMAR CPF", key="confirma_cpf"):
            cpf_limpo = sanitizar_cpf(cpf_input)
            if not validar_cpf(cpf_limpo):
                st.error("CPF inválido")
            else:
                try:
                    pessoa = supabase.table("Pessoas").select("nome, empresa").eq("cpf", cpf_limpo).execute().data
                    if pessoa:
                        st.session_state.pessoa_confirmada = {"cpf": cpf_limpo, "nome": pessoa[0]['nome'], "empresa": pessoa[0].get('empresa', '')}
                        st.success(f"✅ {pessoa[0]['nome']} - {pessoa[0].get('empresa','N/A')}")
                    else:
                        st.error("CPF não cadastrado")
                        st.session_state.pessoa_confirmada = None
                except:
                    st.error("Erro ao buscar CPF")
    else:
        st.button("✅ CONFIRMAR CPF", disabled=True, key="confirma_cpf_disabled")

setor_escolhido = st.selectbox("📍 Destino:", destinos, key="destino")
if st.button("✅ Registrar Entrada", key="btn_entrada", type="primary"):
    if st.session_state.get("pessoa_confirmada"):
        p = st.session_state.pessoa_confirmada
        try:
            supabase.table("movimentacao").insert({
                "cpf": p['cpf'], "nome": p['nome'], "empresa": p['empresa'],
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "data_saida": ""
            }).execute()
            st.success(f"Entrada registrada para {setor_escolhido}!")
            st.session_state.pessoa_confirmada = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Confirme o CPF primeiro.")

# ====================== PESSOAS PRESENTES ======================
st.markdown("---")
st.markdown("### 📍 Pessoas Presentes")
try:
    dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
except:
    dados = []
if dados:
    st.markdown("#### 🔍 Pesquisar CPF para saída")
    col_pesq, col_btn_sair = st.columns([3,1])
    with col_pesq:
        cpf_saida = st.text_input("CPF:", key="cpf_saida", placeholder="Digite o CPF")
    with col_btn_sair:
        if st.button("🔎 Buscar", key="buscar_saida"):
            if cpf_saida:
                encontrado = next((p for p in dados if p['cpf'] == sanitizar_cpf(cpf_saida)), None)
                if encontrado:
                    st.session_state.pessoa_saida = encontrado
                    st.success(f"Pessoa encontrada: {encontrado['nome']}")
                else:
                    st.error("Não encontrado")
                    st.session_state.pessoa_saida = None
    if st.session_state.get("pessoa_saida"):
        p = st.session_state.pessoa_saida
        st.markdown(f"**{p['nome']}** - CPF: {p['cpf']} - Setor: {p['setor_destino']}")
        if st.button("🚪 Registrar Saída", key="sair_pesquisado"):
            try:
                supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                st.success("Saída registrada")
                st.session_state.pessoa_saida = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
        st.markdown("---")
    st.markdown("#### 📋 Lista completa")
    tabs = st.tabs(["📊 Prestador de Serviço", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"])
    with tabs[0]:
        for p in dados:
            col1, col2, col3, col4 = st.columns([4,3,2,2])
            col1.write(f"**{p['nome']}**")
            col2.write(f"📍 {p['setor_destino']}")
            col3.write(f"🏢 {p.get('empresa','N/A')}")
            if col4.button("🚪 Saída", key=f"saida_{p['id']}"):
                try:
                    supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                    st.rerun()
                except:
                    pass
            st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
    for i, setor in enumerate(["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"], 1):
        with tabs[i]:
            setor_clean = setor.split()[-1]
            pessoas_setor = [p for p in dados if setor_clean in p['setor_destino']]
            for p in pessoas_setor:
                col1, col2, col3, col4 = st.columns([4,3,2,2])
                col1.write(f"**{p['nome']}**")
                col2.write(f"🏢 {p.get('empresa','N/A')}")
                col3.write(f"🕒 {p['data_entrada']}")
                if col4.button("🚪 Saída", key=f"saida2_{p['id']}"):
                    try:
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                        st.rerun()
                    except:
                        pass
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
else:
    st.info("Nenhuma pessoa presente no momento")

# ====================== HISTÓRICO ======================
st.markdown("---")
with st.expander("🕒 Histórico Completo de Movimentações", expanded=True):
    try:
        todos = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    except:
        todos = []
    if todos:
        df = pd.DataFrame(todos)
        st.markdown("### 📄 Gerar Relatório")
        if st.button("📑 Relatório completo", key="relatorio_completo"):
            html = gerar_html_impressao(df, "RELATÓRIO COMPLETO")
            if html:
                b64 = base64.b64encode(html.encode()).decode()
                st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir relatório (Ctrl+P para PDF)</a>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### 📑 Relatório Consolidado")
        if st.button("📑 Consolidado (todos setores)", key="relatorio_consolidado"):
            html = gerar_html_consolidado(df)
            if html:
                b64 = base64.b64encode(html.encode()).decode()
                st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir consolidado</a>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🗑️ Exclusão de Registros")
        for idx, row in df.iterrows():
            col_check, col_data = st.columns([0.5, 9.5])
            with col_check:
                checked = st.checkbox("", key=f"chk_{row['id']}", value=row['id'] in st.session_state.selected_ids)
                if checked and row['id'] not in st.session_state.selected_ids:
                    st.session_state.selected_ids.append(row['id'])
                elif not checked and row['id'] in st.session_state.selected_ids:
                    st.session_state.selected_ids.remove(row['id'])
            with col_data:
                st.markdown(f"ID {row['id']} - {row['nome']} | CPF: {row['cpf']} | Empresa: {row.get('empresa','N/A')} | Entrada: {row['data_entrada']} | Saída: {row['data_saida'] or 'Presente'}")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🗑️ Excluir Selecionados", key="excluir_selecionados"):
                if st.session_state.selected_ids:
                    st.session_state.pending_delete_ids = st.session_state.selected_ids.copy()
                    st.rerun()
        with col_btn2:
            if st.button("📋 Limpar Seleção", key="limpar_selecao"):
                st.session_state.selected_ids = []
                st.rerun()
        with col_btn3:
            if st.button("⚠️ LIMPAR TODO HISTÓRICO", key="limpar_historico"):
                st.session_state.pending_clear_all = True
                st.rerun()
        if st.session_state.pending_delete_ids:
            st.error(f"⚠️ Excluir {len(st.session_state.pending_delete_ids)} registro(s)?")
            col_conf, col_canc = st.columns(2)
            with col_conf:
                if st.button("✅ SIM, EXCLUIR", key="confirmar_excluir"):
                    try:
                        for id_ in st.session_state.pending_delete_ids:
                            supabase.table("movimentacao").delete().eq("id", id_).execute()
                        st.session_state.selected_ids = []
                        st.session_state.pending_delete_ids = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            with col_canc:
                if st.button("❌ Cancelar", key="cancelar_excluir"):
                    st.session_state.pending_delete_ids = []
                    st.rerun()
        if st.session_state.pending_clear_all:
            st.error("🚨 ATENÇÃO: apagar TODOS os registros. Digite 'LIMPAR TUDO'")
            confirm = st.text_input("Confirmação:", type="password", key="confirma_limpar")
            col_clear, col_cancel_clear = st.columns(2)
            with col_clear:
                if st.button("🔥 EXCLUIR TUDO", key="excluir_tudo"):
                    if confirm == "LIMPAR TUDO":
                        try:
                            supabase.table("movimentacao").delete().neq("id", 0).execute()
                            st.success("Histórico limpo!")
                            st.session_state.pending_clear_all = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.error("Confirmação incorreta")
            with col_cancel_clear:
                if st.button("Cancelar", key="cancelar_limpar"):
                    st.session_state.pending_clear_all = False
                    st.rerun()
    else:
        st.info("Nenhum registro encontrado.")

# ====================== GESTÃO DE CADASTROS (ADMIN) ======================
st.markdown("---")
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        try:
            todos = supabase.table("Pessoas").select("id, nome, cpf, empresa").order("nome").execute().data
        except:
            todos = []
        if not todos:
            st.info("Nenhum cadastro")
        else:
            br = [p for p in todos if p.get('empresa', '').upper() == "BRASANITAS"]
            gr = [p for p in todos if p.get('empresa', '').upper() == "GRSA"]
            outros = [p for p in todos if p.get('empresa', '').upper() not in ["BRASANITAS", "GRSA"]]
            tab1, tab2, tab3 = st.tabs(["🏭 BRASANITAS", "🔧 GRSA", "🏢 OUTROS"])
            with tab1:
                st.markdown(f"**Total:** {len(br)}")
                for p in br:
                    col1, col2, col3, col4 = st.columns([3,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    with col3:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_br_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_br_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_br_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_br_{p['id']}")
                                if st.form_submit_button("Salvar", key=f"save_br_{p['id']}"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase.table("Pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                st.success("Atualizado!")
                                                st.rerun()
                                            else:
                                                st.error("CPF já existe")
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    else:
                                        st.error("CPF inválido")
                    with col4:
                        with st.popover("🗑️ Excluir"):
                            st.warning(f"Excluir {p['nome']}?")
                            if st.button("Confirmar", key=f"del_br_{p['id']}"):
                                try:
                                    supabase.table("Pessoas").delete().eq("id", p['id']).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    st.divider()
            with tab2:
                st.markdown(f"**Total:** {len(gr)}")
                for p in gr:
                    col1, col2, col3, col4 = st.columns([3,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    with col3:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_gr_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_gr_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_gr_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_gr_{p['id']}")
                                if st.form_submit_button("Salvar", key=f"save_gr_{p['id']}"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase.table("Pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                st.success("Atualizado!")
                                                st.rerun()
                                            else:
                                                st.error("CPF já existe")
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    else:
                                        st.error("CPF inválido")
                    with col4:
                        with st.popover("🗑️ Excluir"):
                            st.warning(f"Excluir {p['nome']}?")
                            if st.button("Confirmar", key=f"del_gr_{p['id']}"):
                                try:
                                    supabase.table("Pessoas").delete().eq("id", p['id']).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    st.divider()
            with tab3:
                st.markdown(f"**Total:** {len(outros)}")
                search = st.text_input("🔍 Pesquisar", key="search_outros")
                filtrados = [p for p in outros if search.lower() in p['nome'].lower() or search.lower() in p['cpf'] or search.lower() in p.get('empresa','').lower()] if search else outros
                for p in filtrados:
                    col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    col3.write(f"Empresa: {p.get('empresa','N/A')}")
                    with col4:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_out_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_out_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_out_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_out_{p['id']}")
                                if st.form_submit_button("Salvar", key=f"save_out_{p['id']}"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase.table("Pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                st.success("Atualizado!")
                                                st.rerun()
                                            else:
                                                st.error("CPF já existe")
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    else:
                                        st.error("CPF inválido")
                    with col5:
                        with st.popover("🗑️ Excluir"):
                            st.warning(f"Excluir {p['nome']}?")
                            if st.button("Confirmar", key=f"del_out_{p['id']}"):
                                try:
                                    supabase.table("Pessoas").delete().eq("id", p['id']).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    st.divider()

apply_theme_css()

st.markdown("---")
st.markdown("""
<div class="footer">
    👮‍♂️ JOHN ACESSOS - ACESSO DE DADOS | Segurança e Proteção de Dados | Monitoramento de Sessões
</div>
""", unsafe_allow_html=True)
