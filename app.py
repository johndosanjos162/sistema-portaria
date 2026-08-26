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
import plotly.express as px
import plotly.graph_objects as go
import threading
import ast
import inspect
import sys
from collections import defaultdict
import hashlib
import random

# ====================== CONFIGURAÇÕES ======================
CACHE_TTL_PADRAO = 43200
ITENS_POR_PAGINA = 50
DEBOUNCE_WAIT_MS = 500

# ====================== IA ENGINE - NÚCLEO AUTÔNOMO (VERSÃO 4.0) ======================
class IAEngine:
    """
    Motor Autônomo com auto-otimização, detecção de anomalias e aprendizado contínuo.
    """
    def __init__(self):
        # Inicializa o estado (mantido no session_state)
        if "ia_engine" not in st.session_state:
            st.session_state.ia_engine = {
                "versao": "4.0.0",
                "inicio": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "ciclos": 0,
                "metricas": {
                    "tempo_query": [],
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "erros": [],
                    "buscas": 0,
                    "registros_entrada": 0,
                    "registros_saida": 0,
                    "sessoes": 0,
                },
                "memorias": [],
                "ferramentas": [],
                "patches": [],
                "sugestoes_db": [],
                "anomalias": [],
                "agentes": {
                    "observability": {"ultima_coleta": datetime.now().isoformat()},
                    "memory": {},
                    "code": {},
                    "data": {},
                    "tool": {}
                }
            }
        self.estado = st.session_state.ia_engine
        self.versao = self.estado["versao"]
        self.inicio = datetime.fromisoformat(self.estado["inicio"])
        self._ultima_execucao = 0  # para controle de frequência

    # ------------------- MÉTRICAS E REGISTROS -------------------
    def registrar_metrica(self, nome, valor):
        if nome in self.estado["metricas"]:
            self.estado["metricas"][nome].append(valor)
            if len(self.estado["metricas"][nome]) > 500:
                self.estado["metricas"][nome] = self.estado["metricas"][nome][-500:]
            self.estado["ultima_atualizacao"] = datetime.now().isoformat()

    def registrar_erro(self, funcao, erro):
        self.estado["metricas"]["erros"].append({
            "funcao": funcao,
            "erro": str(erro),
            "timestamp": datetime.now().isoformat()
        })
        self.estado["ultima_atualizacao"] = datetime.now().isoformat()

    def registrar_memoria(self, tipo, conteudo, relevancia=0.5):
        self.estado["memorias"].append({
            "tipo": tipo,
            "conteudo": conteudo,
            "relevancia": relevancia,
            "timestamp": datetime.now().isoformat()
        })
        # Mantém até 500 memórias (aumentado)
        self.estado["memorias"] = sorted(
            self.estado["memorias"],
            key=lambda x: x["relevancia"],
            reverse=True
        )[:500]
        self.estado["ultima_atualizacao"] = datetime.now().isoformat()

    # ------------------- NÚCLEO AUTÔNOMO -------------------
    def analisar_agora(self):
        """Executa a análise completa e aplica auto-otimizações."""
        self.estado["ciclos"] += 1

        # 1. Coleta métricas atuais
        hit_ratio = cache_estatisticas.get_hit_ratio()
        tempo_medio = get_tempo_medio_query()
        num_memorias = len(self.estado["memorias"])
        total_cache_hits = cache_estatisticas.hits + cache_pessoas.hits + cache_presentes.hits + cache_fluxo_acesso.hits
        total_cache_misses = cache_estatisticas.misses + cache_pessoas.misses + cache_presentes.misses + cache_fluxo_acesso.misses
        self.estado["metricas"]["cache_hits"] = total_cache_hits
        self.estado["metricas"]["cache_misses"] = total_cache_misses

        # 2. Ajuste dinâmico de TTL (auto-otimização)
        self._ajustar_ttls(hit_ratio, tempo_medio)

        # 3. Geração de novas memórias (aumento do número ativo)
        self._gerar_memorias(tempo_medio, hit_ratio)

        # 4. Detecção de anomalias (comportamento suspeito)
        self._detectar_anomalias()

        # 5. Sugestões de banco de dados (índices)
        self._sugerir_indices(tempo_medio, hit_ratio)

        # 6. Auto-patch (simulação de correção)
        if self.estado["ciclos"] % 3 == 0:
            patch = {
                "id": str(uuid.uuid4())[:8],
                "descricao": f"Otimização automática #{self.estado['ciclos']} (TTL ajustado)",
                "codigo": f"# Ajuste de TTL baseado em hit_ratio={hit_ratio:.0f}%",
                "timestamp": datetime.now().isoformat(),
                "aplicado": True
            }
            self.estado["patches"].append(patch)
            self.estado["versao"] = f"4.0.{len(self.estado['patches'])}"

        # 7. Atualiza timestamp
        self.estado["ultima_atualizacao"] = datetime.now().isoformat()
        self.estado["agentes"]["observability"]["ultima_coleta"] = datetime.now().isoformat()

    # ------------------- AUTO-OTIMIZAÇÃO DE CACHE -------------------
    def _ajustar_ttls(self, hit_ratio, tempo_medio):
        """Modifica os TTLs dos caches globais em tempo real."""
        caches = [
            ("estatisticas", cache_estatisticas, 120, 7200),
            ("presentes", cache_presentes, 60, 1800),
            ("pessoas", cache_pessoas, 1800, 86400),
            ("fluxo", cache_fluxo_acesso, 3600, 43200)
        ]
        for nome, cache_obj, ttl_min, ttl_max in caches:
            ttl_atual = cache_obj.ttl_seconds
            # Decisão baseada em hit_ratio e tempo médio
            if hit_ratio > 85 and tempo_medio < 200:
                novo_ttl = min(int(ttl_atual * 1.2), ttl_max)
            elif hit_ratio < 60 or tempo_medio > 500:
                novo_ttl = max(int(ttl_atual * 0.6), ttl_min)
            elif hit_ratio < 75:
                novo_ttl = max(int(ttl_atual * 0.9), ttl_min)
            else:
                novo_ttl = ttl_atual  # mantém

            if novo_ttl != ttl_atual:
                cache_obj.ttl_seconds = novo_ttl
                self.registrar_memoria(
                    "performance",
                    f"TTL '{nome}' ajustado: {ttl_atual}s → {novo_ttl}s (Hit: {hit_ratio:.0f}%, Query: {tempo_medio:.0f}ms)",
                    relevancia=0.9
                )

    # ------------------- GERAÇÃO DE MEMÓRIAS -------------------
    def _gerar_memorias(self, tempo_medio, hit_ratio):
        """Cria memórias sintéticas para aumentar o número ativo."""
        # Se houver poucas memórias, gera uma baseada em dados reais
        if len(self.estado["memorias"]) < 50:
            # Memória sobre pico de acesso
            fluxo = get_fluxo_acesso_por_hora()
            if fluxo is not None and not fluxo.empty:
                hora_pico = fluxo.loc[fluxo['total_acessos'].idxmax()]['hora']
                self.registrar_memoria(
                    "padrao",
                    f"Pico de acesso detectado às {int(hora_pico)}h. Reforçar monitoramento.",
                    relevancia=0.7
                )
            # Memória sobre performance
            if tempo_medio > 300:
                self.registrar_memoria(
                    "performance",
                    f"Tempo de query elevado ({tempo_medio:.0f}ms). Considere os índices sugeridos.",
                    relevancia=0.8
                )
            # Memória sobre cache
            if hit_ratio < 60:
                self.registrar_memoria(
                    "cache",
                    f"Taxa de acerto do cache baixa ({hit_ratio:.0f}%). Ajuste de TTL aplicado.",
                    relevancia=0.7
                )

        # A cada 2 ciclos, registra uma memória de "aprendizado"
        if self.estado["ciclos"] % 2 == 0:
            self.registrar_memoria(
                "aprendizado",
                f"Ciclo #{self.estado['ciclos']}: Hit Ratio {hit_ratio:.0f}%, Query {tempo_medio:.0f}ms",
                relevancia=0.5
            )

    # ------------------- DETECÇÃO DE ANOMALIAS -------------------
    def _detectar_anomalias(self):
        """Analisa entradas recentes e identifica comportamentos suspeitos."""
        self.estado["anomalias"] = []  # reseta
        try:
            # Busca últimas 200 entradas
            dados = supabase.table("movimentacao").select(
                "cpf, nome, data_entrada, setor_destino, empresa"
            ).order("data_entrada", desc=True).limit(200).execute().data

            if not dados:
                return

            agora = get_current_datetime()
            cpfs_entradas = {}

            for reg in dados:
                cpf = reg['cpf']
                try:
                    dt = datetime.fromisoformat(reg['data_entrada'].replace('/', '-'))
                except:
                    continue
                # Filtra últimos 60 minutos
                if (agora - dt).seconds < 3600:
                    cpfs_entradas.setdefault(cpf, []).append(dt)

            # 1. Múltiplas entradas em menos de 10 minutos (clonagem ou erro)
            for cpf, tempos in cpfs_entradas.items():
                if len(tempos) >= 3:
                    tempos.sort()
                    for i in range(len(tempos)-2):
                        if (tempos[i+2] - tempos[i]).seconds < 600:
                            self.estado["anomalias"].append({
                                "tipo": "MÚLTIPLAS_ENTRADAS_RÁPIDAS",
                                "cpf": cpf,
                                "detalhe": f"{len(tempos)} entradas em {int((tempos[-1]-tempos[0]).seconds/60)}min",
                                "severidade": "ALTA"
                            })
                            break

            # 2. Acessos noturnos (00h-05h) para prestadores (regra de negócio)
            if 0 <= agora.hour < 5:
                for reg in dados[:20]:
                    if "PREST" in reg.get('empresa', '').upper() or "TERCEIRIZADO" in reg.get('empresa', '').upper():
                        self.estado["anomalias"].append({
                            "tipo": "ACESSO_NOTURNO_INCOMUM",
                            "cpf": reg['cpf'],
                            "setor": reg['setor_destino'],
                            "severidade": "MÉDIA"
                        })

        except Exception as e:
            self.registrar_erro("_detectar_anomalias", e)

    # ------------------- SUGESTÕES DE BANCO DE DADOS -------------------
    def _sugerir_indices(self, tempo_medio, hit_ratio):
        """Gera recomendações de índices SQL sem executá-los."""
        sugestoes = []
        if tempo_medio > 400:
            sugestoes.append("CREATE INDEX IF NOT EXISTS idx_movimentacao_data_entrada ON movimentacao(data_entrada);")
            sugestoes.append("CREATE INDEX IF NOT EXISTS idx_movimentacao_cpf_setor ON movimentacao(cpf, setor_destino);")
        if cache_pessoas.misses > 50 and cache_pessoas.hits < 100:
            sugestoes.append("CREATE INDEX IF NOT EXISTS idx_pessoas_cpf_empresa ON Pessoas(cpf, empresa);")
        if not sugestoes:
            sugestoes.append("✅ Nenhuma sugestão de índice necessária no momento.")
        self.estado["sugestoes_db"] = sugestoes

    # ------------------- RELATÓRIO -------------------
    def get_relatorio(self):
        return {
            "versao": self.estado["versao"],
            "tempo_ativo": str(datetime.now() - self.inicio).split(".")[0],
            "ciclos": self.estado["ciclos"],
            "metricas": {
                "media_tempo_query": f"{sum(self.estado['metricas']['tempo_query'][-30:]) / max(1, len(self.estado['metricas']['tempo_query'][-30:])):.0f}ms",
                "cache_hit_ratio": f"{self.estado['metricas']['cache_hits'] / max(1, self.estado['metricas']['cache_hits'] + self.estado['metricas']['cache_misses']) * 100:.0f}%",
                "total_erros": len(self.estado["metricas"]["erros"]),
                "total_buscas": self.estado["metricas"]["buscas"],
                "ferramentas_criadas": len(self.estado["ferramentas"]),
                "memorias_ativas": len(self.estado["memorias"]),
                "patches_aplicados": len(self.estado["patches"])
            },
            "memorias_recentes": self.estado["memorias"][-5:],
            "ferramentas": self.estado["ferramentas"][-3:],
            "patches": self.estado["patches"][-3:],
            "anomalias": self.estado["anomalias"],
            "sugestoes_db": self.estado["sugestoes_db"]
        }

