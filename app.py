import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import pandas as pd
from PIL import Image
import base64
import re
import uuid
import json
import io
import time
import threading
from queue import Queue
from functools import lru_cache, wraps
from typing import Dict, Any, Optional, List
import hashlib

# ====================== CONFIGURAÇÕES DE PERFORMANCE ======================
CACHE_TTL_PADRAO = 30  # segundos
ITENS_POR_PAGINA = 50  # Paginação no histórico
DEBOUNCE_WAIT_MS = 500  # Milissegundos para debounce

# ====================== FUNÇÃO DE CACHE DECORATOR ======================
class TimedCache:
    """Cache com tempo de vida para consultas frequentes"""
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

# Instâncias de cache
cache_estatisticas = TimedCache(ttl_seconds=30)
cache_pessoas = TimedCache(ttl_seconds=60)
cache_presentes = TimedCache(ttl_seconds=10)

# ====================== FUNÇÃO DE DEBOUNCE ======================
def debounce(wait_time=DEBOUNCE_WAIT_MS):
    """Decorator para debounce de funções de busca"""
    def decorator(func):
        last_call = 0
        last_result = None
        
        def wrapper(*args, **kwargs):
            nonlocal last_call, last_result
            current_time = time.time() * 1000  # milliseconds
            
            if current_time - last_call >= wait_time:
                last_call = current_time
                last_result = func(*args, **kwargs)
                return last_result
            return last_result
        return wrapper
    return decorator

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

# ====================== INICIALIZAÇÃO DE SESSION STATE OTIMIZADA ======================
if "dados" not in st.session_state:
    st.session_state.dados = {
        "logado": False,
        "perfil": "",
        "selected_ids": [],
        "pending_delete_ids": [],
        "pending_clear_all": False,
        "tentativas_login": 0,
        "bloqueado_ate": None,
        "session_id": None,
        "pessoa_confirmada": None,
        "pessoa_saida": None,
        "pagina_historico": 1,
        "ultima_busca": "",
        "ultimo_resultado_busca": None,
        "metricas": {
            "tempo_medio_query": [],
            "cache_hits": 0,
            "cache_misses": 0
        }
    }

# ====================== FUNÇÕES DE PERFORMANCE ======================
def registrar_tempo_query(inicio):
    """Registra tempo de query para métricas"""
    tempo = (time.time() - inicio) * 1000  # em ms
    st.session_state.dados["metricas"]["tempo_medio_query"].append(tempo)
    # Manter apenas últimas 100 medições
    if len(st.session_state.dados["metricas"]["tempo_medio_query"]) > 100:
        st.session_state.dados["metricas"]["tempo_medio_query"] = st.session_state.dados["metricas"]["tempo_medio_query"][-100:]
    return tempo

def get_tempo_medio_query():
    """Retorna tempo médio das queries"""
    tempos = st.session_state.dados["metricas"]["tempo_medio_query"]
    return sum(tempos) / len(tempos) if tempos else 0

def invalidar_cache():
    """Invalida todos os caches após modificações"""
    cache_estatisticas.clear()
    cache_pessoas.clear()
    cache_presentes.clear()

# ====================== FUNÇÕES DE CONSULTA COM CACHE ======================
def get_estatisticas_cached():
    """Retorna estatísticas com cache de 30 segundos"""
    cache_key = "estatisticas"
    cached = cache_estatisticas.get(cache_key)
    if cached:
        return cached
    
    inicio = time.time()
    try:
        presentes = supabase.table("movimentacao").select("id", count="exact").eq("data_saida", "").execute()
        cadastrados = supabase.table("Pessoas").select("id", count="exact").execute()
        setores = supabase.table("movimentacao").select("setor_destino").execute()
        
        setores_unicos = len(set(p['setor_destino'] for p in setores.data)) if setores.data else 11
        
        resultado = {
            "presentes": presentes.count if hasattr(presentes, 'count') else 0,
            "cadastrados": cadastrados.count if hasattr(cadastrados, 'count') else 0,
            "setores_unicos": setores_unicos
        }
        
        registrar_tempo_query(inicio)
        cache_estatisticas.set(cache_key, resultado)
        return resultado
    except Exception as e:
        st.error(f"Erro ao carregar estatísticas: {e}")
        return {"presentes": 0, "cadastrados": 0, "setores_unicos": 11}

