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

# ====================== CONFIGURAÇÕES ======================
CACHE_TTL_PADRAO = 30
ITENS_POR_PAGINA = 50
DEBOUNCE_WAIT_MS = 500

# ====================== FUNÇÕES DO SUPABASE ======================
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

# ====================== ATUALIZAÇÃO AUTOMÁTICA (POLLING) ======================
# Substitui o Realtime que causava NotImplementedError
if "ultima_atualizacao" not in st.session_state:
    st.session_state.ultima_atualizacao = time.time()

def verificar_atualizacao_automatica():
    """Verifica a cada X segundos se deve atualizar o cache"""
    agora = time.time()
    intervalo = 5  # segundos (pode ajustar para 10, 15 conforme necessidade)
    if agora - st.session_state.ultima_atualizacao > intervalo:
        st.session_state.ultima_atualizacao = agora
        st.cache_data.clear()
        st.rerun()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "fgxv4VP0/*")
VIGILANTE_PASSWORD = st.secrets.get("VIGILANTE_PASSWORD", "JOHN123")

# ====================== CACHE OTIMIZADO (st.cache_data) ======================
@st.cache_data(ttl=30, show_spinner=False)
def get_estatisticas_cached():
    """Versão cacheada usando materialized view (se existir) ou view comum"""
    try:
        # Tenta usar a materialized view (mais rápida)
        result = supabase.table("estatisticas_dashboard_mv").select("*").execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
    except Exception:
        pass
    # Fallback para a view original
    try:
        result = supabase.table("estatisticas_dashboard").select("*").execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
    except Exception:
        pass
    return {"total_presentes": 0, "total_cadastrados": 0, "setores_unicos": 11}

@st.cache_data(ttl=60, show_spinner=False)
def get_presentes_cached():
    """Lista de pessoas presentes com apenas colunas necessárias"""
    try:
        dados = supabase.table("movimentacao")\
            .select("id, cpf, nome, empresa, setor_destino, data_entrada")\
            .eq("data_saida", "")\
            .execute()
        return dados.data
    except Exception:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def get_pessoa_por_cpf(cpf):
    """Busca pessoa pelo CPF com cache longo"""
    try:
        pessoa = supabase.table("Pessoas").select("nome, empresa").eq("cpf", cpf).execute()
        return pessoa.data[0] if pessoa.data else None
    except Exception:
        return None

def invalidar_cache():
    """Limpa todo o cache do Streamlit"""
    st.cache_data.clear()

def refresh_estatisticas_view():
    """Atualiza a materialized view e limpa cache"""
    try:
        supabase_admin.rpc('refresh_estatisticas_dashboard_mv').execute()
    except Exception:
        try:
            supabase_admin.sql("REFRESH MATERIALIZED VIEW estatisticas_dashboard_mv").execute()
        except Exception:
            pass
    invalidar_cache()
    return True

def registrar_tempo_query(tempo_ms):
    if "tempos_query" not in st.session_state:
        st.session_state.tempos_query = []
    st.session_state.tempos_query.append(tempo_ms)
    if len(st.session_state.tempos_query) > 100:
        st.session_state.tempos_query = st.session_state.tempos_query[-100:]

def get_tempo_medio_query():
    tempos = st.session_state.get("tempos_query", [])
    return sum(tempos) / len(tempos) if tempos else 0

# ====================== FUNÇÕES AUXILIARES (MANTIDAS ORIGINAIS) ======================
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

@debounce(wait_time=DEBOUNCE_WAIT_MS)
def buscar_pessoa_por_cpf_debounced(cpf):
    """Usa o cache interno para evitar consultas repetidas"""
    return get_pessoa_por_cpf(cpf)

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
        total = supabase.table("movimentacao").select("id", count="estimated").execute()
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

def get_timezone_offset():
    try:
        result = supabase.table("app_config").select("value").eq("key", "timezone_offset").execute()
        if result.data and result.data[0]['value']:
            return float(result.data[0]['value'])
    except:
        pass
    return 0.0