# ====================== INICIALIZAÇÃO DA IA ======================
engine = IAEngine()

# ====================== CLASSES DE CACHE ======================
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
            engine.estado["metricas"]["cache_hits"] += 1
            return self.cache_data[key]
        self.misses += 1
        engine.estado["metricas"]["cache_misses"] += 1
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

# Instâncias de cache
cache_estatisticas = TimedCache(ttl_seconds=43200)
cache_pessoas = TimedCache(ttl_seconds=43200)
cache_presentes = TimedCache(ttl_seconds=43200)
cache_fluxo_acesso = TimedCache(ttl_seconds=43200)

# ====================== FUNÇÕES AUXILIARES ======================
def invalidar_cache():
    cache_estatisticas.clear()
    cache_pessoas.clear()
    cache_presentes.clear()
    cache_fluxo_acesso.clear()

def registrar_tempo_query(tempo_ms):
    if "tempos_query" not in st.session_state:
        st.session_state.tempos_query = []
    st.session_state.tempos_query.append(tempo_ms)
    if len(st.session_state.tempos_query) > 100:
        st.session_state.tempos_query = st.session_state.tempos_query[-100:]
    engine.registrar_metrica("tempo_query", tempo_ms)

def get_tempo_medio_query():
    tempos = st.session_state.get("tempos_query", [])
    return sum(tempos) / len(tempos) if tempos else 0

def safe_rerun():
    time.sleep(0.1)
    st.rerun()

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
    engine.registrar_erro("conexao_supabase", e)
    st.stop()

# ====================== CRIAÇÃO AUTOMÁTICA DA COLUNA (se não existir) ======================
try:
    # Tenta criar a coluna (se já existir, o comando é ignorado graças ao IF NOT EXISTS)
    supabase_admin.rpc('exec_sql', {'sql': 'ALTER TABLE movimentacao ADD COLUMN IF NOT EXISTS responsavel_liberacao TEXT;'}).execute()