@debounce(wait_time=DEBOUNCE_WAIT_MS)
def buscar_pessoa_por_cpf_debounced(cpf):
    """Busca pessoa com debounce para evitar muitas consultas"""
    try:
        pessoa = supabase.table("Pessoas").select("nome, empresa").eq("cpf", cpf).execute()
        return pessoa.data[0] if pessoa.data else None
    except:
        return None

def get_historico_paginado(pagina=1, itens_por_pagina=ITENS_POR_PAGINA):
    """Retorna histórico com paginação"""
    inicio = time.time()
    offset = (pagina - 1) * itens_por_pagina
    
    try:
        # Buscar total de registros
        total = supabase.table("movimentacao").select("id", count="exact").execute()
        total_registros = total.count if hasattr(total, 'count') else 0
        
        # Buscar página atual
        dados = supabase.table("movimentacao")\
            .select("*")\
            .order("id", desc=True)\
            .range(offset, offset + itens_por_pagina - 1)\
            .execute()
        
        registrar_tempo_query(inicio)
        return {
            "dados": dados.data,
            "total": total_registros,
            "pagina": pagina,
            "total_paginas": (total_registros + itens_por_pagina - 1) // itens_por_pagina if total_registros > 0 else 1
        }
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")
        return {"dados": [], "total": 0, "pagina": 1, "total_paginas": 1}

def get_pessoas_cached():
    """Retorna lista de pessoas com cache"""
    cache_key = "pessoas"
    cached = cache_pessoas.get(cache_key)
    if cached:
        return cached
    
    inicio = time.time()
    try:
        pessoas = supabase.table("Pessoas").select("*").order("nome").execute()
        registrar_tempo_query(inicio)
        cache_pessoas.set(cache_key, pessoas.data)
        return pessoas.data
    except:
        return []

def get_presentes_cached():
    """Retorna lista de pessoas presentes com cache"""
    cache_key = "presentes"
    cached = cache_presentes.get(cache_key)
    if cached:
        return cached
    
    inicio = time.time()
    try:
        presentes = supabase.table("movimentacao").select("*").eq("data_saida", "").execute()
        registrar_tempo_query(inicio)
        cache_presentes.set(cache_key, presentes.data)
        return presentes.data
    except:
        return []

def excluir_multiplos_registros(ids, tabela="movimentacao"):
    """Exclui múltiplos registros em lote"""
    if not ids:
        return {"sucesso": False, "mensagem": "Nenhum ID para excluir"}
    
    inicio = time.time()
    try:
        # Exclusão em lote - uma única query
        supabase_admin.table(tabela).delete().in_("id", ids).execute()
        registrar_tempo_query(inicio)
        invalidar_cache()
        return {"sucesso": True, "mensagem": f"{len(ids)} registro(s) excluído(s)"}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro: {e}"}

def otimizar_banco():
    """Limpa dados antigos e otimiza (opcional)"""
    try:
        # Remover movimentações com mais de 1 ano (opcional - comentado por padrão)
        # data_limite = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        # supabase_admin.table("movimentacao").delete().lt("data_entrada", data_limite).execute()
        
        # Invalidar cache após otimização
        invalidar_cache()
        return {"sucesso": True, "mensagem": "Otimização concluída"}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro: {e}"}