def save_timezone_offset(offset_horas):
    try:
        supabase_admin.table("app_config").upsert({
            "key": "timezone_offset",
            "value": str(offset_horas),
            "updated_at": datetime.now().isoformat()
        }).execute()
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

def futuristic_background_script():
    st.markdown("""
    <canvas id="futuristic-canvas"></canvas>
    <script>/* ... conteúdo original ... */</script>
    """, unsafe_allow_html=True)

def apply_theme_css():
    config = st.session_state.get("theme_config", get_theme_config())
    bg_type = config.get("type", "gradient")
    if bg_type == "gradient":
        bg_value = config.get("value", "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)")
        st.markdown(f'<style>.stApp {{ background: {bg_value} !important; background-attachment: fixed; background-size: cover; }}</style>', unsafe_allow_html=True)
    elif bg_type == "solid":
        bg_value = config.get("value", "#0a0a1a")
        st.markdown(f'<style>.stApp {{ background: {bg_value} !important; }}</style>', unsafe_allow_html=True)
    elif bg_type == "futuristic":
        futuristic_background_script()
    else:
        st.markdown('<style>.stApp{background:radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);}</style>', unsafe_allow_html=True)

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

    df_cc = df[
        df['setor_destino'].str.contains('C.C', case=False, na=False) &
        ~df['setor_destino'].str.contains('PRESTADOR', case=False, na=False)
    ]
    df_gr = df[df['setor_destino'].str.contains('GRSA', case=False, na=False)]
    df_br = df[df['setor_destino'].str.contains('Brasanitas', case=False, na=False)]
    outros = df[
        ~df['setor_destino'].str.contains('C.C|GRSA|Brasanitas', case=False, na=False) |
        df['setor_destino'].str.contains('PRESTADOR', case=False, na=False)
    ]

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

def validar_cpf(cpf):
    cpf_limpo = re.sub(r'\D', '', cpf)
    return cpf_limpo.isdigit() and len(cpf_limpo) == 11

def sanitizar_cpf(cpf):
    return re.sub(r'\D', '', cpf)

def sanitizar_texto(texto):
    if not texto:
        return texto
    return texto.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

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
            return {"sucesso": False, "mensagem": "Colunas 'cpf' e 'nome' obrigatórias."}
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
                    erros.append(f"Linha {idx+2}: CPF '{row['cpf']}' inválido")
                    registros_ignorados += 1
                    continue
                if not nome:
                    erros.append(f"Linha {idx+2}: Nome não pode estar vazio")
                    registros_ignorados += 1
                    continue
                existe = supabase_admin.table("Pessoas").select("id, nome, empresa").eq("cpf", cpf).execute().data
                if existe:
                    precisa_atualizar = False
                    if existe[0]['nome'] != nome:
                        precisa_atualizar = True
                    if empresa and existe[0].get('empresa', '') != empresa:
                        precisa_atualizar = True
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
        mensagem = f"Sincronização concluída! Inseridos: {registros_inseridos}, Atualizados: {registros_atualizados}, Ignorados: {registros_ignorados}"
        if erros:
            mensagem += f"\nErros encontrados: {len(erros)}"
        return {"sucesso": True, "mensagem": mensagem, "inseridos": registros_inseridos, "atualizados": registros_atualizados, "ignorados": registros_ignorados, "erros": erros}
    except Exception as e:
        return {"sucesso": False, "mensagem": f"Erro ao processar arquivo: {str(e)}"}

# ====================== INICIALIZAÇÃO DO ESTADO ======================
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

st.session_state.theme_config = get_theme_config()
st.session_state.avatar_url = get_avatar_url()