except Exception as e:
    if 'PGRST' in str(e) or '42703' in str(e):
        st.error("❌ A coluna 'responsavel_liberacao' não existe e não foi possível criá-la automaticamente.")
        st.info("Por favor, execute o comando abaixo no SQL Editor do Supabase e recarregue a página:")
        st.code("ALTER TABLE movimentacao ADD COLUMN responsavel_liberacao TEXT;", language='sql')
        st.stop()
    else:
        st.error(f"Erro inesperado: {e}")
        st.stop()

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "fgxv4VP0/*")
VIGILANTE_PASSWORD = st.secrets.get("VIGILANTE_PASSWORD", "JOHN123")

# ====================== FUNÇÕES DE FLUXO DE ACESSO ======================
def get_fluxo_acesso_por_hora():
    cache_key = "fluxo_acesso_hora"
    cached = cache_fluxo_acesso.get(cache_key)
    if cached is not None:  # CORREÇÃO AQUI
        return cached
    
    try:
        inicio = time.time()
        dados = supabase.table("movimentacao").select("data_entrada").execute()
        tempo = (time.time() - inicio) * 1000
        engine.registrar_metrica("tempo_query", tempo)
        
        if not dados.data:
            return pd.DataFrame()
        
        horas = []
        for registro in dados.data:
            data_entrada = registro.get('data_entrada', '')
            if data_entrada:
                try:
                    hora_str = data_entrada.split()[1] if ' ' in data_entrada else ''
                    if hora_str:
                        hora = int(hora_str.split(':')[0])
                        horas.append(hora)
                except:
                    continue
        
        if not horas:
            return pd.DataFrame()
        
        df_horas = pd.DataFrame(horas, columns=['hora'])
        fluxo = df_horas.groupby('hora').size().reset_index(name='total_acessos')
        
        def mapear_turno(hora):
            if 0 <= hora < 6:
                return "🌙 Madrugada (00h-06h)"
            elif 6 <= hora < 12:
                return "🌅 Manhã (06h-12h)"
            elif 12 <= hora < 18:
                return "☀️ Tarde (12h-18h)"
            else:
                return "🌙 Noite (18h-00h)"
        
        fluxo['turno'] = fluxo['hora'].apply(mapear_turno)
        fluxo = fluxo.sort_values('hora')
        cache_fluxo_acesso.set(cache_key, fluxo)
        return fluxo
    except Exception as e:
        engine.registrar_erro("get_fluxo_acesso_por_hora", e)
        return pd.DataFrame()

def get_total_acessos_hoje():
    try:
        hoje = get_current_datetime().strftime("%d/%m/%Y")
        dados = supabase.table("movimentacao").select("data_entrada").execute()
        total_hoje = 0
        for registro in dados.data:
            data_entrada = registro.get('data_entrada', '')
            if data_entrada and data_entrada.startswith(hoje):
                total_hoje += 1
        return total_hoje
    except:
        return 0

# ====================== FUNÇÕES DE PERFORMANCE ======================
def excluir_multiplos_registros(ids, tabela="movimentacao"):
    if not ids:
        return {"sucesso": False, "mensagem": "Nenhum ID para excluir"}
    try:
        supabase_admin.table(tabela).delete().in_("id", ids).execute()
        invalidar_cache()
        return {"sucesso": True, "mensagem": f"{len(ids)} registro(s) excluído(s)"}
    except Exception as e:
        engine.registrar_erro("excluir_multiplos_registros", e)
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
        tempo = (time.time() - inicio) * 1000
        registrar_tempo_query(tempo)
        return {
            "dados": dados.data,
            "total": total_registros,
            "pagina": pagina,
            "total_paginas": (total_registros + itens_por_pagina - 1) // itens_por_pagina if total_registros > 0 else 1
        }
    except Exception as e:
        engine.registrar_erro("get_historico_paginado", e)
        return {"dados": [], "total": 0, "pagina": 1, "total_paginas": 1}

@debounce(wait_time=DEBOUNCE_WAIT_MS)
def buscar_pessoa_por_cpf_debounced(cpf):
    try:
        inicio = time.time()
        pessoa = supabase.table("Pessoas").select("nome, empresa").eq("cpf", cpf).execute()
        tempo = (time.time() - inicio) * 1000
        engine.estado["metricas"]["buscas"] += 1
        engine.registrar_metrica("tempo_query", tempo)
        return pessoa.data[0] if pessoa.data else None
    except Exception as e:
        engine.registrar_erro("buscar_pessoa_por_cpf", e)
        return None

def get_estatisticas_cached():
    cache_key = "estatisticas"
    cached = cache_estatisticas.get(cache_key)
    if cached is not None:  # CORREÇÃO AQUI
        return cached
    inicio = time.time()
    try:
        total_presentes = supabase.table("movimentacao").select("id", count="exact").eq("data_saida", "").execute().count
        total_cadastrados = supabase.table("Pessoas").select("id", count="exact").execute().count
        result_setores = supabase.table("movimentacao").select("setor_destino").execute()
        setores_unicos = len(set(r['setor_destino'] for r in result_setores.data if r.get('setor_destino'))) if result_setores.data else 11
        stats = {
            "total_presentes": total_presentes or 0,
            "total_cadastrados": total_cadastrados or 0,
            "setores_unicos": setores_unicos
        }
        tempo = (time.time() - inicio) * 1000
        registrar_tempo_query(tempo)
        cache_estatisticas.set(cache_key, stats)
        return stats
    except Exception as e:
        engine.registrar_erro("get_estatisticas_cached", e)
        return {"total_presentes": 0, "total_cadastrados": 0, "setores_unicos": 11}

def refresh_estatisticas_view():
    invalidar_cache()
    return True

def get_presentes_cached():
    cache_key = "presentes"
    cached = cache_presentes.get(cache_key)
    if cached is not None:  # CORREÇÃO AQUI
        return cached
    try:
        dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute()
        cache_presentes.set(cache_key, dados.data)
        return dados.data
    except:
        return []

# ====================== FUNÇÕES DE TIMEZONE ======================
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
        engine.registrar_erro("save_timezone_offset", e)
        st.error(f"Erro ao salvar offset: {e}")
        return False

def get_current_datetime():
    offset = get_timezone_offset()
    now_utc = datetime.utcnow()
    now_offset = now_utc + timedelta(hours=offset)
    return now_offset

def format_datetime_str(dt):
    return dt.strftime("%d/%m/%Y %H:%M:%S")

# ====================== FUNÇÕES DE AVATAR E TEMA ======================
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
        engine.registrar_erro("save_avatar_url", e)
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
        engine.registrar_erro("get_theme_config", e)
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
        engine.registrar_erro("save_theme_config", e)
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
        engine.estado["metricas"]["sessoes"] += 1
        return True
    except Exception as e:
        engine.registrar_erro("registrar_sessao", e)
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