# ====================== CSS FUTURISTA ======================
st.markdown("""
<style>
    /* RESET E BACKGROUND */
    html, body, .stApp {
        margin: 0;
        padding: 0;
        height: 100%;
    }
    .stApp {
        background: radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);
        overflow: auto;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(0, 255, 255, 0.2);
    }
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 25, 0.65) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(0, 255, 255, 0.3);
    }
    .dashboard-card {
        background: rgba(10, 15, 30, 0.45);
        backdrop-filter: blur(12px);
        border-radius: 28px;
        padding: 1.2rem;
        margin: 0.5rem;
        border: 1px solid rgba(0, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-6px);
        border-color: rgba(0, 255, 255, 0.8);
        box-shadow: 0 0 25px cyan;
    }
    .card-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, cyan);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    .stButton>button {
        background: rgba(0,20,40,0.7) !important;
        border: 1px solid #0ff !important;
        border-radius: 40px !important;
        color: #0ff !important;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background: rgba(0,255,255,0.15) !important;
        border-color: magenta !important;
        color: magenta !important;
        transform: scale(1.02);
    }
    .footer {
        text-align: center;
        padding: 15px;
        color: #6b7280;
        font-size: 9px;
        border-top: 1px solid rgba(0,255,255,0.2);
        margin-top: 25px;
    }
    .metric-card {
        background: rgba(0,0,0,0.3);
        border-radius: 15px;
        padding: 10px;
        text-align: center;
        border: 1px solid rgba(0,255,255,0.2);
    }
    .pagination {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ====================== FUNÇÕES AVATAR E TEMA ======================
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
        if buffer.tell() / 1024 <= max_size_kb or quality <= 20:
            break
        quality -= 10
    return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"

def get_avatar_url():
    padrao = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230a0a2a'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-size='10'%3ESEGURANÇA%3C/text%3E%3C/svg%3E"
    try:
        result = supabase.table("app_config").select("value").eq("key", "avatar_url").execute()
        if result.data and result.data[0]['value']:
            return result.data[0]['value']
    except:
        pass
    return padrao

def save_avatar_url(url):
    try:
        supabase_admin.table("app_config").upsert({
            "key": "avatar_url", "value": url, "updated_at": datetime.now().isoformat()
        }).execute()
        return True
    except:
        return False

# ====================== FUNÇÕES DE SESSÃO ======================
def registrar_sessao(perfil, usuario="admin"):
    session_id = str(uuid.uuid4())
    try:
        supabase_admin.table("sessoes_ativas").insert({
            "id": session_id, "usuario": usuario, "perfil": perfil,
            "ultima_atividade": datetime.now().isoformat(), "ip": "desconhecido", "user_agent": "streamlit"
        }).execute()
        st.session_state.dados["session_id"] = session_id
        return True
    except:
        return False

def remover_sessao():
    if st.session_state.dados.get("session_id"):
        try:
            supabase_admin.table("sessoes_ativas").delete().eq("id", st.session_state.dados["session_id"]).execute()
        except:
            pass
        st.session_state.dados["session_id"] = None

def contar_sessoes_ativas():
    try:
        limite = (datetime.now() - timedelta(minutes=5)).isoformat()
        result = supabase.table("sessoes_ativas").select("id", count="exact").gte("ultima_atividade", limite).execute()
        return result.count
    except:
        return 0

def require_admin():
    if st.session_state.dados.get("perfil") != "ADMIN":
        st.error("❌ Ação restrita a administradores.")
        st.stop()

# ====================== FUNÇÕES DE RELATÓRIOS ======================
def gerar_html_impressao(df, titulo):
    if df.empty:
        return None
    colunas = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida']
    colunas_existentes = [c for c in colunas if c in df.columns]
    df_rel = df[colunas_existentes].copy().fillna('')
    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>{titulo}</title>
    <style>
        body{{font-family:Arial;margin:2cm;}}
        h1{{text-align:center;color:#0a2b3e;}}
        table{{width:100%;border-collapse:collapse;}}
        th,td{{border:1px solid #ccc;padding:8px;text-align:left;}}
        th{{background:#0a2b3e;color:white;}}
    </style></head>
    <body>
        <h1>JOHN ACESSOS - {titulo}</h1>
        <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        {df_rel.to_html(escape=True, index=False)}
        <button onclick="window.print();">🖨️ Imprimir</button>
    </body></html>
    """

def validar_cpf(cpf):
    cpf_limpo = re.sub(r'\D', '', cpf)
    return cpf_limpo.isdigit() and len(cpf_limpo) == 11

def sanitizar_cpf(cpf):
    return re.sub(r'\D', '', cpf)

def sanitizar_texto(texto):
    if not texto:
        return texto
    return texto.replace('<', '&lt;').replace('>', '&gt;')

# ====================== TELA DE LOGIN ======================
if not st.session_state.dados.get("logado", False):
    st.markdown('<style>.stApp{background:radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);}</style>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 48px;">🛡️</div>
                <h1 style="color: #0ff;">JOHN ACESSOS</h1>
                <p style="color: #a78bfa;">CYBER SECURITY 2026</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.text_input("", placeholder="Usuário", key="login_user", label_visibility="collapsed")
            senha = st.text_input("", type="password", placeholder="Senha", label_visibility="collapsed")
            if st.form_submit_button("🛡️ ACESSAR", use_container_width=True):
                if senha == ADMIN_PASSWORD:
                    st.session_state.dados["logado"] = True
                    st.session_state.dados["perfil"] = "ADMIN"
                    registrar_sessao("ADMIN", "admin")
                    st.rerun()
                elif senha == VIGILANTE_PASSWORD:
                    st.session_state.dados["logado"] = True
                    st.session_state.dados["perfil"] = "VIGILANTE"
                    registrar_sessao("VIGILANTE", "vigilante")
                    st.rerun()
                else:
                    st.error("❌ ACESSO NEGADO")
    st.stop()

# ====================== HEADER ======================
avatar_url = get_avatar_url()
total_conectados = contar_sessoes_ativas()

st.markdown(f"""
<div style="background: rgba(8,8,20,0.6); backdrop-filter: blur(8px); border-radius: 20px; padding: 10px 20px; margin-bottom: 20px; border: 1px solid cyan;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; gap:15px; align-items:center;">
            <img src="{avatar_url}" style="width:45px; height:45px; border-radius:50%; border:1px solid cyan;">
            <div><h1 style="margin:0;font-size:18px; color:cyan;">JOHN ACESSOS - CYBER SECURITY 2026</h1></div>
        </div>
        <div style="display:flex; gap:15px;">
            <span style="color:#0f0;">● LIVE</span>
            <span>👥 {total_conectados}</span>
            <span style="background:linear-gradient(135deg,cyan,magenta); padding:2px 10px; border-radius:20px;">{st.session_state.dados['perfil']}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([6,1,1,1])
with col3:
    if st.button("🔄 ATUALIZAR"):
        invalidar_cache()
        st.rerun()
with col4:
    if st.button("🚪 SAIR"):
        remover_sessao()
        st.session_state.dados["logado"] = False
        st.rerun()

# ====================== DASHBOARD COM MÉTRICAS DE PERFORMANCE ======================
stats = get_estatisticas_cached()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-value">{stats['presentes']}</div>
        <div>PRESENTES</div>
        <small>🟢 ONLINE</small>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-value">{stats['cadastrados']}</div>
        <div>CADASTRADOS</div>
        <small>📋 BASE</small>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-value">{stats['setores_unicos']}</div>
        <div>SETORES</div>
        <small>📍 ATIVOS</small>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-value">ATIVA</div>
        <div>SEGURANÇA</div>
        <small>🛡️ 24/7</small>
    </div>
    """, unsafe_allow_html=True)

# ====================== MÉTRICAS DE PERFORMANCE ======================
with st.expander("📊 Métricas de Performance", expanded=False):
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("⏱️ Tempo médio query", f"{get_tempo_medio_query():.0f}ms")
    with col_m2:
        hit_ratio = cache_estatisticas.get_hit_ratio()
        st.metric("🎯 Cache hit ratio", f"{hit_ratio:.0f}%")
    with col_m3:
        total_cached = len(cache_estatisticas.cache_data) + len(cache_pessoas.cache_data) + len(cache_presentes.cache_data)
        st.metric("💾 Registros em cache", total_cached)
    with col_m4:
        st.metric("📄 Itens por página", ITENS_POR_PAGINA)
    
    # Gráfico simples de performance
    st.markdown("---")
    st.markdown("**📈 Histórico de tempo de queries (últimas 100)**")
    tempos = st.session_state.dados["metricas"]["tempo_medio_query"][-20:]
    if tempos:
        df_tempos = pd.DataFrame({"Tempo (ms)": tempos})
        st.line_chart(df_tempos)

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
                    existe = supabase.table("Pessoas").select("id").eq("cpf", cpf_limpo).execute().data
                    if existe:
                        st.error("❌ Pessoa já cadastrada")
                    else:
                        supabase.table("Pessoas").insert({
                            "cpf": cpf_limpo,
                            "nome": sanitizar_texto(novo_nome).strip().upper(),
                            "empresa": sanitizar_texto(novo_empresa).strip().upper() if novo_empresa else ""
                        }).execute()
                        invalidar_cache()
                        st.success("✅ Cadastro salvo!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.error("CPF e Nome obrigatórios.")

# ====================== REGISTRO DE ENTRADA ======================
st.markdown("---")
st.markdown("### 📋 Registrar Movimentação")

tipo = st.radio("👥 Tipo de Pessoa:", ["🏢 Prestador de serviços", "🔧 Terceirizados"], horizontal=True)
if tipo == "🏢 Prestador de serviços":
    destinos = ["🏥 C.C", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção"]
else:
    destinos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

col_cpf, col_btn = st.columns([3,1])
with col_cpf:
    cpf_input = st.text_input("📄 CPF:", key="cpf_entrada", placeholder="Digite o CPF", 
                              on_change=lambda: setattr(st.session_state, 'buscar_cpf', True))
with col_btn:
    if cpf_input:
        if st.button("✅ CONFIRMAR CPF", key="confirma_cpf"):
            cpf_limpo = sanitizar_cpf(cpf_input)
            if not validar_cpf(cpf_limpo):
                st.error("CPF inválido")
            else:
                pessoa = buscar_pessoa_por_cpf_debounced(cpf_limpo)
                if pessoa:
                    st.session_state.dados["pessoa_confirmada"] = {
                        "cpf": cpf_limpo, 
                        "nome": pessoa['nome'], 
                        "empresa": pessoa.get('empresa', '')
                    }
                    st.success(f"✅ {pessoa['nome']}")
                else:
                    st.error("CPF não cadastrado")
                    st.session_state.dados["pessoa_confirmada"] = None

setor_escolhido = st.selectbox("📍 Destino:", destinos, key="destino")

if st.button("✅ Registrar Entrada", key="btn_entrada", type="primary"):
    if st.session_state.dados.get("pessoa_confirmada"):
        p = st.session_state.dados["pessoa_confirmada"]
        try:
            supabase.table("movimentacao").insert({
                "cpf": p['cpf'], "nome": p['nome'], "empresa": p['empresa'],
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "data_saida": ""
            }).execute()
            invalidar_cache()
            st.success(f"Entrada registrada!")
            st.session_state.dados["pessoa_confirmada"] = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Confirme o CPF primeiro.")

# ====================== PESSOAS PRESENTES (LAZY LOADING) ======================
st.markdown("---")
st.markdown("### 📍 Pessoas Presentes")

# Lazy loading - carregar apenas a aba ativa
aba_selecionada = st.radio("Selecione a visualização:", 
                           ["📊 Todos", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"],
                           horizontal=True)

presentes = get_presentes_cached()

if presentes:
    # Filtrar baseado na aba selecionada
    if aba_selecionada == "🏥 C.C":
        presentes_filtrados = [p for p in presentes if "C.C" in p['setor_destino']]
    elif aba_selecionada == "🔧 GRSA":
        presentes_filtrados = [p for p in presentes if "GRSA" in p['setor_destino']]
    elif aba_selecionada == "🏭 Brasanitas":
        presentes_filtrados = [p for p in presentes if "Brasanitas" in p['setor_destino']]
    else:
        presentes_filtrados = presentes
    
    for p in presentes_filtrados[:20]:  # Limitar exibição para performance
        col1, col2, col3, col4 = st.columns([4,3,2,2])
        col1.write(f"**{p['nome']}**")
        col2.write(f"📍 {p['setor_destino']}")
        col3.write(f"🏢 {p.get('empresa','N/A')}")
        if col4.button("🚪 Saída", key=f"saida_{p['id']}"):
            try:
                supabase.table("movimentacao").update({
                    "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }).eq("id", p['id']).execute()
                invalidar_cache()
                st.rerun()
            except:
                pass
        st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
    
    if len(presentes_filtrados) > 20:
        st.info(f"📌 Mostrando 20 de {len(presentes_filtrados)} registros. Use a busca para filtrar.")
else:
    st.info("Nenhuma pessoa presente no momento")

# ====================== HISTÓRICO COM PAGINAÇÃO ======================
st.markdown("---")
with st.expander("🕒 Histórico Completo de Movimentações", expanded=True):
    # Controles de paginação
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if st.button("◀ ANTERIOR", key="pag_anterior"):
            if st.session_state.dados.get("pagina_historico", 1) > 1:
                st.session_state.dados["pagina_historico"] -= 1
                st.rerun()
    
    with col_page:
        pagina_atual = st.session_state.dados.get("pagina_historico", 1)
        st.markdown(f"<div style='text-align:center'>Página {pagina_atual}</div>", unsafe_allow_html=True)
    
    with col_next:
        if st.button("PRÓXIMO ▶", key="pag_proximo"):
            historico_data = get_historico_paginado(pagina_atual + 1)
            if pagina_atual < historico_data["total_paginas"]:
                st.session_state.dados["pagina_historico"] += 1
                st.rerun()
    
    # Carregar dados da página atual
    historico = get_historico_paginado(pagina_atual)
    
    if historico["dados"]:
        df = pd.DataFrame(historico["dados"])
        
        st.markdown(f"**Total de registros:** {historico['total']} | **Página {historico['pagina']} de {historico['total_paginas']}**")
        
        # Relatórios
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("📑 Relatório completo", key="relatorio_completo"):
                html = gerar_html_impressao(df, "RELATÓRIO COMPLETO")
                if html:
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir relatório</a>', unsafe_allow_html=True)
        
        with col_r2:
            if st.button("📑 Consolidado", key="relatorio_consolidado"):
                html = gerar_html_impressao(df, "RELATÓRIO CONSOLIDADO")
                if html:
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir consolidado</a>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🗑️ Exclusão de Registros (APENAS ADMIN)")
        
        # Seleção em lote
        if st.session_state.dados.get("perfil") == "ADMIN":
            selecionar_todos = st.checkbox("✅ Selecionar todos da página")
            ids_pagina = [row['id'] for row in historico["dados"]]
            
            if selecionar_todos:
                for id_ in ids_pagina:
                    if id_ not in st.session_state.dados["selected_ids"]:
                        st.session_state.dados["selected_ids"].append(id_)
            else:
                for id_ in ids_pagina:
                    if id_ in st.session_state.dados["selected_ids"]:
                        st.session_state.dados["selected_ids"].remove(id_)
        
        # Listar registros
        for row in historico["dados"]:
            col_check, col_data = st.columns([0.5, 9.5])
            with col_check:
                if st.session_state.dados.get("perfil") == "ADMIN":
                    checked = st.checkbox("", key=f"chk_{row['id']}", 
                                         value=row['id'] in st.session_state.dados["selected_ids"])
                    if checked and row['id'] not in st.session_state.dados["selected_ids"]:
                        st.session_state.dados["selected_ids"].append(row['id'])
                    elif not checked and row['id'] in st.session_state.dados["selected_ids"]:
                        st.session_state.dados["selected_ids"].remove(row['id'])
            with col_data:
                st.markdown(f"ID {row['id']} - {row['nome']} | CPF: {row['cpf']} | Empresa: {row.get('empresa','N/A')} | Entrada: {row['data_entrada']} | Saída: {row['data_saida'] or 'Presente'}")
        
        # Botões de exclusão em lote
        if st.session_state.dados.get("perfil") == "ADMIN" and st.session_state.dados["selected_ids"]:
            st.warning(f"⚠️ {len(st.session_state.dados['selected_ids'])} registro(s) selecionado(s)")
            col_excluir, col_cancelar = st.columns(2)
            with col_excluir:
                if st.button("🗑️ EXCLUIR SELECIONADOS", key="excluir_lote"):
                    resultado = excluir_multiplos_registros(st.session_state.dados["selected_ids"])
                    if resultado["sucesso"]:
                        st.success(resultado["mensagem"])
                        st.session_state.dados["selected_ids"] = []
                        invalidar_cache()
                        st.rerun()
                    else:
                        st.error(resultado["mensagem"])
            with col_cancelar:
                if st.button("❌ CANCELAR", key="cancelar_excluir_lote"):
                    st.session_state.dados["selected_ids"] = []
                    st.rerun()
    else:
        st.info("Nenhum registro encontrado.")

# ====================== GESTÃO DE CADASTROS COM OTIMIZAÇÕES ======================
st.markdown("---")
if st.session_state.dados.get("perfil") == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        # Ferramentas administrativas
        col_ferr1, col_ferr2 = st.columns(2)
        
        with col_ferr1:
            st.markdown("### 🗑️ Limpeza de Duplicados")
            pessoas = get_pessoas_cached()
            if pessoas:
                df_pessoas = pd.DataFrame(pessoas)
                duplicados = df_pessoas[df_pessoas.duplicated(subset=['cpf'], keep=False)]
                if not duplicados.empty:
                    st.warning(f"⚠️ {len(duplicados)} registros duplicados encontrados")
                    if st.button("🗑️ REMOVER DUPLICADOS", key="remover_duplicados"):
                        with st.spinner("Processando..."):
                            # Agrupar por CPF e manter apenas o primeiro
                            cpfs_unicos = {}
                            for p in pessoas:
                                if p['cpf'] not in cpfs_unicos:
                                    cpfs_unicos[p['cpf']] = p
                                else:
                                    supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                            invalidar_cache()
                            st.success("Duplicados removidos!")
                            st.rerun()
                else:
                    st.success("✅ Nenhum duplicado encontrado")
        
        with col_ferr2:
            st.markdown("### 🔄 Otimização do Banco")
            if st.button("🧹 OTIMIZAR BANCO", key="otimizar_banco"):
                with st.spinner("Otimizando..."):
                    resultado = otimizar_banco()
                    if resultado["sucesso"]:
                        st.success(resultado["mensagem"])
                    else:
                        st.error(resultado["mensagem"])
        
        st.markdown("---")
        
        # Listagem de cadastros (com lazy loading por aba)
        tab1, tab2, tab3 = st.tabs(["🏭 BRASANITAS", "🔧 GRSA", "🏢 PRESTADORES"])
        
        with tab1:
            br = [p for p in pessoas if p.get('empresa', '').upper() == "BRASANITAS"]
            for p in br[:50]:  # Limitar exibição
                cols = st.columns([3,2,1,1])
                cols[0].write(f"**{p['nome']}**")
                cols[1].write(f"CPF: {p['cpf']}")
                with cols[2]:
                    if st.button("✏️", key=f"edit_br_{p['id']}"):
                        st.session_state[f"editando_{p['id']}"] = True
                with cols[3]:
                    if st.button("🗑️", key=f"del_br_{p['id']}"):
                        supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                        invalidar_cache()
                        st.rerun()
                
                if st.session_state.get(f"editando_{p['id']}"):
                    with st.form(key=f"form_edit_{p['id']}"):
                        novo_nome = st.text_input("Nome", p['nome'])
                        novo_cpf = st.text_input("CPF", p['cpf'])
                        nova_emp = st.text_input("Empresa", p.get('empresa', ''))
                        if st.form_submit_button("Salvar"):
                            supabase_admin.table("Pessoas").update({
                                "nome": novo_nome.upper(),
                                "cpf": sanitizar_cpf(novo_cpf),
                                "empresa": nova_emp.upper()
                            }).eq("id", p['id']).execute()
                            invalidar_cache()
                            st.session_state[f"editando_{p['id']}"] = False
                            st.rerun()
                st.divider()
        
        with tab2:
            gr = [p for p in pessoas if p.get('empresa', '').upper() == "GRSA"]
            for p in gr[:50]:
                cols = st.columns([3,2,1,1])
                cols[0].write(f"**{p['nome']}**")
                cols[1].write(f"CPF: {p['cpf']}")
                with cols[2]:
                    if st.button("✏️", key=f"edit_gr_{p['id']}"):
                        st.session_state[f"editando_{p['id']}"] = True
                with cols[3]:
                    if st.button("🗑️", key=f"del_gr_{p['id']}"):
                        supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                        invalidar_cache()
                        st.rerun()
                
                if st.session_state.get(f"editando_{p['id']}"):
                    with st.form(key=f"form_edit_gr_{p['id']}"):
                        novo_nome = st.text_input("Nome", p['nome'])
                        novo_cpf = st.text_input("CPF", p['cpf'])
                        nova_emp = st.text_input("Empresa", p.get('empresa', ''))
                        if st.form_submit_button("Salvar"):
                            supabase_admin.table("Pessoas").update({
                                "nome": novo_nome.upper(),
                                "cpf": sanitizar_cpf(novo_cpf),
                                "empresa": nova_emp.upper()
                            }).eq("id", p['id']).execute()
                            invalidar_cache()
                            st.session_state[f"editando_{p['id']}"] = False
                            st.rerun()
                st.divider()
        
        with tab3:
            prestadores = [p for p in pessoas if p.get('empresa', '').upper() not in ["BRASANITAS", "GRSA"]]
            search = st.text_input("🔍 Pesquisar", key="search_prestadores")
            if search:
                prestadores = [p for p in prestadores if search.lower() in p['nome'].lower() or search.lower() in p['cpf']]
            
            for p in prestadores[:50]:
                cols = st.columns([2,2,2,1,1])
                cols[0].write(f"**{p['nome']}**")
                cols[1].write(f"CPF: {p['cpf']}")
                cols[2].write(f"Empresa: {p.get('empresa','N/A')}")
                with cols[3]:
                    if st.button("✏️", key=f"edit_pre_{p['id']}"):
                        st.session_state[f"editando_{p['id']}"] = True
                with cols[4]:
                    if st.button("🗑️", key=f"del_pre_{p['id']}"):
                        supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                        invalidar_cache()
                        st.rerun()
                
                if st.session_state.get(f"editando_{p['id']}"):
                    with st.form(key=f"form_edit_pre_{p['id']}"):
                        novo_nome = st.text_input("Nome", p['nome'])
                        novo_cpf = st.text_input("CPF", p['cpf'])
                        nova_emp = st.text_input("Empresa", p.get('empresa', ''))
                        if st.form_submit_button("Salvar"):
                            supabase_admin.table("Pessoas").update({
                                "nome": novo_nome.upper(),
                                "cpf": sanitizar_cpf(novo_cpf),
                                "empresa": nova_emp.upper()
                            }).eq("id", p['id']).execute()
                            invalidar_cache()
                            st.session_state[f"editando_{p['id']}"] = False
                            st.rerun()
                st.divider()

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
<div class="footer">
    🛡️ JOHN ACESSOS - CYBER SECURITY 2026 | Monitoramento Inteligente & Proteção de Dados
    <br>
    <small>⚡ Cache ativo | 📄 Paginação: {} itens/página | 🎯 Hit ratio: {:.0f}%</small>
</div>
""".format(ITENS_POR_PAGINA, cache_estatisticas.get_hit_ratio()), unsafe_allow_html=True)