# ====================== CONFIGURAÇÃO DA PÁGINA ======================
st.set_page_config(page_title="JOHN ACESSOS - CYBER SECURITY 2026", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

# ====================== CSS FUTURISTA ======================
st.markdown("""
<style>
    /* RESET E BACKGROUND - EVITA ROLAGEM NA TELA DE LOGIN */
    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        overflow: hidden;
    }
    .stApp {
        transition: background 0.3s ease;
        height: 100%;
        overflow: auto;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(0, 255, 255, 0.2);
    }
    header[data-testid="stHeader"] button {
        color: #0ff !important;
        text-shadow: 0 0 3px #0ff;
    }
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 25, 0.65) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 4px 0 30px rgba(0, 255, 255, 0.1);
    }
    .avatar-container {
        text-align: center;
        margin-bottom: 25px;
        position: relative;
    }
    .avatar-image {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #0ff;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.5), inset 0 0 10px rgba(0, 255, 255, 0.3);
        transition: 0.3s;
        filter: drop-shadow(0 0 8px cyan);
    }
    .avatar-image:hover {
        transform: scale(1.02);
        box-shadow: 0 0 30px cyan;
        border-color: #f0f;
    }
    .glow-ring {
        position: absolute;
        top: -5px;
        left: 50%;
        transform: translateX(-50%);
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0,255,255,0.2), transparent);
        pointer-events: none;
        animation: pulseRing 2s infinite;
    }
    @keyframes pulseRing {
        0% { opacity: 0.5; transform: translateX(-50%) scale(0.9); }
        100% { opacity: 0; transform: translateX(-50%) scale(1.3); }
    }
    .dashboard-card {
        background: rgba(10, 15, 30, 0.45);
        backdrop-filter: blur(12px);
        border-radius: 28px;
        padding: 1.2rem 1rem;
        margin: 0.5rem;
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 15px rgba(0,255,255,0.2);
        transition: all 0.3s cubic-bezier(0.2,0.9,0.4,1.1);
        position: relative;
        overflow: hidden;
        cursor: default;
        z-index: 1;
    }
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.15), transparent);
        transition: left 0.6s ease;
        z-index: 0;
        pointer-events: none;
    }
    .dashboard-card:hover::before {
        left: 100%;
    }
    .dashboard-card::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, cyan, magenta, cyan, #0ff);
        border-radius: 30px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.4s;
    }
    .dashboard-card:hover::after {
        opacity: 0.6;
    }
    .dashboard-card:hover {
        transform: translateY(-6px);
        border-color: rgba(0, 255, 255, 0.8);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 25px cyan;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        position: relative;
        z-index: 2;
    }
    .card-icon {
        font-size: 2.5rem;
        filter: drop-shadow(0 0 6px cyan);
        transition: 0.2s;
    }
    .dashboard-card:hover .card-icon {
        transform: scale(1.05);
        filter: drop-shadow(0 0 12px magenta);
    }
    .status-indicator {
        display: flex;
        align-items: center;
        gap: 6px;
        background: rgba(0,0,0,0.5);
        padding: 4px 10px;
        border-radius: 30px;
        font-size: 0.7rem;
        font-family: 'Space Mono', monospace;
        border: 1px solid rgba(0, 255, 255, 0.4);
        backdrop-filter: blur(4px);
    }
    .status-led {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #0f0;
        box-shadow: 0 0 6px #0f0;
        animation: pulseLed 1.2s infinite;
    }
    @keyframes pulseLed {
        0% { opacity: 0.4; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1.2); }
    }
    .card-title {
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #aaf;
        font-weight: 500;
        margin-bottom: 8px;
        position: relative;
        z-index: 2;
    }
    .card-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, cyan);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 20px rgba(0,255,255,0.5);
        line-height: 1.2;
        font-family: 'Space Mono', monospace;
        margin-bottom: 4px;
        position: relative;
        z-index: 2;
    }
    .card-footer {
        font-size: 0.7rem;
        color: rgba(0, 255, 255, 0.7);
        font-family: monospace;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 8px;
        position: relative;
        z-index: 2;
    }
    .stButton>button, .stForm button {
        background: rgba(0,20,40,0.7) !important;
        backdrop-filter: blur(8px);
        border: 1px solid #0ff !important;
        border-radius: 40px !important;
        color: #0ff !important;
        font-weight: bold;
        transition: 0.2s;
        box-shadow: 0 0 5px rgba(0,255,255,0.3);
    }
    .stButton>button:hover, .stForm button:hover {
        background: rgba(0,255,255,0.15) !important;
        border-color: magenta !important;
        color: magenta !important;
        box-shadow: 0 0 15px magenta;
        transform: scale(1.02);
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div {
        background: rgba(0, 10, 20, 0.7) !important;
        backdrop-filter: blur(8px);
        border: 1px solid #0ff !important;
        border-radius: 16px !important;
        color: #0ff !important;
        font-family: 'Space Mono', monospace;
        transition: 0.2s;
    }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
        border-color: magenta !important;
        box-shadow: 0 0 12px magenta;
    }
    .stForm, .stExpander, .stTabs [data-baseweb="tab-list"] {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(8px);
        border-radius: 20px;
        border: 1px solid rgba(0,255,255,0.2);
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #ccc;
        border-radius: 30px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0,255,255,0.2), rgba(255,0,255,0.2));
        color: #0ff !important;
        text-shadow: 0 0 3px cyan;
    }
    .stDataFrame {
        background: rgba(0,0,0,0.4) !important;
        border: 1px solid cyan !important;
        border-radius: 16px;
    }
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0,0,0,0.5);
        padding: 4px 12px;
        border-radius: 40px;
        font-size: 12px;
        font-family: monospace;
        border: 1px solid #0ff;
        color: #0ff;
    }
    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #0f0;
        border-radius: 50%;
        box-shadow: 0 0 5px #0f0;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.4; transform: scale(0.8);}
        100% { opacity: 1; transform: scale(1.2);}
    }
    .footer {
        text-align: center;
        padding: 15px;
        color: #6b7280;
        font-size: 9px;
        border-top: 1px solid rgba(0,255,255,0.2);
        margin-top: 25px;
    }
    h1, h2, h3, p, label, .info-item, .stMarkdown, .stRadio label, .stCheckbox label {
        color: #eef !important;
        text-shadow: 0 0 2px rgba(0,0,0,0.5);
    }
    .info-item {
        margin-bottom: 12px;
        font-size: 13px;
        display: flex;
        gap: 8px;
        font-family: 'Space Mono', monospace;
    }
    .badge-admin {
        background: linear-gradient(135deg, cyan, magenta);
        padding: 4px 15px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 11px;
        color: #000;
    }
    .session-indicator {
        background: rgba(0,0,0,0.6);
        border-radius: 30px;
        padding: 4px 12px;
        font-size: 12px;
        font-family: monospace;
        color: cyan;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    #futuristic-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -9999;
        pointer-events: none;
    }
    .sync-card {
        background: linear-gradient(135deg, rgba(0,255,255,0.05), rgba(0,100,100,0.1));
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(0,255,255,0.3);
    }
    .success-animation {
        animation: glowPulse 0.5s ease-in-out;
    }
    @keyframes glowPulse {
        0% { box-shadow: 0 0 0 0 rgba(0,255,0,0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0,255,0,0); }
        100% { box-shadow: 0 0 0 0 rgba(0,255,0,0); }
    }
</style>
""", unsafe_allow_html=True)

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    theme = st.session_state.theme_config
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
# Chamada da atualização automática
verificar_atualizacao_automatica()

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
    if st.session_state.get("perfil"):
        st.markdown(f"<div class='info-item'>👑 Perfil: {st.session_state.perfil}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-item'>👑 Perfil: ---</div>", unsafe_allow_html=True)
    st.markdown('<div class="info-item">🟢 Status: Online</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item">📦 Versão: 13.2 (CYBER OTIMIZADO)</div>', unsafe_allow_html=True)

# ====================== ADMIN: CONFIGURAÇÕES ======================
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
        tipo = st.selectbox("Tipo de fundo", ["Gradiente padrão", "Cor sólida", "Futurista Dinâmico (Canvas)"])
        if tipo == "Cor sólida":
            cor = st.color_picker("Escolha a cor", value="#0a0a1a")
            nova_config = {"type": "solid", "value": cor, "apply_to_login": False}
        elif tipo == "Futurista Dinâmico (Canvas)":
            nova_config = {"type": "futuristic", "value": "futuristic", "apply_to_login": False}
        else:
            nova_config = {"type": "gradient", "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)", "apply_to_login": False}
        if st.button("💾 Salvar Tema"):
            if save_theme_config(nova_config):
                apply_theme_css()
                st.success("Tema atualizado!")
                st.rerun()
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("📤 Compartilhar Dados de Pessoas", expanded=False):
        st.markdown("### Exportar Cadastros")
        try:
            todas_pessoas = supabase.table("Pessoas").select("nome, cpf, empresa").execute().data
            if todas_pessoas:
                df_todas = pd.DataFrame(todas_pessoas)
                csv = df_todas.to_csv(index=False, encoding='utf-8-sig')
                st.download_button("📥 Baixar CSV", data=csv, file_name=f"cadastros_{datetime.now().strftime('%Y%m%d')}.csv")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("🖼️ Configurar Avatar", expanded=False):
        uploaded_avatar = st.file_uploader("Imagem (PNG/JPG)", type=["png","jpg","jpeg"])
        if uploaded_avatar:
            with st.spinner("Processando..."):
                try:
                    avatar_base64 = compress_avatar_image(uploaded_avatar)
                    if save_avatar_url(avatar_base64):
                        st.success("Avatar atualizado!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        st.image(st.session_state.avatar_url, width=100, caption="Avatar atual")
        if st.button("Restaurar padrão"):
            padrao = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230a0a2a'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-size='10'%3ESEGURANÇA%3C/text%3E%3C/svg%3E"
            if save_avatar_url(padrao):
                st.success("Avatar restaurado!")
                st.rerun()

# ====================== MÉTRICAS DE PERFORMANCE ======================
with st.expander("📊 Métricas de Performance", expanded=False):
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        tempo_medio = get_tempo_medio_query()
        st.metric("⏱️ Tempo médio de query", f"{tempo_medio:.0f}ms" if tempo_medio > 0 else "Calculando...")
    with col_m2:
        st.metric("🎯 Cache hit ratio", "N/A (st.cache_data)")
    with col_m3:
        st.metric("💾 Cache ativo", "st.cache_data (automático)")
    st.caption(f"⚙️ Configurações: Cache TTL: {CACHE_TTL_PADRAO}s | Itens por página: {ITENS_POR_PAGINA} | Debounce: {DEBOUNCE_WAIT_MS}ms")
    if st.button("🔄 Atualizar Estatísticas (View)", key="refresh_stats_view", use_container_width=True):
        with st.spinner("Atualizando..."):
            if refresh_estatisticas_view():
                st.success("Estatísticas atualizadas!")
                st.rerun()
            else:
                st.error("Falha na atualização. Verifique se a view existe.")

# ====================== DASHBOARD ======================
st.markdown("---")
stats = get_estatisticas_cached()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">👥</div><div class="status-indicator">ATIVO</div></div>
        <div class="card-title">PRESENTES</div>
        <div class="card-value">{stats['total_presentes']}</div>
        <div class="card-footer">🟢 ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">📊</div><div class="status-indicator">BASE</div></div>
        <div class="card-title">CADASTRADOS</div>
        <div class="card-value">{stats['total_cadastrados']}</div>
        <div class="card-footer">📋 VERIFICADOS</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">🏛️</div><div class="status-indicator">MAPA</div></div>
        <div class="card-title">SETORES ATIVOS</div>
        <div class="card-value">{stats['setores_unicos']}</div>
        <div class="card-footer">📍 MONITORADOS</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">🛡️</div><div class="status-indicator">24/7</div></div>
        <div class="card-title">SEGURANÇA</div>
        <div class="card-value">ATIVA</div>
        <div class="card-footer">🔒 PROTEÇÃO</div>
    </div>
    """, unsafe_allow_html=True)

# ====================== CADASTRO DE PESSOAS ======================
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
    destinos = ["🏥 C.C PRESTADOR DE SERVIÇOS", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção", "🧪 Laboratório", "💊 Farmacia", "🏥 P.A", "👶 PEDIATRIA P.A", "🔧 ENG.CLINICA", "🧹 HORTELARIA", "📦 OPME 6°AND", "📦 OPME 9°AND", "🔒 SSGA", "🏥 CDU", "⚕️ ONCOLOGIA"]
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
            st.success(f"Entrada registrada para {setor_escolhido} às {data_entrada_str}!")
            st.session_state.pessoa_confirmada = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")

# ====================== PESSOAS PRESENTES ======================
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
                st.success(f"Saída registrada às {saida_str}")
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
            with col4:
                with st.popover("🚪 Saída"):
                    st.write(f"Registrar saída de **{p['nome']}**")
                    with st.expander("⏱️ Horário", expanded=False):
                        editar_horario_saida = st.checkbox("Editar horário", key=f"edit_saida_{p['id']}")
                        if editar_horario_saida:
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
                            st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
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
                with col4:
                    with st.popover("🚪 Saída"):
                        st.write(f"Registrar saída de **{p['nome']}**")
                        with st.expander("⏱️ Horário", expanded=False):
                            editar_horario_saida = st.checkbox("Editar horário", key=f"edit_saida2_{p['id']}")
                            if editar_horario_saida:
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
                                st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
else:
    st.info("Nenhuma pessoa presente no momento")

# ====================== HISTÓRICO ======================
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
        st.markdown("### 🗑️ Exclusão de Registros (APENAS ADMIN)")
        if st.session_state.perfil == "ADMIN":
            col_sel_all, col_sel_clear = st.columns(2)
            with col_sel_all:
                if st.button("✅ Selecionar todos da página", key="selecionar_todos_pagina"):
                    ids_pagina = [row['id'] for row in historico["dados"]]
                    for id_ in ids_pagina:
                        if id_ not in st.session_state.selected_ids:
                            st.session_state.selected_ids.append(id_)
                    st.rerun()
            with col_sel_clear:
                if st.button("📋 Limpar seleção", key="limpar_selecao_todos"):
                    st.session_state.selected_ids = []
                    st.rerun()
        for row in historico["dados"]:
            col_check, col_data = st.columns([0.5, 9.5])
            with col_check:
                if st.session_state.perfil == "ADMIN":
                    checked = st.checkbox("", key=f"chk_{row['id']}", value=row['id'] in st.session_state.selected_ids)
                    if checked and row['id'] not in st.session_state.selected_ids:
                        st.session_state.selected_ids.append(row['id'])
                    elif not checked and row['id'] in st.session_state.selected_ids:
                        st.session_state.selected_ids.remove(row['id'])
            with col_data:
                st.markdown(f"ID {row['id']} - {row['nome']} | CPF: {row['cpf']} | Empresa: {row.get('empresa','N/A')} | Entrada: {row['data_entrada']} | Saída: {row['data_saida'] or 'Presente'}")
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
                        st.rerun()
                    else:
                        st.error(resultado["mensagem"])
            with col_cancelar:
                if st.button("❌ Cancelar", key="cancelar_excluir_lote"):
                    st.session_state.selected_ids = []
                    st.rerun()
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
        col_ferramenta1, col_ferramenta2 = st.columns(2)
        with col_ferramenta1:
            st.markdown("### 🗑️ Limpeza de Registros Duplicados")
            try:
                todas_pessoas = supabase.table("Pessoas").select("cpf, nome, empresa, id").execute().data
                if todas_pessoas:
                    df_check = pd.DataFrame(todas_pessoas)
                    duplicados = df_check[df_check.duplicated(subset=['cpf'], keep=False)]
                    qtd_cpfs_dup = len(duplicados['cpf'].unique()) if not duplicados.empty else 0
                    qtd_reg_dup = len(duplicados)
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    col_stats1.metric("Total de Cadastros", len(todas_pessoas))
                    col_stats2.metric("CPFs Duplicados", qtd_cpfs_dup, delta="⚠️" if qtd_cpfs_dup > 0 else "✓")
                    col_stats3.metric("Registros Duplicados", qtd_reg_dup, delta=f"-{qtd_reg_dup - qtd_cpfs_dup} a remover" if qtd_reg_dup > 0 else "✓")
                    if qtd_reg_dup > 0:
                        st.warning(f"Detectados {qtd_reg_dup} registro(s) duplicado(s)")
                        if st.button("🗑️ APAGAR REGISTROS DUPLICADOS", key="btn_apagar_duplicados", type="primary"):
                            with st.spinner("Processando..."):
                                resultado = apagar_registros_duplicados()
                                if resultado["sucesso"]:
                                    if resultado.get("duplicados_removidos", 0) > 0:
                                        st.success(resultado["mensagem"])
                                        st.balloons()
                                        time.sleep(2)
                                        st.rerun()
                                    else:
                                        st.info(resultado["mensagem"])
                                else:
                                    st.error(resultado["mensagem"])
                    else:
                        st.success("Nenhum CPF duplicado encontrado!")
                else:
                    st.info("Nenhum cadastro encontrado.")
            except Exception as e:
                st.error(f"Erro ao verificar duplicatas: {e}")
        with col_ferramenta2:
            st.markdown("### 📤 Sincronizar Novos Cadastros")
            arquivo_sync = st.file_uploader("Selecione o arquivo CSV/Excel", type=["csv","xlsx","xls"], key="sync_arquivo")
            if arquivo_sync:
                if st.button("🔄 SINCRONIZAR CADASTROS", key="btn_sincronizar", type="primary"):
                    with st.spinner("Processando sincronização..."):
                        resultado = sincronizar_novos_cadastros(arquivo_sync)
                        if resultado["sucesso"]:
                            st.success("✅ Sincronização concluída!")
                            col_res1, col_res2, col_res3 = st.columns(3)
                            col_res1.metric("Inseridos", resultado.get("inseridos", 0), delta="+")
                            col_res2.metric("Atualizados", resultado.get("atualizados", 0), delta="~")
                            col_res3.metric("Ignorados", resultado.get("ignorados", 0), delta="=")
                            st.info(resultado["mensagem"])
                            if resultado.get("erros"):
                                with st.expander(f"⚠️ {len(resultado['erros'])} erro(s)"):
                                    for erro in resultado["erros"][:20]:
                                        st.error(erro)
                            invalidar_cache()
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(resultado["mensagem"])
        st.markdown("---")
        try:
            todos = supabase.table("Pessoas").select("id, nome, cpf, empresa").order("nome").execute().data
        except:
            todos = []
        if not todos:
            st.info("Nenhum cadastro")
        else:
            br = [p for p in todos if p.get('empresa', '').upper() == "BRASANITAS"]
            gr = [p for p in todos if p.get('empresa', '').upper() == "GRSA"]
            outros = [p for p in todos if p.get('empresa', '').upper() not in ["BRASANITAS","GRSA"]]
            tab1, tab2, tab3 = st.tabs(["🏭 BRASANITAS", "🔧 GRSA", "🏢 Prestadores"])
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
                                st.rerun()
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
                                supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                                invalidar_cache()
                                st.rerun()
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
                                supabase_admin.table("Pessoas").delete().eq("id", p['id']).execute()
                                invalidar_cache()
                                st.rerun()
                    st.divider()

apply_theme_css()
st.markdown("---")
st.markdown("""
<div class="footer">
    🛡️ JOHN ACESSOS - CYBER SECURITY 2026 | Monitoramento Inteligente & Proteção de Dados
</div>
""", unsafe_allow_html=True)