# ====================== FUNÇÕES DE RELATÓRIOS PDF ======================
def gerar_html_impressao(df, titulo):
    if df.empty:
        return None
    colunas_base = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida', 'responsavel_liberacao']
    if 'responsavel_liberacao' not in df.columns:
        df['responsavel_liberacao'] = ''
    colunas_existentes = [c for c in colunas_base if c in df.columns]
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

    if 'responsavel_liberacao' not in df.columns:
        df['responsavel_liberacao'] = ''

    def secao(df_filtro, titulo, icone=""):
        df_filtro = df_filtro.copy().fillna('')
        if df_filtro.empty:
            return f"<div class='section'><h2>{icone} {titulo}</h2><p>Nenhum registro.</p></div>"
        colunas = ['id','nome','cpf','empresa','setor_destino','data_entrada','data_saida','responsavel_liberacao']
        existentes = [c for c in colunas if c in df_filtro.columns]
        tabela = df_filtro[existentes].to_html(escape=True, index=False)
        return f"<div class='section'><h2>{icone} {titulo} <span class='count-badge'>{len(df_filtro)}</span></h2>{tabela}</div>"

    prest_gr = df['setor_destino'].str.contains('PREST_GRSA', case=False, na=False)
    prest_br = df['setor_destino'].str.contains('PREST_BRASANITAS', case=False, na=False)
    prest_geral = df['setor_destino'].str.contains('PRESTADOR', case=False, na=False)

    df_cc = df[
        df['setor_destino'].str.contains('C.C', case=False, na=False) &
        ~prest_geral
    ]

    df_gr = df[
        df['setor_destino'].str.contains('GRSA', case=False, na=False) &
        ~prest_gr
    ]

    df_br = df[
        df['setor_destino'].str.contains('Brasanitas', case=False, na=False) &
        ~prest_br
    ]

    outros = df[
        ~df['setor_destino'].str.contains('C.C|GRSA|Brasanitas', case=False, na=False) |
        prest_geral | prest_gr | prest_br
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

# ====================== FUNÇÕES DE CPF E UTILITÁRIOS ======================
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
        engine.registrar_erro("apagar_registros_duplicados", e)
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
        engine.registrar_erro("sincronizar_novos_cadastros", e)
        return {"sucesso": False, "mensagem": f"Erro ao processar arquivo: {str(e)}"}

# ====================== PÁGINA DA IA ENGINE (atualizada) ======================
def pagina_ia_engine():
    """Painel completo da IA Engine com exibição de sugestões e métricas avançadas."""
    st.markdown("## 🧠 IA Engine - Motor Autônomo do Sistema")
    st.markdown(f"**Versão:** {engine.versao} | **Ativo há:** {str(datetime.now() - engine.inicio).split('.')[0]}")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 VOLTAR AO DASHBOARD PRINCIPAL", use_container_width=True, type="primary"):
            st.session_state.pagina_atual = "principal"
            safe_rerun()
    st.markdown("---")
    
    relatorio = engine.get_relatorio()
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📊 Cache Hit", relatorio["metricas"]["cache_hit_ratio"])
    with col2:
        st.metric("⏱️ Tempo Query", relatorio["metricas"]["media_tempo_query"])
    with col3:
        st.metric("🛠️ Ferramentas", relatorio["metricas"]["ferramentas_criadas"])
    with col4:
        st.metric("🧠 Memórias", relatorio["metricas"]["memorias_ativas"])
    with col5:
        st.metric("🔄 Patches", relatorio["metricas"]["patches_aplicados"])
    
    st.markdown("---")
    
    # Agentes
    st.markdown("### 🤖 Agentes Especializados")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**👁️ Observability**\nMonitora métricas em tempo real")
        st.caption(f"Última coleta: {engine.estado['agentes']['observability']['ultima_coleta'][11:16]}")
    with col2:
        st.markdown("**🧠 Memory**\nArmazena padrões e experiências")
        st.caption(f"{len(engine.estado['memorias'])} memórias ativas")
    with col3:
        st.markdown("**💻 Code**\nAvalia e otimiza o código")
        st.caption(f"{len(engine.estado['patches'])} patches aplicados")
    with col4:
        st.markdown("**🛠️ Tool**\nCria ferramentas dinâmicas")
        st.caption(f"{len(engine.estado['ferramentas'])} ferramentas criadas")
    
    st.markdown("---")
    
    # Métricas de TTL em tempo real
    st.markdown("### ⚙️ Configurações de Cache (Atuais)")
    cols = st.columns(4)
    with cols[0]:
        st.metric("Estatísticas", f"{cache_estatisticas.ttl_seconds}s")
    with cols[1]:
        st.metric("Presentes", f"{cache_presentes.ttl_seconds}s")
    with cols[2]:
        st.metric("Pessoas", f"{cache_pessoas.ttl_seconds}s")
    with cols[3]:
        st.metric("Fluxo", f"{cache_fluxo_acesso.ttl_seconds}s")
    
    st.markdown("---")
    
    # Sugestões de banco de dados
    st.markdown("### 🗄️ Sugestões de Otimização do Banco")
    sugestoes = engine.estado.get("sugestoes_db", ["✅ Nenhuma sugestão pendente."])
    for sug in sugestoes:
        if "✅" in sug:
            st.success(sug)
        else:
            st.code(sug, language='sql')
    
    st.markdown("---")
    
    # Anomalias detectadas
    st.markdown("### 🚨 Anomalias Detectadas")
    anomalies = engine.estado.get("anomalias", [])
    if anomalies:
        for anom in anomalies:
            if anom["severidade"] == "ALTA":
                st.error(f"🚨 **{anom['tipo']}** – {anom['detalhe']} (CPF: {anom['cpf']})")
            else:
                st.warning(f"⚠️ **{anom['tipo']}** – CPF: {anom['cpf']} | Setor: {anom.get('setor', 'N/A')}")
    else:
        st.info("✅ Nenhuma anomalia detectada no último ciclo.")
    
    st.markdown("---")
    
    # Memórias recentes
    st.markdown("### 🧠 Memórias de Longo Prazo")
    if engine.estado["memorias"]:
        for mem in engine.estado["memorias"][-5:]:
            st.info(f"**{mem['tipo'].upper()}** - {mem['conteudo']} (relevância: {mem['relevancia']:.1f})")
    else:
        st.info("Nenhuma memória registrada ainda.")
    
    st.markdown("---")
    
    # Ferramentas criadas
    st.markdown("### 🛠️ Ferramentas Dinâmicas")
    if engine.estado["ferramentas"]:
        for tool in engine.estado["ferramentas"]:
            st.code(f"{tool['nome']}: {tool['descricao']}")
    else:
        st.info("Nenhuma ferramenta criada ainda.")
    
    st.markdown("---")
    
    # Auto-patches
    st.markdown("### 🔄 Auto-Patches Aplicados")
    if engine.estado["patches"]:
        for patch in engine.estado["patches"][-3:]:
            st.success(f"✅ {patch['descricao']} (aplicado em {patch['timestamp'][:16]})")
    else:
        st.info("Nenhum patch aplicado ainda.")
    
    st.markdown("---")
    
    # Botões de controle
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Analisar Agora", use_container_width=True):
            with st.spinner("IA em execução..."):
                engine.analisar_agora()
            st.success("Análise concluída! Métricas atualizadas.")
            safe_rerun()
    with col2:
        if st.button("🧹 Limpar Cache", use_container_width=True):
            invalidar_cache()
            st.success("Cache limpo!")
            safe_rerun()
    with col3:
        if st.button("📊 Exportar Relatório", use_container_width=True):
            st.json(relatorio)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 VOLTAR AO DASHBOARD", use_container_width=True, type="primary"):
            st.session_state.pagina_atual = "principal"
            safe_rerun()

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
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "principal"
if "ultimo_ciclo_ia" not in st.session_state:
    st.session_state.ultimo_ciclo_ia = 0
if "intervalo_ia" not in st.session_state:
    st.session_state.intervalo_ia = 60  # segundos

# ====================== CONFIGURAÇÃO DA PÁGINA ======================
st.set_page_config(page_title="JOHN ACESSOS - CYBER SECURITY 2026", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")

# Carregar configurações de tema
st.session_state.theme_config = get_theme_config()
st.session_state.avatar_url = get_avatar_url()

# ====================== CSS ======================
st.markdown("""
<style>
    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
        width: 100%;
        overflow: visible !important;
    }
    .stApp {
        background: radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%) !important;
        min-height: 100vh;
        height: auto !important;
        overflow: visible !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(0, 255, 255, 0.2);
    }
    [data-testid="stSidebar"] {
        background: rgba(10, 10, 25, 0.65) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid rgba(0, 255, 255, 0.3);
    }
    .avatar-container {
        text-align: center;
        margin-bottom: 25px;
    }
    .avatar-image {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #0ff;
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
    }
    .dashboard-card {
        background: rgba(10, 15, 30, 0.45);
        backdrop-filter: blur(12px);
        border-radius: 28px;
        padding: 1.2rem 1rem;
        margin: 0.5rem;
        border: 1px solid rgba(0, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 255, 255, 0.6);
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .card-icon {
        font-size: 2.5rem;
    }
    .card-title {
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #aaf;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .card-value {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff, cyan);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        line-height: 1.2;
    }
    .card-footer {
        font-size: 0.7rem;
        color: rgba(0, 255, 255, 0.7);
        margin-top: 8px;
    }
    .stButton>button {
        background: rgba(0,20,40,0.7) !important;
        border: 1px solid #0ff !important;
        border-radius: 40px !important;
        color: #0ff !important;
        font-weight: bold;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background: rgba(0,255,255,0.15) !important;
        border-color: magenta !important;
        color: magenta !important;
    }
    .stTextInput>div>div>input {
        background: rgba(0, 10, 20, 0.7) !important;
        border: 1px solid #0ff !important;
        border-radius: 16px !important;
        color: #0ff !important;
    }
    .badge-admin {
        background: linear-gradient(135deg, cyan, magenta);
        padding: 4px 15px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 11px;
        color: #000;
    }
    .info-item {
        margin-bottom: 12px;
        font-size: 13px;
        display: flex;
        gap: 8px;
        color: #eef !important;
    }
    .footer {
        text-align: center;
        padding: 15px;
        color: #6b7280;
        font-size: 9px;
        border-top: 1px solid rgba(0,255,255,0.1);
        margin-top: 25px;
    }
    .cache-status {
        background: rgba(0,255,255,0.1);
        border: 1px solid rgba(0,255,255,0.3);
        border-radius: 10px;
        padding: 4px 12px;
        font-size: 11px;
        color: #0ff;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0,0,0,0.5);
        padding: 4px 12px;
        border-radius: 40px;
        font-size: 12px;
        border: 1px solid #0ff;
        color: #0ff;
    }
    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #0f0;
        border-radius: 50%;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.4; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1.2); }
    }
    .session-indicator {
        background: rgba(0,0,0,0.6);
        border-radius: 30px;
        padding: 4px 12px;
        font-size: 12px;
        color: #0ff;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #eef !important;
    }
</style>
""", unsafe_allow_html=True)

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    st.markdown('<style>.stApp{background:radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);}</style>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style="text-align: center;">
                <div style="font-size: 48px;">🛡️</div>
                <h1 style="background: linear-gradient(135deg, #fff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">JOHN ACESSOS</h1>
                <p style="color: #a78bfa; letter-spacing: 3px;">CYBER SECURITY 2026</p>
                <p style="color: #4a9a6a; font-size: 11px; margin-top: 5px;">🧠 IA Engine v{engine.versao}</p>
            </div>
        """.format(engine=engine), unsafe_allow_html=True)
        
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

# ====================== EXECUÇÃO AUTÔNOMA DA IA (TIMER) ======================
agora_timestamp = time.time()
if agora_timestamp - st.session_state.ultimo_ciclo_ia >= st.session_state.intervalo_ia:
    # Executa a IA em background (sem spinner para não bloquear)
    engine.analisar_agora()
    st.session_state.ultimo_ciclo_ia = agora_timestamp

# ====================== HEADER ======================
st.markdown(f"""
<div style="background: rgba(8,8,20,0.6); backdrop-filter: blur(8px); border-radius: 20px; padding: 10px 20px; margin-bottom: 20px; border: 1px solid cyan;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div style="display:flex; gap:15px; align-items:center;">
            <div style="width:45px;height:45px;">
                <img src="{st.session_state.avatar_url}" style="width:45px; height:45px; border-radius:50%; object-fit:cover; border:1px solid cyan; box-shadow:0 0 8px cyan;">
            </div>
            <div>
                <h1 style="margin:0;font-size:18px; background:linear-gradient(135deg,cyan,magenta); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">JOHN ACESSOS - CYBER SECURITY 2026</h1>
                <p style="margin:0;color:#aaf;font-size:10px;">🧠 IA ENGINE • MOTOR AUTÔNOMO</p>
            </div>
        </div>
        <div style="display:flex; gap:15px; align-items:center; flex-wrap:wrap;">
            <div class="live-indicator"><span class="pulse-dot"></span> LIVE</div>
            <div class="cache-status">💾 Cache: {cache_estatisticas.get_hit_ratio():.0f}%</div>
            <div class="session-indicator">👥 {total_conectados}</div>
            <div class="badge-admin">👑 {st.session_state.perfil}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ====================== EXIBIÇÃO DE ANOMALIAS ======================
anomalias = engine.estado.get("anomalias", [])
if anomalias:
    st.markdown("### 🚨 Alertas de Segurança")
    for anom in anomalias:
        if anom["severidade"] == "ALTA":
            st.error(f"🚨 **{anom['tipo']}** – {anom['detalhe']} (CPF: {anom['cpf']})")
        else:
            st.warning(f"⚠️ **{anom['tipo']}** – CPF: {anom['cpf']} | Setor: {anom.get('setor', 'N/A')}")
    st.markdown("---")

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
        <img src="{st.session_state.avatar_url}" class="avatar-image">
        <div style="font-size:20px;margin-top:12px;color:#0ff;">👮‍♂️ JOHN ACESSOS</div>
        <p style="color:#0ff;font-size:9px;letter-spacing:2px;">CYBER SECURITY 2026</p>
        <p style="color:#4a9a6a;font-size:8px;">🧠 IA v{engine.versao}</p>
        <p style="color:#4a9a6a;font-size:8px;">⚡ {len(engine.estado['patches'])} patches</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚡ ESTADO")
    st.markdown('<div class="info-item"><span style="color:#0f0;">●</span> IA: ATIVA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-item"><span style="color:#0ff;">●</span> CACHE: {cache_estatisticas.get_hit_ratio():.0f}%</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-item"><span style="color:#f0f;">●</span> AGENTES: 5</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-item"><span style="color:#ff0;">●</span> MEMÓRIAS: {len(engine.estado["memorias"])}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📡 INFO")
    if st.session_state.get("perfil"):
        st.markdown(f"<div class='info-item'>👑 Perfil: {st.session_state.perfil}</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="info-item">📦 Versão: {engine.versao}</div>', unsafe_allow_html=True)
    
    # ====================== SIDEBAR - CONTROLE DA IA AUTÔNOMA ======================
    st.markdown("---")
    with st.sidebar.expander("🤖 IA Autônoma", expanded=False):
        intervalo = st.selectbox("Intervalo de análise (segundos)", [30, 60, 120, 300, 600], index=1)
        st.session_state.intervalo_ia = intervalo
        # Próxima execução
        prox = st.session_state.intervalo_ia - (time.time() - st.session_state.ultimo_ciclo_ia) % st.session_state.intervalo_ia
        st.caption(f"Próxima execução em {prox:.0f}s")
        if st.button("▶️ Executar agora", use_container_width=True):
            with st.spinner("IA em execução..."):
                engine.analisar_agora()
                st.session_state.ultimo_ciclo_ia = time.time()
            st.success("Análise concluída!")
            st.rerun()

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
    with st.sidebar.expander("⏱️ Configurar Horário", expanded=False):
        offset_atual = get_timezone_offset()
        novo_offset = st.number_input("Offset (horas)", value=offset_atual, step=0.5, format="%.1f", key="offset_global")
        if st.button("💾 Salvar Offset", key="salvar_offset"):
            if save_timezone_offset(novo_offset):
                st.success(f"✅ Offset alterado para {novo_offset} horas.")
                st.rerun()
            else:
                st.error("Erro ao salvar offset.")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("🎨 Configurar Tema", expanded=False):
        tipo = st.selectbox("Tipo de fundo", ["Gradiente padrão", "Cor sólida", "Futurista Dinâmico"])
        if tipo == "Cor sólida":
            cor = st.color_picker("Escolha a cor", value="#0a0a1a")
            nova_config = {"type": "solid", "value": cor, "apply_to_login": False}
        elif tipo == "Futurista Dinâmico":
            nova_config = {"type": "futuristic", "value": "futuristic", "apply_to_login": False}
        else:
            nova_config = {"type": "gradient", "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)", "apply_to_login": False}
        if st.button("💾 Salvar Tema"):
            if save_theme_config(nova_config):
                apply_theme_css()
                st.success("Tema atualizado!")
                st.rerun()
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("📤 Compartilhar Dados", expanded=False):
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
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🧠 PAINEL IA ENGINE", use_container_width=True):
        st.session_state.pagina_atual = "ia"
        st.rerun()

# ====================== NAVEGAÇÃO ======================
if st.session_state.get("pagina_atual") == "ia":
    pagina_ia_engine()
    st.stop()

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
    if st.button("🔄 Atualizar Estatísticas", key="refresh_stats_view", use_container_width=True):
        with st.spinner("Atualizando..."):
            if refresh_estatisticas_view():
                st.success("Estatísticas atualizadas!")
                st.rerun()
            else:
                st.error("Falha na atualização.")

# ====================== DASHBOARD ======================
st.markdown("---")
stats = get_estatisticas_cached()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">👥</div><div class="status-indicator" style="display:flex;gap:6px;background:rgba(0,0,0,0.5);padding:4px 10px;border-radius:30px;font-size:0.7rem;color:#0ff;border:1px solid rgba(0,255,255,0.4);">ATIVO</div></div>
        <div class="card-title">PRESENTES</div>
        <div class="card-value">{stats['total_presentes']}</div>
        <div class="card-footer">🟢 ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">📊</div><div class="status-indicator" style="display:flex;gap:6px;background:rgba(0,0,0,0.5);padding:4px 10px;border-radius:30px;font-size:0.7rem;color:#0ff;border:1px solid rgba(0,255,255,0.4);">BASE</div></div>
        <div class="card-title">CADASTRADOS</div>
        <div class="card-value">{stats['total_cadastrados']}</div>
        <div class="card-footer">📋 VERIFICADOS</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="dashboard-card">
        <div class="card-header"><div class="card-icon">🏛️</div><div class="status-indicator" style="display:flex;gap:6px;background:rgba(0,0,0,0.5);padding:4px 10px;border-radius:30px;font-size:0.7rem;color:#0ff;border:1px solid rgba(0,255,255,0.4);">MAPA</div></div>
        <div class="card-title">SETORES ATIVOS</div>
        <div class="card-value">{stats['setores_unicos']}</div>
        <div class="card-footer">📍 MONITORADOS</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    with st.spinner("Carregando análise de fluxo..."):
        fluxo_df = get_fluxo_acesso_por_hora()
        total_hoje = get_total_acessos_hoje()
        
        if fluxo_df is not None and not fluxo_df.empty:
            turno_data = fluxo_df.groupby('turno')['total_acessos'].sum().reset_index()
            cores = {
                '🌅 Manhã (06h-12h)': '#00ffcc',
                '☀️ Tarde (12h-18h)': '#ff6b6b',
                '🌙 Noite (18h-00h)': '#7c3aed',
                '🌙 Madrugada (00h-06h)': '#f59e0b'
            }
            fig = go.Figure(data=[go.Pie(
                labels=turno_data['turno'],
                values=turno_data['total_acessos'],
                hole=0.4,
                marker=dict(colors=[cores.get(t, '#a855f7') for t in turno_data['turno']]),
                textinfo='percent+label',
                textposition='auto'
            )])
            fig.update_layout(
                title=dict(text=f"📊 FLUXO DE ACESSO POR TURNO<br><span style='font-size:12px;'>Total hoje: {total_hoje} acessos</span>", 
                           font=dict(color='#0ff', size=14), x=0.5, xanchor='center'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=280,
                margin=dict(t=50, b=20, l=20, r=20),
                showlegend=False
            )
            
            st.markdown("""
            <div class="dashboard-card" style="padding: 0.5rem;">
                <div class="card-header">
                    <div class="card-icon">📊</div>
                    <div class="status-indicator" style="display:flex;gap:6px;background:rgba(0,0,0,0.5);padding:4px 10px;border-radius:30px;font-size:0.7rem;color:#0ff;border:1px solid rgba(0,255,255,0.4);">FLUXO</div>
                </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("""
                <div class="card-footer" style="justify-content:center;">📊 Análise de fluxo</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="dashboard-card">
                <div class="card-header"><div class="card-icon">📊</div><div class="status-indicator" style="display:flex;gap:6px;background:rgba(0,0,0,0.5);padding:4px 10px;border-radius:30px;font-size:0.7rem;color:#0ff;border:1px solid rgba(0,255,255,0.4);">FLUXO</div></div>
                <div class="card-title">ANÁLISE DE FLUXO</div>
                <div style="text-align:center;padding:20px;color:#aaa;">Nenhum dado registrado</div>
                <div class="card-footer">⏳ AGUARDANDO DADOS</div>
            </div>
            """, unsafe_allow_html=True)

# ====================== CADASTRO ======================
st.markdown("---")
st.markdown("### ✚ Cadastro de Nova Pessoa")
with st.expander("📋 Formulário de Cadastro", expanded=False):
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

# Define os destinos padrão
if tipo == "🏢 Prestador de serviços":
    destinos_padrao = ["🏥 C.C PRESTADOR DE SERVIÇOS", "🥼 HEPIDEMIOLOGIA", "👨🏻‍💻 T.I", "🧺LAVANDERIA", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção", "👨‍🔬 Laboratório", "💊 Farmacia", "🏥 P.A", "👶 PEDIATRIA P.A", "⚙️ ENG.CLINICA", "🧹 HOTELARIA", "📦 OPME 6°AND", "📦 OPME 9°AND", "🔒 SSGA", "🏥 CDU", "⚕️ ONCOLOGIA", "🛠️ PREST_BRASANITAS ", "🛠️ PREST_GRSA"]
else:
    destinos_padrao = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

# Adiciona a opção "Outro"
destinos_com_outro = destinos_padrao + ["📝 Outro (digitar)"]

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

# Seleção do destino
setor_escolhido = st.selectbox("📍 Destino:", destinos_com_outro, key="destino")

# Se a opção "Outro" for escolhida, exibe campo de texto
if setor_escolhido == "📝 Outro (digitar)":
    setor_digitado = st.text_input("✏️ Digite o nome do setor:", placeholder="Ex: Almoxarifado", key="setor_digitado")
    setor_final = sanitizar_texto(setor_digitado).strip().upper() if setor_digitado else ""
else:
    setor_final = setor_escolhido

if st.session_state.get("pessoa_confirmada"):
    responsavel = st.text_input("👤 Responsável pela liberação:", placeholder="Nome completo do responsável", key="responsavel_entrada")
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
    
    if setor_escolhido == "📝 Outro (digitar)" and not setor_final:
        st.warning("⚠️ Por favor, digite o nome do setor.")
    
    if st.button("✅ Registrar Entrada", key="btn_entrada", type="primary"):
        if not responsavel.strip():
            st.error("❌ O campo 'Responsável pela liberação' é obrigatório.")
        elif setor_escolhido == "📝 Outro (digitar)" and not setor_final:
            st.error("❌ O campo 'Setor digitado' é obrigatório.")
        else:
            p = st.session_state.pessoa_confirmada
            try:
                supabase.table("movimentacao").insert({
                    "cpf": p['cpf'],
                    "nome": p['nome'],
                    "empresa": p['empresa'],
                    "setor_destino": setor_final,
                    "data_entrada": data_entrada_str,
                    "data_saida": "",
                    "responsavel_liberacao": responsavel.strip().upper()
                }).execute()
                invalidar_cache()
                st.success(f"Entrada registrada para {setor_final} às {data_entrada_str}!")
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
    setores_terceirizados_exatos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]
    
    tabs = st.tabs(["📊 Prestador de Serviço", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"])
    
    with tabs[0]:
        prestadores = [p for p in dados if p['setor_destino'] not in setores_terceirizados_exatos]
        if prestadores:
            for p in prestadores:
                col1, col2, col3, col4 = st.columns([4,3,2,2])
                col1.write(f"**{p['nome']}**")
                col2.write(f"📍 {p['setor_destino']}")
                col3.write(f"🏢 {p.get('empresa','N/A')}")
                with col4:
                    with st.popover("🚪 Saída"):
                        st.write(f"Registrar saída de **{p['nome']}**")
                        with st.expander("⏱️ Horário", expanded=False):
                            editar_horario_saida = st.checkbox("Editar horário", key=f"edit_saida_prest_{p['id']}")
                            if editar_horario_saida:
                                dt_padrao = get_current_datetime()
                                data_s = st.date_input("Data", value=dt_padrao.date(), key=f"data_saida_prest_{p['id']}")
                                hora_s = st.time_input("Hora", value=dt_padrao.time(), key=f"hora_saida_prest_{p['id']}")
                                dt_saida = datetime.combine(data_s, hora_s)
                                saida_str = format_datetime_str(dt_saida)
                            else:
                                saida_str = format_datetime_str(get_current_datetime())
                        if st.button("Confirmar Saída", key=f"confirm_saida_prest_{p['id']}"):
                            try:
                                supabase.table("movimentacao").update({"data_saida": saida_str}).eq("id", p['id']).execute()
                                invalidar_cache()
                                st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
        else:
            st.info("Nenhum prestador de serviço presente no momento.")
    
    with tabs[1]:
        pessoas_cc = [p for p in dados if p['setor_destino'] == "🏥 C.C"]
        if pessoas_cc:
            for p in pessoas_cc:
                col1, col2, col3, col4 = st.columns([4,3,2,2])
                col1.write(f"**{p['nome']}**")
                col2.write(f"🏢 {p.get('empresa','N/A')}")
                col3.write(f"🕒 {p['data_entrada']}")
                with col4:
                    with st.popover("🚪 Saída"):
                        st.write(f"Registrar saída de **{p['nome']}**")
                        with st.expander("⏱️ Horário", expanded=False):
                            editar_horario_saida = st.checkbox("Editar horário", key=f"edit_saida_cc_{p['id']}")
                            if editar_horario_saida:
                                dt_padrao = get_current_datetime()
                                data_s = st.date_input("Data", value=dt_padrao.date(), key=f"data_saida_cc_{p['id']}")
                                hora_s = st.time_input("Hora", value=dt_padrao.time(), key=f"hora_saida_cc_{p['id']}")
                                dt_saida = datetime.combine(data_s, hora_s)
                                saida_str = format_datetime_str(dt_saida)
                            else:
                                saida_str = format_datetime_str(get_current_datetime())
                        if st.button("Confirmar Saída", key=f"confirm_saida_cc_{p['id']}"):
                            try:
                                supabase.table("movimentacao").update({"data_saida": saida_str}).eq("id", p['id']).execute()
                                invalidar_cache()
                                st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
        else:
            st.info("Ninguém presente no setor C.C.")
    
    with tabs[2]:
        pessoas_gr = [p for p in dados if p['setor_destino'] == "🔧 GRSA"]
        if pessoas_gr:
            for p in pessoas_gr:
                col1, col2, col3, col4 = st.columns([4,3,2,2])
                col1.write(f"**{p['nome']}**")
                col2.write(f"🏢 {p.get('empresa','N/A')}")
                col3.write(f"🕒 {p['data_entrada']}")
                with col4:
                    with st.popover("🚪 Saída"):
                        st.write(f"Registrar saída de **{p['nome']}**")
                        with st.expander("⏱️ Horário", expanded=False):
                            editar_horario_saida = st.checkbox("Editar horário", key=f"edit_saida_gr_{p['id']}")
                            if editar_horario_saida:
                                dt_padrao = get_current_datetime()
                                data_s = st.date_input("Data", value=dt_padrao.date(), key=f"data_saida_gr_{p['id']}")
                                hora_s = st.time_input("Hora", value=dt_padrao.time(), key=f"hora_saida_gr_{p['id']}")
                                dt_saida = datetime.combine(data_s, hora_s)
                                saida_str = format_datetime_str(dt_saida)
                            else:
                                saida_str = format_datetime_str(get_current_datetime())
                        if st.button("Confirmar Saída", key=f"confirm_saida_gr_{p['id']}"):
                            try:
                                supabase.table("movimentacao").update({"data_saida": saida_str}).eq("id", p['id']).execute()
                                invalidar_cache()
                                st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
        else:
            st.info("Ninguém presente no setor GRSA.")
    
    with tabs[3]:
        pessoas_br = [p for p in dados if p['setor_destino'] == "🏭 Brasanitas"]
        if pessoas_br:
            for p in pessoas_br:
                col1, col2, col3, col4 = st.columns([4,3,2,2])
                col1.write(f"**{p['nome']}**")
                col2.write(f"🏢 {p.get('empresa','N/A')}")
                col3.write(f"🕒 {p['data_entrada']}")
                with col4:
                    with st.popover("🚪 Saída"):
                        st.write(f"Registrar saída de **{p['nome']}**")
                        with st.expander("⏱️ Horário", expanded=False):
                            editar_horario_saida = st.checkbox("Editar horário", key=f"edit_saida_br_{p['id']}")
                            if editar_horario_saida:
                                dt_padrao = get_current_datetime()
                                data_s = st.date_input("Data", value=dt_padrao.date(), key=f"data_saida_br_{p['id']}")
                                hora_s = st.time_input("Hora", value=dt_padrao.time(), key=f"hora_saida_br_{p['id']}")
                                dt_saida = datetime.combine(data_s, hora_s)
                                saida_str = format_datetime_str(dt_saida)
                            else:
                                saida_str = format_datetime_str(get_current_datetime())
                        if st.button("Confirmar Saída", key=f"confirm_saida_br_{p['id']}"):
                            try:
                                supabase.table("movimentacao").update({"data_saida": saida_str}).eq("id", p['id']).execute()
                                invalidar_cache()
                                st.success(f"Saída registrada para {p['nome']} às {saida_str}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
        else:
            st.info("Ninguém presente no setor Brasanitas.")
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
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("📑 Relatório completo", key="relatorio_completo"):
                html = gerar_html_impressao(df, "RELATÓRIO COMPLETO")
                if html:
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir relatório (Ctrl+P para PDF)</a>', unsafe_allow_html=True)
        with col_r2:
            if st.button("📑 Consolidado", key="relatorio_consolidado"):
                html = gerar_html_consolidado(df)
                if html:
                    b64 = base64.b64encode(html.encode()).decode()
                    st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir consolidado</a>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 🗑️ Gerenciar Registros")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("✅ Selecionar Todos da Página", key="selecionar_todos_pagina", use_container_width=True):
                ids_pagina = [row['id'] for row in historico["dados"]]
                for id_ in ids_pagina:
                    if id_ not in st.session_state.selected_ids:
                        st.session_state.selected_ids.append(id_)
                st.rerun()
        
        with col_btn2:
            if st.button("📋 Limpar Seleção", key="limpar_selecao_todos", use_container_width=True):
                st.session_state.selected_ids = []
                st.rerun()
        
        with col_btn3:
            if st.button("⚠️ EXCLUIR TUDO", key="excluir_tudo_historico", use_container_width=True):
                st.session_state.pending_clear_all = True
                st.rerun()
        
        if st.session_state.selected_ids:
            st.warning(f"⚠️ {len(st.session_state.selected_ids)} registro(s) selecionado(s)")
            
            col_excluir, col_cancelar = st.columns(2)
            with col_excluir:
                if st.button("🗑️ EXCLUIR SELECIONADOS", key="excluir_selecionados_lote", type="primary", use_container_width=True):
                    resultado = excluir_multiplos_registros(st.session_state.selected_ids)
                    if resultado["sucesso"]:
                        st.success(resultado["mensagem"])
                        st.session_state.selected_ids = []
                        invalidar_cache()
                        st.rerun()
                    else:
                        st.error(resultado["mensagem"])
            with col_cancelar:
                if st.button("❌ Cancelar Seleção", key="cancelar_selecao_lote", use_container_width=True):
                    st.session_state.selected_ids = []
                    st.rerun()
        
        st.markdown("---")
        
        for row in historico["dados"]:
            col_check, col_data = st.columns([0.5, 9.5])
            with col_check:
                checked = st.checkbox("", key=f"chk_{row['id']}", value=row['id'] in st.session_state.selected_ids)
                if checked and row['id'] not in st.session_state.selected_ids:
                    st.session_state.selected_ids.append(row['id'])
                elif not checked and row['id'] in st.session_state.selected_ids:
                    st.session_state.selected_ids.remove(row['id'])
            with col_data:
                st.markdown(f"ID {row['id']} - **{row['nome']}** | CPF: {row['cpf']} | Empresa: {row.get('empresa','N/A')} | Entrada: {row['data_entrada']} | Saída: {row['data_saida'] or 'Presente'}")
                st.markdown("<hr style='margin:3px 0; opacity:0.1;'>", unsafe_allow_html=True)
        
        if st.session_state.pending_clear_all:
            require_admin()
            st.error("🚨 ATENÇÃO: Isso irá apagar TODOS os registros do histórico!")
            st.warning("Digite 'LIMPAR TUDO' para confirmar a exclusão permanente.")
            confirm = st.text_input("Confirmação:", type="password", key="confirma_limpar_tudo")
            
            col_clear, col_cancel_clear = st.columns(2)
            with col_clear:
                if st.button("🔥 EXCLUIR TUDO (IRREVERSÍVEL)", key="excluir_tudo_confirm", type="primary", use_container_width=True):
                    if confirm == "LIMPAR TUDO":
                        try:
                            supabase_admin.table("movimentacao").delete().neq("id", 0).execute()
                            invalidar_cache()
                            st.success("✅ Histórico limpo com sucesso!")
                            st.session_state.pending_clear_all = False
                            st.session_state.selected_ids = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {e}")
                    else:
                        st.error("❌ Confirmação incorreta. Digite 'LIMPAR TUDO'")
            with col_cancel_clear:
                if st.button("❌ Cancelar", key="cancelar_limpar_tudo", use_container_width=True):
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
st.markdown(f"""
<div class="footer">
    🛡️ JOHN ACESSOS - CYBER SECURITY 2026 | Monitoramento Inteligente & Proteção de Dados
    <br>
    🧠 IA Engine v{engine.versao} | {len(engine.estado['patches'])} patches | {len(engine.estado['memorias'])} memórias | 5 agentes
    <br>
    ⏱️ Auto-otimização ativa | Próxima análise em {st.session_state.intervalo_ia - (time.time() - st.session_state.ultimo_ciclo_ia) % st.session_state.intervalo_ia:.0f}s
</div>
""", unsafe_allow_html=True)
