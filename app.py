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
import time
from functools import wraps
import gc
from datetime import timedelta

# ====================== CONFIGURAÇÕES DE PERFORMANCE ======================
CACHE_TTL_PADRAO = 30
ITENS_POR_PAGINA = 50
DEBOUNCE_WAIT_MS = 500

class TimedCache:
    def __init__(self, ttl_seconds=CACHE_TTL_PADRAO):
        self.ttl_seconds = ttl_seconds
        self.cache_data = {}
        self.cache_times = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        now = time.time()
        if key in self.cache_data and (now - self.cache_times.get(key, 0)) < self.ttl_seconds:
            self.hits += 1
            return self.cache_data[key]
        self.misses += 1
        return None
    
    def set(self, key, value):
        self.cache_data[key] = value
        self.cache_times[key] = time.time()
    
    def clear(self):
        self.cache_data.clear()
        self.cache_times.clear()
    
    def get_hit_ratio(self):
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0

def debounce(wait_time=DEBOUNCE_WAIT_MS):
    def decorator(func):
        last_call = 0
        last_result = None
        def wrapper(*args, **kwargs):
            nonlocal last_call, last_result
            current_time = time.time() * 1000
            if current_time - last_call >= wait_time:
                last_call = current_time
                last_result = func(*args, **kwargs)
                return last_result
            return last_result
        return wrapper
    return decorator

cache_estatisticas = TimedCache(ttl_seconds=30)
cache_pessoas = TimedCache(ttl_seconds=60)
cache_presentes = TimedCache(ttl_seconds=10)

def invalidar_cache():
    cache_estatisticas.clear()
    cache_pessoas.clear()
    cache_presentes.clear()

def registrar_tempo_query(tempo_ms):
    if "tempos_query" not in st.session_state:
        st.session_state.tempos_query = []
    st.session_state.tempos_query.append(tempo_ms)
    if len(st.session_state.tempos_query) > 100:
        st.session_state.tempos_query = st.session_state.tempos_query[-100:]

def get_tempo_medio_query():
    tempos = st.session_state.get("tempos_query", [])
    return sum(tempos) / len(tempos) if tempos else 0

# ====================== CAMADA 1: CREDENCIAIS ======================
try:
    url = st.secrets["SUPABASE_URL"]
    anon_key = st.secrets["SUPABASE_KEY"]
    service_key = st.secrets["SUPABASE_SERVICE_KEY"]
    
    supabase = create_client(url, anon_key)
    supabase_admin = create_client(url, service_key)
    supabase.table("sessoes_ativas").select("id", count="exact").limit(1).execute()
except Exception as e:
    st.error(f"❌ Erro de conexão com Supabase: {e}")
    st.stop()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "fgxv4VP0/*")
VIGILANTE_PASSWORD = st.secrets.get("VIGILANTE_PASSWORD", "JOHN123")

