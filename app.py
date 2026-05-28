import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image
import base64
import re
import uuid

# --- CONFIGURAÇÃO ---
MAX_TENTATIVAS_LOGIN = 5
SESSION_TIMEOUT_MINUTOS = 2  # 2 minutos para teste

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(
    page_title="JOHN ACESSOS - ACESSO DE DADOS",
    layout="wide",
    page_icon="👮‍♂️",
    initial_sidebar_state="expanded"
)

# ====================== FUNÇÕES DE SESSÃO COM DIAGNÓSTICO ======================
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
        st.toast(f"✅ Sessão registrada: {session_id[:8]}", icon="✅")
        return True
    except Exception as e:
        st.error(f"❌ Erro ao registrar sessão: {e}")
        return False

def atualizar_atividade_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").update({
                "ultima_atividade": datetime.now().isoformat()
            }).eq("id", st.session_state.session_id).execute()
        except Exception as e:
            st.warning(f"⚠️ Erro ao atualizar sessão: {e}")

def remover_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").delete().eq("id", st.session_state.session_id).execute()
            st.toast("🔒 Sessão removida", icon="🔒")
        except:
            pass
        st.session_state.session_id = None

def contar_sessoes_ativas():
    limite = (datetime.now() - pd.Timedelta(minutes=SESSION_TIMEOUT_MINUTOS)).isoformat()
    try:
        result = supabase.table("sessoes_ativas").select("id", count="exact").gte("ultima_atividade", limite).execute()
        return result.count
    except Exception as e:
        st.error(f"❌ Erro ao contar sessões: {e}")
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
                <tr>{cabecalho_html}</td>
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

# ====================== VALIDAÇÕES ======================
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

# ====================== DESIGN BASE (apenas um trecho para encurtar; na prática é grande) ======================
# ... (mantenha o design CSS idêntico ao código que você já tem, para não perder espaço) ...
# Vou assumir que o CSS já está correto e não o repetirei aqui para evitar limites.

# ====================== SIDEBAR ======================
# ... (mantenha igual ao seu código atual) ...

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

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    # ... (todo o HTML da tela de login, igual ao seu código atual) ...
    # Ao submeter o formulário:
    with st.form("login_form"):
        st.text_input("", placeholder="Identificação (usuário)", key="data_user", label_visibility="collapsed")
        senha = st.text_input("", type="password", placeholder="Chave de acesso criptografada", label_visibility="collapsed")
        submitted = st.form_submit_button("👮‍♂️ ACESSAR SISTEMA", use_container_width=True)
        if submitted:
            if senha == "fgxv4VP0/*":
                st.session_state.logado = True
                st.session_state.perfil = "ADMIN"
                st.session_state.tentativas_login = 0
                if registrar_sessao("ADMIN", "admin"):
                    st.rerun()
                else:
                    st.error("Falha ao registrar sessão. Verifique a tabela 'sessoes_ativas' no Supabase.")
            elif senha == "JOHN123":
                st.session_state.logado = True
                st.session_state.perfil = "VIGILANTE"
                st.session_state.tentativas_login = 0
                registrar_sessao("VIGILANTE", "vigilante")
                st.rerun()
            else:
                # ... (tratamento de erro) ...
    st.stop()

# ====================== APÓS LOGIN ======================
if st.session_state.session_id:
    atualizar_atividade_sessao()
    limpar_sessoes_expiradas()
    total_conectados = contar_sessoes_ativas()
else:
    total_conectados = 0

alerta_monitoramento = total_conectados > 1

# ====================== HEADER COM INDICADOR ======================
indicador_html = f'<div class="session-indicator">{"⚠️ " if alerta_monitoramento else ""}<span>👥 {total_conectados}</span></div>'

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

# ... (restante do código: dashboard, cadastro, etc. igual ao seu código atual) ...
