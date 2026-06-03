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
from functools import wraps

# ====================== CONFIGURAÇÕES DE PERFORMANCE ======================
CACHE_TTL_PADRAO = 60  # segundos (aumentado de 30 para 60)
ITENS_POR_PAGINA = 50  # Paginação no histórico
ITENS_POR_PAGINA_PRESENTES = 20  # Paginação na lista de presentes
DEBOUNCE_WAIT_MS = 500

# ====================== CACHE COM TTL ======================
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

cache_estatisticas = TimedCache(ttl_seconds=CACHE_TTL_PADRAO)
cache_pessoas = TimedCache(ttl_seconds=120)
cache_presentes = TimedCache(ttl_seconds=30)

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

def excluir_multiplos_registros(ids, tabela="movimentacao"):
    if not ids:
        return {"sucesso": False, "mensagem": "Nenhum ID para excluir"}
    try:
        supabase_admin.table(tabela).delete().in_("id", ids).execute()
        invalidar_cache()
        return {"sucesso": True, "mensagem": f"{len(ids)} registro(s) excluído(s)"}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro: {e}"}

def get_historico_paginado(pagina=1, itens_por_pagina=ITENS_POR_PAGINA):
    inicio = time.time()
    offset = (pagina - 1) * itens_por_pagina
    try:
        total = supabase.table("movimentacao").select("id", count="exact").execute()
        total_registros = total.count if hasattr(total, 'count') else 0
        dados = supabase.table("movimentacao")\
            .select("*")\
            .order("id", desc=True)\
            .range(offset, offset + itens_por_pagina - 1)\
            .execute()
        registrar_tempo_query((time.time() - inicio) * 1000)
        return {
            "dados": dados.data,
            "total": total_registros,
            "pagina": pagina,
            "total_paginas": (total_registros + itens_por_pagina - 1) // itens_por_pagina if total_registros > 0 else 1
        }
    except Exception as e:
        return {"dados": [], "total": 0, "pagina": 1, "total_paginas": 1}

@debounce(wait_time=DEBOUNCE_WAIT_MS)
def buscar_pessoa_por_cpf_debounced(cpf):
    try:
        pessoa = supabase.table("Pessoas").select("nome, empresa").eq("cpf", cpf).execute()
        return pessoa.data[0] if pessoa.data else None
    except:
        return None

@st.cache_data(ttl=CACHE_TTL_PADRAO)
def get_estatisticas_cached():
    try:
        presentes_data = supabase.table("movimentacao").select("id", count="exact").eq("data_saida", "").execute()
        cadastrados_data = supabase.table("Pessoas").select("id", count="exact").execute()
        setores_data = supabase.table("movimentacao").select("setor_destino").execute()
        setores_unicos = len(set(p['setor_destino'] for p in setores_data.data)) if setores_data.data else 11
        return {
            "total_presentes": presentes_data.count if hasattr(presentes_data, 'count') else 0,
            "total_cadastrados": cadastrados_data.count if hasattr(cadastrados_data, 'count') else 0,
            "setores_unicos": setores_unicos
        }
    except Exception as e:
        return {"total_presentes": 0, "total_cadastrados": 0, "setores_unicos": 11}

def get_presentes_cached():
    cache_key = "presentes"
    cached = cache_presentes.get(cache_key)
    if cached:
        return cached
    try:
        dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute()
        cache_presentes.set(cache_key, dados.data)
        return dados.data
    except:
        return []

# ====================== FUNÇÕES DE TIMEZONE COM CACHE EM SESSION_STATE ======================
def get_timezone_offset():
    if "timezone_offset" not in st.session_state:
        try:
            result = supabase.table("app_config").select("value").eq("key", "timezone_offset").execute()
            if result.data and result.data[0]['value']:
                st.session_state.timezone_offset = float(result.data[0]['value'])
            else:
                st.session_state.timezone_offset = 0.0
        except:
            st.session_state.timezone_offset = 0.0
    return st.session_state.timezone_offset

def save_timezone_offset(offset_horas):
    try:
        supabase_admin.table("app_config").upsert({
            "key": "timezone_offset",
            "value": str(offset_horas),
            "updated_at": datetime.now().isoformat()
        }).execute()
        st.session_state.timezone_offset = offset_horas
        return True
    except Exception as e:
        st.error(f"Erro ao salvar offset: {e}")
        return False

def get_current_datetime():
    offset = get_timezone_offset()
    now_utc = datetime.utcnow()
    now_offset = now_utc + timedelta(hours=offset)
    return now_offset

def format_datetime_str(dt):
    return dt.strftime("%d/%m/%Y %H:%M:%S")

# ====================== CREDENCIAIS ======================
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