# ====================== CONFIGURAÇÃO DA PÁGINA ======================
st.set_page_config(
    page_title="JOHN ACESSOS - CYBER SECURITY 2026",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ====================== CSS FUTURISTA ======================
st.markdown("""<style>
    html, body {margin:0;padding:0;height:100%;width:100%;overflow:hidden;}
    .stApp {transition: background 0.3s ease;height:100%;overflow:auto;}
    header[data-testid="stHeader"] {background:transparent !important;box-shadow:none !important;backdrop-filter:blur(8px);}
    [data-testid="stSidebar"] {background:rgba(10,10,25,0.65)!important;backdrop-filter:blur(16px);}
    .dashboard-card {background:rgba(10,15,30,0.45);backdrop-filter:blur(12px);border-radius:28px;padding:1.2rem 1rem;margin:0.5rem;border:1px solid rgba(0,255,255,0.3);transition:all 0.3s;}
    .dashboard-card:hover {transform:translateY(-6px);border-color:rgba(0,255,255,0.8);}
</style>""", unsafe_allow_html=True)

# ====================== FUNÇÕES ORIGINAIS ======================
def compress_avatar_image(uploaded_file, max_size_kb=200):
    img = Image.open(uploaded_file)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
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

def get_avatar_url():
    padrao_url = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230a0a2a'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-size='10'%3ESEGURANÇA%3C/text%3E%3C/svg%3E"
    try:
        result = supabase.table("app_config").select("value").eq("key", "avatar_url").execute()
        if result.data and result.data[0]['value']:
            return result.data[0]['value']
    except:
        pass
    return padrao_url

def save_avatar_url(url):
    try:
        supabase_admin.table("app_config").upsert({
            "key": "avatar_url",
            "value": url,
            "updated_at": datetime.now().isoformat()
        }).execute()
        st.session_state.avatar_url = url
        return True
    except Exception as e:
        st.error(f"Erro ao salvar avatar: {e}")
        return False

# (Todas as outras funções originais como get_theme_config, apply_theme_css, etc. devem ser mantidas aqui)

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
if "pagina_historico" not in st.session_state:
    st.session_state.pagina_historico = 1
if "ultima_limpeza" not in st.session_state:
    st.session_state.ultima_limpeza = "Nunca"
if "ultima_limpeza_dt" not in st.session_state:
    st.session_state.ultima_limpeza_dt = datetime.now() - timedelta(minutes=40)

st.session_state.theme_config = get_theme_config()
st.session_state.avatar_url = get_avatar_url()

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    # Seu código de login original aqui
    st.stop()

# ====================== APÓS LOGIN ======================
apply_theme_css()

if st.session_state.session_id:
    atualizar_atividade_sessao()
    limpar_sessoes_expiradas()
    total_conectados = contar_sessoes_ativas()
else:
    total_conectados = 0

# ====================== SEU CÓDIGO ORIGINAL CONTINUA AQUI ======================
# (Header, Sidebar, Dashboard, Cadastro, Registro de Entrada, Pessoas Presentes, Histórico, Gestão de Cadastros, etc.)

# ====================== IA AUTÔNOMA DE PERFORMANCE ======================
st.markdown("---")
with st.expander("⚡ IA Autônoma de Performance & Limpeza", expanded=True):
    st.markdown("### 🧹 Sistema Inteligente de Manutenção Automática")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🧠 Status", "Otimizado", "✅")
    with col2:
        st.metric("🔄 Cache Streamlit", "Ativo", "📊")
    with col3:
        st.metric("⏱️ Última Limpeza", st.session_state.get("ultima_limpeza", "Nunca"), "🕒")
    with col4:
        st.metric("Modo IA", "AUTÔNOMO", "🟢")

    st.markdown("---")

    def limpeza_inteligente():
        agora = datetime.now()
        st.session_state.ultima_limpeza = agora.strftime("%H:%M:%S")
        
        st.cache_data.clear()
        st.cache_resource.clear()
        invalidar_cache()
        
        chaves_para_manter = ["logado", "perfil", "session_id", "avatar_url", "theme_config", 
                            "ultima_limpeza", "ultima_limpeza_dt"]
        for chave in list(st.session_state.keys()):
            if chave not in chaves_para_manter and not chave.startswith("_"):
                try:
                    del st.session_state[chave]
                except:
                    pass
        
        gc.collect()
        try:
            limpar_sessoes_expiradas()
        except:
            pass
        return True

    if st.button("🚀 EXECUTAR LIMPEZA TOTAL AGORA", type="primary", use_container_width=True):
        with st.spinner("IA executando limpeza completa..."):
            if limpeza_inteligente():
                st.success("✅ Limpeza completa realizada com sucesso!")
                st.balloons()
                time.sleep(1)
                st.rerun()

    st.markdown("### ⚙️ Configurações de Autonomia da IA")
    col_a, col_b = st.columns(2)
    with col_a:
        auto_cache = st.toggle("🧹 Limpeza Automática de Cache", value=True, key="auto_cache")
    with col_b:
        modo_agressivo = st.toggle("Modo Agressivo", value=False)

    if auto_cache:
        if "ultima_limpeza_dt" not in st.session_state:
            st.session_state.ultima_limpeza_dt = datetime.now() - timedelta(minutes=40)
        tempo_passado = (datetime.now() - st.session_state.ultima_limpeza_dt).total_seconds() / 60
        if tempo_passado > 25:
            with st.spinner("🧠 IA Autônoma realizando manutenção..."):
                limpeza_inteligente()
                st.session_state.ultima_limpeza_dt = datetime.now()
                st.toast("✅ Manutenção automática concluída", icon="⚡")

    if st.button("🔍 Diagnóstico Completo de Performance"):
        with st.spinner("Analisando sistema..."):
            st.info(f"**Chaves em Session State:** {len(st.session_state.keys())}")
            st.info(f"**Cache Hit Ratio:** {cache_estatisticas.get_hit_ratio():.1f}%")
            st.success("✅ Sistema rodando de forma otimizada!")

    st.caption("💡 A IA está monitorando e limpando automaticamente o cache para manter o app sempre liso.")

apply_theme_css()

st.markdown("---")
st.markdown("""
<div class="footer">
    🛡️ JOHN ACESSOS - CYBER SECURITY 2026 | Monitoramento Inteligente & Proteção de Dados
</div>
""", unsafe_allow_html=True)