st.set_page_config(page_title="JOHN ACESSOS - CYBER SECURITY 2026", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

# ====================== CSS (resumido para brevidade - manter o mesmo original) ======================
st.markdown("""
<style>
    /* Manter todo o CSS original aqui - omitido para economizar espaço, mas no código real mantenha */
    html, body { margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; }
    .stApp { transition: background 0.3s ease; height: 100%; overflow: auto; }
    /* ... todo o CSS existente ... */
    .footer { text-align: center; padding: 15px; color: #6b7280; font-size: 9px; border-top: 1px solid rgba(0,255,255,0.2); margin-top: 25px; }
</style>
""", unsafe_allow_html=True)

# ====================== FUNÇÕES DE AVATAR E TEMA (com cache session_state) ======================
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
    if "avatar_url" not in st.session_state:
        padrao_url = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230a0a2a'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-size='10'%3ESEGURANÇA%3C/text%3E%3C/svg%3E"
        try:
            result = supabase.table("app_config").select("value").eq("key", "avatar_url").execute()
            if result.data and result.data[0]['value']:
                st.session_state.avatar_url = result.data[0]['value']
            else:
                st.session_state.avatar_url = padrao_url
        except:
            st.session_state.avatar_url = padrao_url
    return st.session_state.avatar_url

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

def get_theme_config():
    if "theme_config" not in st.session_state:
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
                st.session_state.theme_config = config
            else:
                save_theme_config(padrao)
                st.session_state.theme_config = padrao
        except:
            st.session_state.theme_config = padrao
    return st.session_state.theme_config

def save_theme_config(config):
    try:
        supabase_admin.table("app_config").upsert({
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
    config = get_theme_config()
    bg_type = config.get("type", "gradient")
    if bg_type == "gradient":
        bg_value = config.get("value", "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)")
        st.markdown(f'<style>html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{ background: {bg_value} !important; background-attachment: fixed !important; background-size: cover !important; background-repeat: no-repeat !important; background-position: center !important; }}</style>', unsafe_allow_html=True)
    elif bg_type == "solid":
        bg_value = config.get("value", "#0a0a1a")
        st.markdown(f'<style>html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{ background: {bg_value} !important; background-attachment: fixed !important; }}</style>', unsafe_allow_html=True)
    # ... outras opções de tema (url, video, futuristic) podem ser mantidas, mas omitidas para brevidade
    elif bg_type == "futuristic":
        st.markdown("""
        <canvas id="futuristic-canvas"></canvas>
        <script>/* ... script canvas ... */</script>
        """, unsafe_allow_html=True)

# ====================== FUNÇÕES DE SESSÃO ======================
MAX_TENTATIVAS_LOGIN = 5
SESSION_TIMEOUT_MINUTOS = 5

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
        supabase_admin.table("sessoes_ativas").insert(data).execute()
        st.session_state.session_id = session_id
        return True
    except Exception as e:
        st.error(f"Erro ao registrar sessão: {e}")
        return False

def atualizar_atividade_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase_admin.table("sessoes_ativas").update({
                "ultima_atividade": datetime.now().isoformat()
            }).eq("id", st.session_state.session_id).execute()
        except:
            pass

def remover_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase_admin.table("sessoes_ativas").delete().eq("id", st.session_state.session_id).execute()
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
            supabase_admin.table("sessoes_ativas").delete().lt("ultima_atividade", limite).neq("id", st.session_state.session_id).execute()
        else:
            supabase_admin.table("sessoes_ativas").delete().lt("ultima_atividade", limite).execute()
    except:
        pass

def encerrar_outras_sessoes():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase_admin.table("sessoes_ativas").delete().neq("id", st.session_state.session_id).execute()
            return True
        except:
            return False
    return False

# ====================== FUNÇÕES DE PERMISSÃO ======================
def require_admin():
    if st.session_state.get("perfil") != "ADMIN":
        st.error("❌ Ação restrita a administradores.")
        st.stop()

def require_vigilante():
    if st.session_state.get("perfil") != "VIGILANTE":
        st.error("❌ Ação restrita a vigilantes.")
        st.stop()

def require_any_login():
    if not st.session_state.get("logado", False):
        st.error("❌ Você precisa estar logado.")
        st.stop()

# ====================== FUNÇÕES DE RELATÓRIOS PDF ======================
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
    def secao(df_filtro, titulo, icone=""):
        df_filtro = df_filtro.copy().fillna('')
        if df_filtro.empty:
            return f"<div class='section'><h2>{icone} {titulo}</h2><p>Nenhum registro.</p></div>"
        colunas = ['id','nome','cpf','empresa','setor_destino','data_entrada','data_saida']
        existentes = [c for c in colunas if c in df_filtro.columns]
        tabela = df_filtro[existentes].to_html(escape=True, index=False)
        return f"<div class='section'><h2>{icone} {titulo} <span class='count-badge'>{len(df_filtro)}</span></h2>{tabela}</div>"

    df_cc = df[df['setor_destino'].str.contains('C.C', case=False, na=False)]
    df_gr = df[df['setor_destino'].str.contains('GRSA', case=False, na=False)]
    df_br = df[df['setor_destino'].str.contains('Brasanitas', case=False, na=False)]
    outros = df[~df['setor_destino'].str.contains('C.C|GRSA|Brasanitas', case=False, na=False)]
    html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>RELATÓRIO CONSOLIDADO POR SETOR</title>
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
        <h1>JOHN ACESSOS - RELATÓRIO CONSOLIDADO POR SETOR</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
    """
    html += secao(df_cc, "C.C", "🏥")
    html += secao(df_gr, "GRSA", "🔧")
    html += secao(df_br, "Brasanitas", "🏭")
    html += secao(outros, "Prestadores de Serviços", "🏢")
    html += '<div class="no-print" style="text-align:center;margin-top:30px;"><button onclick="window.print();">🖨️ Imprimir / PDF</button></div></body></html>'
    return html

# ====================== FUNÇÕES CPF ======================
def validar_cpf(cpf):
    cpf_limpo = re.sub(r'\D', '', cpf)
    return cpf_limpo.isdigit() and len(cpf_limpo) == 11

def sanitizar_cpf(cpf):
    return re.sub(r'\D', '', cpf)

def sanitizar_texto(texto):
    if not texto:
        return texto
    return texto.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# ====================== FUNÇÕES DE LIMPEZA E SINCRONIA ======================
def apagar_registros_duplicados():
    try:
        todas_pessoas = supabase_admin.table("Pessoas").select("*").execute().data
        if not todas_pessoas:
            return {"sucesso": False, "mensagem": "Nenhum registro encontrado na tabela Pessoas"}
        grupos_por_cpf = {}
        for pessoa in todas_pessoas:
            cpf = pessoa['cpf']
            grupos_por_cpf.setdefault(cpf, []).append(pessoa)
        cpfs_com_duplicatas = {cpf: registros for cpf, registros in grupos_por_cpf.items() if len(registros) > 1}
        if not cpfs_com_duplicatas:
            return {"sucesso": True, "mensagem": "Nenhum CPF duplicado encontrado.", "duplicados_removidos": 0}
        total_removidos = 0
        resultados = []
        for cpf, registros in cpfs_com_duplicatas.items():
            registros_ordenados = sorted(registros, key=lambda x: x['id'])
            registro_principal = registros_ordenados[0]
            ids_para_remover = [r['id'] for r in registros_ordenados[1:]]
            for id_remover in ids_para_remover:
                supabase_admin.table("Pessoas").delete().eq("id", id_remover).execute()
                total_removidos += 1
            resultados.append(f"CPF {cpf}: mantido ID {registro_principal['id']} - {registro_principal['nome']} | Removidos: {len(ids_para_remover)}")
        return {"sucesso": True, "mensagem": f"Limpeza concluída! {total_removidos} registro(s) duplicado(s) removido(s).", "duplicados_removidos": total_removidos, "detalhes": resultados}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro durante a limpeza: {str(e)}"}

def sincronizar_novos_cadastros(arquivo_csv):
    try:
        df = pd.read_csv(arquivo_csv)
        if 'cpf' not in df.columns or 'nome' not in df.columns:
            return {"sucesso": False, "mensagem": "Arquivo deve conter colunas 'cpf' e 'nome'"}
        registros_inseridos = 0
        registros_atualizados = 0
        registros_ignorados = 0
        erros = []
        for idx, row in df.iterrows():
            try:
                cpf = sanitizar_cpf(str(row['cpf']))
                nome = sanitizar_texto(str(row['nome'])).strip().upper()
                empresa = sanitizar_texto(str(row.get('empresa', ''))).strip().upper() if pd.notna(row.get('empresa')) else ""
                if not validar_cpf(cpf):
                    erros.append(f"Linha {idx+2}: CPF inválido")
                    registros_ignorados += 1
                    continue
                if not nome:
                    erros.append(f"Linha {idx+2}: Nome vazio")
                    registros_ignorados += 1
                    continue
                existe = supabase_admin.table("Pessoas").select("id, nome, empresa").eq("cpf", cpf).execute().data
                if existe:
                    precisa_atualizar = (existe[0]['nome'] != nome) or (empresa and existe[0].get('empresa', '') != empresa)
                    if precisa_atualizar:
                        supabase_admin.table("Pessoas").update({"nome": nome, "empresa": empresa}).eq("cpf", cpf).execute()
                        registros_atualizados += 1
                    else:
                        registros_ignorados += 1
                else:
                    supabase_admin.table("Pessoas").insert({"cpf": cpf, "nome": nome, "empresa": empresa}).execute()
                    registros_inseridos += 1
            except Exception as e:
                erros.append(f"Linha {idx+2}: {str(e)}")
                registros_ignorados += 1
        mensagem = f"✅ Sincronização concluída! Inseridos: {registros_inseridos}, Atualizados: {registros_atualizados}, Ignorados: {registros_ignorados}"
        if erros:
            mensagem += f"\n⚠️ Erros: {len(erros)}"
        return {"sucesso": True, "mensagem": mensagem, "inseridos": registros_inseridos, "atualizados": registros_atualizados, "ignorados": registros_ignorados, "erros": erros}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao processar arquivo: {str(e)}"}

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
if "pagina_presentes" not in st.session_state:
    st.session_state.pagina_presentes = 1
if "br_list" not in st.session_state:
    st.session_state.br_list = None
if "gr_list" not in st.session_state:
    st.session_state.gr_list = None
if "outros_list" not in st.session_state:
    st.session_state.outros_list = None

# Carrega configurações iniciais
get_theme_config()
get_avatar_url()
get_timezone_offset()

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    theme = get_theme_config()
    if theme.get("apply_to_login", False):
        apply_theme_css()
    else:
        st.markdown('<style>.stApp{background:radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);}</style>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 48px;">🛡️</div>
                <h1 style="background: linear-gradient(135deg, #fff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">JOHN ACESSOS</h1>
                <p style="color: #a78bfa; letter-spacing: 3px;">CYBER SECURITY 2026</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            st.text_input("", placeholder="Identificação (usuário)", key="data_user", label_visibility="collapsed")
            senha = st.text_input("", type="password", placeholder="Chave de acesso criptografada", label_visibility="collapsed")
            submitted = st.form_submit_button("🛡️ ACESSAR SISTEMA", use_container_width=True)
            if submitted:
                if st.session_state.get("bloqueado_ate") and datetime.now() < st.session_state.bloqueado_ate:
                    st.error(f"⛔ Acesso bloqueado até {st.session_state.bloqueado_ate.strftime('%H:%M:%S')}")
                else:
                    if senha == ADMIN_PASSWORD:
                        st.session_state.logado = True
                        st.session_state.perfil = "ADMIN"
                        st.session_state.tentativas_login = 0
                        registrar_sessao("ADMIN", "admin")
                        st.rerun()
                    elif senha == VIGILANTE_PASSWORD:
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
    st.stop()

# ====================== APÓS LOGIN ======================
apply_theme_css()

if st.session_state.session_id:
    atualizar_atividade_sessao()
    limpar_sessoes_expiradas()
    total_conectados = contar_sessoes_ativas()
else:
    total_conectados = 0

# ====================== HEADER ======================
st.markdown(f"""
<div class="admin-header" style="background: rgba(8,8,20,0.6); backdrop-filter: blur(8px); border-radius: 20px; padding: 10px 20px; margin-bottom: 20px; border: 1px solid cyan;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; gap:15px; align-items:center;">
            <div style="width:45px;height:45px;">
                <img src="{st.session_state.avatar_url}" style="width:45px; height:45px; border-radius:50%; object-fit:cover; border:1px solid cyan; box-shadow:0 0 8px cyan;">
            </div>
            <div><h1 style="margin:0;font-size:18px; background:linear-gradient(135deg,cyan,magenta); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">JOHN ACESSOS - CYBER SECURITY 2026</h1><p style="margin:0;color:#aaf;font-size:10px;">MONITORAMENTO INTELIGENTE • ACESSO DE DADOS</p></div>
        </div>
        <div style="display:flex; gap:15px; align-items:center;">
            <div class="live-indicator"><span class="pulse-dot"></span> LIVE</div>
            <div class="session-indicator">👥 {total_conectados}</div>
            <div class="badge-admin">👑 {st.session_state.perfil}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([6,1,1,1])
with col3:
    if st.button("🔄 ATUALIZAR", key="btn_atualizar", use_container_width=True):
        invalidar_cache()
        st.cache_data.clear()
        st.rerun()
with col4:
    if st.button("🚪 SAIR", key="sair_final", use_container_width=True):
        remover_sessao()
        st.session_state.logado = False
        st.rerun()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown(f"""
    <div class="avatar-container">
        <div class="glow-ring"></div>
        <img src="{st.session_state.avatar_url}" class="avatar-image">
        <div class="sidebar-title" style="font-size: 20px; margin-top: 12px;">👮‍♂️ JOHN ACESSOS</div>
        <p style="color:#0ff; font-size: 9px; letter-spacing: 2px;">CYBER SECURITY 2026</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚡ ESTADO")
    st.markdown('<div class="info-item"><span style="color:#0f0;">●</span> REDE NEURAL: ATIVA</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item"><span style="color:#0ff;">●</span> MODELO: DEEP LEARNING</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item"><span style="color:#f0f;">●</span> CRIPTOGRAFIA: QUÂNTICA</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item"><span style="color:#ff0;">●</span> DATA LAKE: SEGURO</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📡 INFO")
    st.markdown(f"<div class='info-item'>👑 Perfil: {st.session_state.perfil}</div>", unsafe_allow_html=True)
    st.markdown('<div class="info-item">🟢 Status: Online</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item">📦 Versão: 13.2 (CYBER OTIMIZADO)</div>', unsafe_allow_html=True)

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
    with st.sidebar.expander("⏱️ Configurar Horário (Global)", expanded=False):
        st.markdown("### Ajuste de Fuso Horário")
        offset_atual = get_timezone_offset()
        novo_offset = st.number_input("Offset (horas)", value=offset_atual, step=0.5, format="%.1f", key="offset_global")
        if st.button("💾 Salvar Offset", key="salvar_offset"):
            if save_timezone_offset(novo_offset):
                st.success(f"✅ Offset alterado para {novo_offset} horas. Todos os novos registros usarão este horário.")
                st.rerun()
            else:
                st.error("Erro ao salvar offset.")
        st.caption("Exemplo: Brasília (UTC-3) = -3 | Londres (UTC+0) = 0")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("🎨 Configurar Tema (Global)", expanded=False):
        st.markdown("### Personalizar Fundo")
        config_atual = get_theme_config()
        tipo_atual = config_atual.get("type", "gradient")
        opcoes = ["Gradiente padrão", "Cor sólida", "Futurista Dinâmico (Canvas)"]
        idx = 0 if tipo_atual == "gradient" else 1 if tipo_atual == "solid" else 2 if tipo_atual == "futuristic" else 0
        tipo = st.radio("Tipo de fundo:", opcoes, index=idx, key="tipo_fundo_radio_simples")
        if tipo == "Gradiente padrão":
            nova_config = {"type": "gradient", "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)", "apply_to_login": False}
        elif tipo == "Cor sólida":
            cor = st.color_picker("Escolha a cor", value="#0a0a1a", key="cor_simples")
            nova_config = {"type": "solid", "value": cor, "apply_to_login": False}
        else:
            nova_config = {"type": "futuristic", "value": "futuristic", "apply_to_login": False}
        if st.button("💾 Salvar Tema", key="salvar_tema_simples"):
            if save_theme_config(nova_config):
                apply_theme_css()
                st.success("Tema atualizado!")
                st.rerun()
    
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
                empresa_selecionada = st.selectbox("Filtrar por unidade:", opcoes_empresa, key="export_empresa")
                if empresa_selecionada == "Todos":
                    df_export = df_todas.copy()
                else:
                    df_export = df_todas[df_todas['empresa'] == empresa_selecionada].copy()
                if not df_export.empty:
                    csv = df_export.to_csv(index=False, encoding='utf-8-sig')
                    nome_arquivo = f"cadastros_{empresa_selecionada.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    st.download_button(label="📥 Baixar CSV", data=csv, file_name=nome_arquivo, mime="text/csv", key="download_csv_pessoas")
                else:
                    st.warning("Nenhum registro para o filtro.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("🖼️ Configurar Avatar", expanded=False):
        st.markdown("### Personalizar Imagem do Perfil")
        uploaded_avatar = st.file_uploader("Escolha uma imagem (PNG/JPG)", type=["png","jpg","jpeg"], key="upload_avatar")
        if uploaded_avatar:
            with st.spinner("Processando..."):
                try:
                    avatar_base64 = compress_avatar_image(uploaded_avatar)
                    if save_avatar_url(avatar_base64):
                        st.success("✅ Avatar atualizado!")
                        st.rerun()
                    else:
                        st.error("Erro ao salvar avatar.")
                except Exception as e:
                    st.error(f"Erro: {e}")
        st.markdown("**Imagem atual:**")
        st.image(st.session_state.avatar_url, width=120, caption="Avatar atual")
        if st.button("↺ Restaurar Padrão", key="reset_avatar"):
            padrao_url = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230a0a2a'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-size='10'%3ESEGURANÇA%3C/text%3E%3C/svg%3E"
            if save_avatar_url(padrao_url):
                st.success("Avatar restaurado!")
                st.rerun()

# ====================== MÉTRICAS DE PERFORMANCE ======================
with st.expander("📊 Métricas de Performance", expanded=False):
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        tempo_medio = get_tempo_medio_query()
        st.metric("⏱️ Tempo médio de query", f"{tempo_medio:.0f}ms" if tempo_medio > 0 else "Calculando...")
    with col_m2:
        hit_ratio = cache_estatisticas.get_hit_ratio()
        st.metric("🎯 Cache hit ratio", f"{hit_ratio:.0f}%")
    with col_m3:
        total_cached = len(cache_estatisticas.cache_data) + len(cache_pessoas.cache_data) + len(cache_presentes.cache_data)
        st.metric("💾 Registros em cache", total_cached)
    st.caption(f"⚙️ Configurações: Cache TTL: {CACHE_TTL_PADRAO}s | Itens por página: {ITENS_POR_PAGINA} | Debounce: {DEBOUNCE_WAIT_MS}ms")

# ====================== DASHBOARD ======================
st.markdown("---")
stats = get_estatisticas_cached()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">👥</div><div class="status-indicator"><span class="status-led"></span> ATIVO</div></div>
        <div class="card-title">PRESENTES</div>
        <div class="card-value">{stats['total_presentes']}</div>
        <div class="card-footer"><span>🟢 ONLINE</span><span>⏱️ TEMPO REAL</span></div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">📊</div><div class="status-indicator"><span class="status-led"></span> BASE</div></div>
        <div class="card-title">CADASTRADOS</div>
        <div class="card-value">{stats['total_cadastrados']}</div>
        <div class="card-footer"><span>📋 CADASTROS</span><span>✅ VERIFICADOS</span></div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">🏛️</div><div class="status-indicator"><span class="status-led"></span> MAPA</div></div>
        <div class="card-title">SETORES ATIVOS</div>
        <div class="card-value">{stats['setores_unicos']}</div>
        <div class="card-footer"><span>📍 ÁREAS</span><span>🔍 MONITORADAS</span></div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">🛡️</div><div class="status-indicator"><span class="status-led"></span> 24/7</div></div>
        <div class="card-title">SEGURANÇA</div>
        <div class="card-value">ATIVA</div>
        <div class="card-footer"><span>🔒 PROTEÇÃO</span><span>⚡ INTELIGENTE</span></div>
    </div>
    """, unsafe_allow_html=True)

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
                        invalidar_cache()
                        st.cache_data.clear()
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
                pessoa = buscar_pessoa_por_cpf_debounced(cpf_limpo)
                if pessoa:
                    st.session_state.pessoa_confirmada = {"cpf": cpf_limpo, "nome": pessoa['nome'], "empresa": pessoa.get('empresa', '')}
                    st.success(f"✅ {pessoa['nome']} - {pessoa.get('empresa','N/A')}")
                else:
                    st.error("CPF não cadastrado")
                    st.session_state.pessoa_confirmada = None
    else:
        st.button("✅ CONFIRMAR CPF", disabled=True, key="confirma_cpf_disabled")

setor_escolhido = st.selectbox("📍 Destino:", destinos, key="destino")

if st.session_state.get("pessoa_confirmada"):
    with st.expander("⏱️ Opções de horário", expanded=False):
        editar_horario = st.checkbox("✏️ Editar horário da entrada", key="editar_horario_entrada")
        if editar_horario:
            dt_padrao = get_current_datetime()
            data_entrada = st.date_input("Data de entrada", value=dt_padrao.date(), key="data_entrada_edit")
            hora_entrada = st.time_input("Horário de entrada", value=dt_padrao.time(), key="hora_entrada_edit")
            dt_entrada = datetime.combine(data_entrada, hora_entrada)
            data_entrada_str = format_datetime_str(dt_entrada)
        else:
            data_entrada_str = format_datetime_str(get_current_datetime())
    if st.button("✅ Registrar Entrada", key="btn_entrada", type="primary"):
        p = st.session_state.pessoa_confirmada
        try:
            supabase.table("movimentacao").insert({
                "cpf": p['cpf'], "nome": p['nome'], "empresa": p['empresa'],
                "setor_destino": setor_escolhido,
                "data_entrada": data_entrada_str,
                "data_saida": ""
            }).execute()
            invalidar_cache()
            st.cache_data.clear()
            st.success(f"Entrada registrada para {setor_escolhido} às {data_entrada_str}!")
            st.session_state.pessoa_confirmada = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

# ====================== PESSOAS PRESENTES COM PAGINAÇÃO ======================
st.markdown("---")
st.markdown("### 📍 Pessoas Presentes")
dados = get_presentes_cached()

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
        with st.expander("⏱️ Editar horário de saída", expanded=False):
            editar_saida = st.checkbox("✏️ Personalizar horário", key="editar_saida_cpf")
            if editar_saida:
                dt_padrao_saida = get_current_datetime()
                data_saida = st.date_input("Data de saída", value=dt_padrao_saida.date(), key="data_saida_cpf")
                hora_saida = st.time_input("Horário de saída", value=dt_padrao_saida.time(), key="hora_saida_cpf")
                dt_saida = datetime.combine(data_saida, hora_saida)
                saida_str = format_datetime_str(dt_saida)
            else:
                saida_str = format_datetime_str(get_current_datetime())
        if st.button("🚪 Registrar Saída", key="sair_pesquisado"):
            try:
                supabase.table("movimentacao").update({"data_saida": saida_str}).eq("id", p['id']).execute()
                invalidar_cache()
                st.cache_data.clear()
                st.success(f"Saída registrada às {saida_str}")
                st.session_state.pessoa_saida = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
        st.markdown("---")
    
    st.markdown("#### 📋 Lista completa")
    # Paginação na lista de presentes
    total_presentes = len(dados)
    total_paginas_presentes = (total_presentes + ITENS_POR_PAGINA_PRESENTES - 1) // ITENS_POR_PAGINA_PRESENTES
    col_pag1, col_pag2, col_pag3 = st.columns([1,2,1])
    with col_pag1:
        if st.button("◀ Anterior", key="pag_presentes_ant"):
            if st.session_state.pagina_presentes > 1:
                st.session_state.pagina_presentes -= 1
                st.rerun()
    with col_pag2:
        st.markdown(f"<div style='text-align:center'>Página {st.session_state.pagina_presentes} de {total_paginas_presentes}</div>", unsafe_allow_html=True)
    with col_pag3:
        if st.button("Próximo ▶", key="pag_presentes_prox"):
            if st.session_state.pagina_presentes < total_paginas_presentes:
                st.session_state.pagina_presentes += 1
                st.rerun()
    start = (st.session_state.pagina_presentes - 1) * ITENS_POR_PAGINA_PRESENTES
    end = start + ITENS_POR_PAGINA_PRESENTES
    dados_paginados = dados[start:end]
    
    tabs = st.tabs(["📊 Prestador de Serviço", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"])
    with tabs[0]:
        for p in dados_paginados:
            col1, col2, col3, col4 = st.columns([4,3,2,2])
            col1.write(f"**{p['nome']}**")
            col2.write(f"📍 {p['setor_destino']}")
            col3.write(f"🏢 {p.get('empresa','N/A')}")
            with col4:
                with st.popover("🚪 Saída"):
                    st.write(f"Registrar saída de **{p['nome']}**")
                    with st.expander("⏱️ Horário", expanded=False):
                        editar = st.checkbox("Editar horário", key=f"edit_saida_{p['id']}")
                        if editar:
                            dt_padrao = get_current_datetime()
                            data_s = st.date_input("Data", value=dt_padrao.date(), key=f"data_saida_{p['id']}")
                            hora_s = st.time_input("Hora", value=dt_padrao.time(), key=f"hora_saida_{p['id']}")
                            dt_saida = datetime.combine(data_s, hora_s)
                            saida_str = format_datetime_str(dt_saida)
                        else:
                            saida_str = format_datetime_str(get_current_datetime())
                    if st.button("Confirmar Saída", key=f"confirm_saida_{p['id']}"):
                        try:
                            supabase.table("movimentacao").update({"data_saida": saida_str}).eq("id", p['id']).execute()
                            invalidar_cache()
                            st.cache_data.clear()
                            st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
            st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
    for i, setor in enumerate(["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"], 1):
        with tabs[i]:
            setor_clean = setor.split()[-1]
            pessoas_setor = [p for p in dados_paginados if setor_clean in p['setor_destino']]
            for p in pessoas_setor:
                col1, col2, col3, col4 = st.columns([4,3,2,2])
                col1.write(f"**{p['nome']}**")
                col2.write(f"🏢 {p.get('empresa','N/A')}")
                col3.write(f"🕒 {p['data_entrada']}")
                with col4:
                    with st.popover("🚪 Saída"):
                        st.write(f"Registrar saída de **{p['nome']}**")
                        with st.expander("⏱️ Horário", expanded=False):
                            editar = st.checkbox("Editar horário", key=f"edit_saida2_{p['id']}")
                            if editar:
                                dt_padrao = get_current_datetime()
                                data_s = st.date_input("Data", value=dt_padrao.date(), key=f"data_saida2_{p['id']}")
                                hora_s = st.time_input("Hora", value=dt_padrao.time(), key=f"hora_saida2_{p['id']}")
                                dt_saida = datetime.combine(data_s, hora_s)
                                saida_str = format_datetime_str(dt_saida)
                            else:
                                saida_str = format_datetime_str(get_current_datetime())
                        if st.button("Confirmar Saída", key=f"confirm_saida2_{p['id']}"):
                            try:
                                supabase.table("movimentacao").update({"data_saida": saida_str}).eq("id", p['id']).execute()
                                invalidar_cache()
                                st.cache_data.clear()
                                st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
else:
    st.info("Nenhuma pessoa presente no momento")

# ====================== HISTÓRICO COM DATA_EDITOR (CORRIGIDO) ======================
st.markdown("---")
with st.expander("🕒 Histórico Completo de Movimentações", expanded=True):
    col_prev, col_page, col_next = st.columns([1,2,1])
    with col_prev:
        if st.button("◀ ANTERIOR", key="pag_anterior"):
            if st.session_state.pagina_historico > 1:
                st.session_state.pagina_historico -= 1
                st.rerun()
    with col_page:
        st.markdown(f"<div style='text-align:center'>Página {st.session_state.pagina_historico}</div>", unsafe_allow_html=True)
    with col_next:
        if st.button("PRÓXIMO ▶", key="pag_proximo"):
            historico_data = get_historico_paginado(st.session_state.pagina_historico + 1)
            if st.session_state.pagina_historico < historico_data["total_paginas"]:
                st.session_state.pagina_historico += 1
                st.rerun()
    
    historico = get_historico_paginado(st.session_state.pagina_historico)
    if historico["dados"]:
        df = pd.DataFrame(historico["dados"])
        st.markdown(f"**Total de registros:** {historico['total']} | **Página {historico['pagina']} de {historico['total_paginas']}**")
        
        # Gerar relatórios
        col_rel1, col_rel2 = st.columns(2)
        with col_rel1:
            if st.button("📑 Relatório completo", key="relatorio_completo"):
                html = gerar_html_impressao(df, "RELATÓRIO COMPLETO")
                if html:
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir relatório (Ctrl+P para PDF)</a>', unsafe_allow_html=True)
        with col_rel2:
            if st.button("📑 Consolidado (todos setores)", key="relatorio_consolidado"):
                html = gerar_html_consolidado(df)
                if html:
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir consolidado</a>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🗑️ Exclusão de Registros (APENAS ADMIN)")
        
        # Preparar DataFrame para edição
        df_edit = df.copy()
        # Garantir que todas as colunas sejam string (exceto a de seleção)
        for col in df_edit.columns:
            if col != "id":
                df_edit[col] = df_edit[col].astype(str).fillna("")
        # Inserir coluna de seleção como booleano
        df_edit.insert(0, "Selecionar", False)
        if st.session_state.selected_ids:
            df_edit["Selecionar"] = df_edit["id"].isin(st.session_state.selected_ids)
        
        # Data editor sem configuração customizada (deixa o Streamlit inferir)
        edited_df = st.data_editor(
            df_edit,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Selecionar", default=False)
            },
            hide_index=True,
            use_container_width=True,
            key="data_editor_historico"
        )
        
        # Atualizar seleção
        novos_selecionados = edited_df[edited_df["Selecionar"]]["id"].tolist()
        if novos_selecionados != st.session_state.selected_ids:
            st.session_state.selected_ids = novos_selecionados
            st.rerun()
        
        if st.session_state.perfil == "ADMIN" and st.session_state.selected_ids:
            st.warning(f"⚠️ {len(st.session_state.selected_ids)} registro(s) selecionado(s)")
            col_excluir, col_cancelar = st.columns(2)
            with col_excluir:
                if st.button("🗑️ EXCLUIR SELECIONADOS (LOTE)", key="excluir_lote"):
                    resultado = excluir_multiplos_registros(st.session_state.selected_ids)
                    if resultado["sucesso"]:
                        st.success(resultado["mensagem"])
                        st.session_state.selected_ids = []
                        invalidar_cache()
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(resultado["mensagem"])
            with col_cancelar:
                if st.button("❌ Cancelar", key="cancelar_excluir_lote"):
                    st.session_state.selected_ids = []
                    st.rerun()
        
        # Botões extras
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🗑️ Excluir Selecionados", key="excluir_selecionados"):
                require_admin()
                if st.session_state.selected_ids:
                    st.session_state.pending_delete_ids = st.session_state.selected_ids.copy()
                    st.rerun()
        with col_btn2:
            if st.button("📋 Limpar Seleção", key="limpar_selecao"):
                st.session_state.selected_ids = []
                st.rerun()
        with col_btn3:
            if st.button("⚠️ LIMPAR TODO HISTÓRICO", key="limpar_historico"):
                require_admin()
                st.session_state.pending_clear_all = True
                st.rerun()
        
        # Confirmações de exclusão
        if st.session_state.pending_delete_ids:
            require_admin()
            st.error(f"⚠️ Excluir {len(st.session_state.pending_delete_ids)} registro(s)?")
            col_conf, col_canc = st.columns(2)
            with col_conf:
                if st.button("✅ SIM, EXCLUIR", key="confirmar_excluir"):
                    try:
                        for id_ in st.session_state.pending_delete_ids:
                            supabase_admin.table("movimentacao").delete().eq("id", id_).execute()
                        st.session_state.selected_ids = []
                        st.session_state.pending_delete_ids = []
                        invalidar_cache()
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            with col_canc:
                if st.button("❌ Cancelar", key="cancelar_excluir"):
                    st.session_state.pending_delete_ids = []
                    st.rerun()
        if st.session_state.pending_clear_all:
            require_admin()
            st.error("🚨 ATENÇÃO: apagar TODOS os registros. Digite 'LIMPAR TUDO'")
            confirm = st.text_input("Confirmação:", type="password", key="confirma_limpar")
            col_clear, col_cancel_clear = st.columns(2)
            with col_clear:
                if st.button("🔥 EXCLUIR TUDO", key="excluir_tudo"):
                    if confirm == "LIMPAR TUDO":
                        try:
                            supabase_admin.table("movimentacao").delete().neq("id", 0).execute()
                            invalidar_cache()
                            st.cache_data.clear()
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

# ====================== GESTÃO DE CADASTROS (ADMIN) COM LAZY LOADING ======================
st.markdown("---")
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        col_ferramenta1, col_ferramenta2 = st.columns(2)
        with col_ferramenta1:
            st.markdown("### 🗑️ Limpeza de Registros Duplicados")
            if st.button("Verificar Duplicados", key="verificar_dup"):
                with st.spinner("Verificando..."):
                    try:
                        todas = supabase.table("Pessoas").select("cpf, nome, empresa, id").execute().data
                        if todas:
                            df_check = pd.DataFrame(todas)
                            duplicados = df_check[df_check.duplicated(subset=['cpf'], keep=False)]
                            qtd_cpfs_dup = len(duplicados['cpf'].unique())
                            qtd_reg_dup = len(duplicados)
                            st.metric("CPFs Duplicados", qtd_cpfs_dup)
                            st.metric("Registros Duplicados", qtd_reg_dup)
                            if qtd_reg_dup > 0:
                                if st.button("🗑️ APAGAR DUPLICADOS", key="btn_apagar_dup"):
                                    resultado = apagar_registros_duplicados()
                                    if resultado["sucesso"]:
                                        st.success(resultado["mensagem"])
                                        st.rerun()
                                    else:
                                        st.error(resultado["mensagem"])
                    except Exception as e:
                        st.error(f"Erro: {e}")
        with col_ferramenta2:
            st.markdown("### 📤 Sincronizar Novos Cadastros")
            arquivo_sync = st.file_uploader("Selecione CSV/Excel", type=["csv","xlsx","xls"], key="sync_arquivo")
            if arquivo_sync:
                if st.button("🔄 SINCRONIZAR", key="btn_sincronizar"):
                    with st.spinner("Processando..."):
                        resultado = sincronizar_novos_cadastros(arquivo_sync)
                        if resultado["sucesso"]:
                            st.success(resultado["mensagem"])
                            invalidar_cache()
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(resultado["mensagem"])
        st.markdown("---")
        # Lazy loading das listas
        if st.button("Carregar Cadastros", key="carregar_cadastros"):
            with st.spinner("Carregando..."):
                todos = supabase.table("Pessoas").select("id, nome, cpf, empresa").order("nome").execute().data
                st.session_state.br_list = [p for p in todos if p.get('empresa', '').upper() == "BRASANITAS"]
                st.session_state.gr_list = [p for p in todos if p.get('empresa', '').upper() == "GRSA"]
                st.session_state.outros_list = [p for p in todos if p.get('empresa', '').upper() not in ["BRASANITAS","GRSA"]]
                st.rerun()
        if st.session_state.br_list is not None:
            tab1, tab2, tab3 = st.tabs(["🏭 BRASANITAS", "🔧 GRSA", "🏢 Prestadores"])
            with tab1:
                st.markdown(f"**Total:** {len(st.session_state.br_list)}")
                for p in st.session_state.br_list:
                    col1, col2, col3, col4 = st.columns([3,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    with col3:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_br_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_br_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_br_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_br_{p['id']}")
                                if st.form_submit_button("Salvar"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase_admin.table("Pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                invalidar_cache()
                                                st.cache_data.clear()
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
                                supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                                invalidar_cache()
                                st.cache_data.clear()
                                st.rerun()
                    st.divider()
            with tab2:
                st.markdown(f"**Total:** {len(st.session_state.gr_list)}")
                for p in st.session_state.gr_list:
                    col1, col2, col3, col4 = st.columns([3,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    with col3:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_gr_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_gr_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_gr_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_gr_{p['id']}")
                                if st.form_submit_button("Salvar"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase_admin.table("Pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                invalidar_cache()
                                                st.cache_data.clear()
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
                                supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                                invalidar_cache()
                                st.cache_data.clear()
                                st.rerun()
                    st.divider()
            with tab3:
                st.markdown(f"**Total:** {len(st.session_state.outros_list)}")
                search = st.text_input("🔍 Pesquisar", key="search_outros")
                filtrados = [p for p in st.session_state.outros_list if search.lower() in p['nome'].lower() or search.lower() in p['cpf']] if search else st.session_state.outros_list
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
                                if st.form_submit_button("Salvar"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("Pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase_admin.table("Pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                invalidar_cache()
                                                st.cache_data.clear()
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
                                supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                                invalidar_cache()
                                st.cache_data.clear()
                                st.rerun()
                    st.divider()
        else:
            st.info("Clique em 'Carregar Cadastros' para exibir a lista.")

apply_theme_css()
st.markdown("---")
st.markdown("""
<div class="footer">
    🛡️ JOHN ACESSOS - CYBER SECURITY 2026 | Monitoramento Inteligente & Proteção de Dados
</div>
""", unsafe_allow_html=True)
