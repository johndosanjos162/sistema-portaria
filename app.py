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
    page_title="JOHN ACESSOS - CENTRAL TÁTICA", 
    layout="wide", 
    page_icon="🛡️", 
    initial_sidebar_state="expanded"
)

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
            linhas_html += f"<td>{valor}</td>"
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
        <h1>JOHN ACESSOS - CENTRAL TÁTICA - {titulo}</h1>
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
        </div>
    </body>
    </html>
    """
    return html

# ====================== CARREGAR IMAGENS ======================
def carregar_imagem(nome_arquivo, nome_descricao):
    try:
        return Image.open(nome_arquivo)
    except:
        return None

IMAGEM_LOGIN = carregar_imagem("login_image.png", "Login")
IMAGEM_SIDEBAR = carregar_imagem("sidebar_logo.png", "Sidebar")
IMAGEM_HEADER = carregar_imagem("header_logo.png", "Header")

# ====================== DESIGN MILITAR ESTÁVEL ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Share+Tech+Mono&display=swap');

/* FUNDO - gradiente escuro estável */
.stApp {
    background: linear-gradient(145deg, #030712 0%, #0a0f1a 100%);
    font-family: 'Orbitron', 'Share Tech Mono', monospace;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(8px);
    border-right: 1px solid #0ff;
}
.sidebar-header {
    text-align: center;
    padding: 20px 10px;
    border-bottom: 1px solid #0ff;
}
.sidebar-title {
    font-size: 22px;
    font-weight: 900;
    background: linear-gradient(135deg, #0ff, #0f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.info-item {
    margin-bottom: 10px;
    color: #0ff;
    font-size: 12px;
    display: flex;
    gap: 8px;
}

/* CABEÇALHO */
.admin-header {
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(8px);
    border-radius: 15px;
    padding: 12px 20px;
    margin-bottom: 20px;
    border: 1px solid #0ff;
}
.badge-admin {
    background: linear-gradient(135deg, #0ff, #0f0);
    padding: 4px 15px;
    border-radius: 20px;
    font-weight: 800;
    font-size: 11px;
    color: black;
}

/* CARDS */
.admin-card {
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(6px);
    border-radius: 15px;
    padding: 15px;
    border: 1px solid #0ff;
    transition: 0.2s;
}
.admin-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 12px #0ff;
}
.card-title {
    font-size: 10px;
    letter-spacing: 1px;
    color: #0ff;
}
.card-value {
    font-size: 28px;
    font-weight: 900;
    background: linear-gradient(135deg, #fff, #0ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* BOTÕES */
.stButton > button, .stForm button {
    border-radius: 40px;
    font-weight: 700;
    font-family: 'Orbitron', monospace;
    background: linear-gradient(90deg, #0ff, #0a0);
    color: black;
    transition: 0.2s;
    border: none;
}
.stButton > button:hover, .stForm button:hover {
    transform: scale(1.01);
    box-shadow: 0 0 12px #0ff;
}
.stButton > button[key="sair_final"] {
    background: linear-gradient(90deg, #f44, #a00);
    color: white;
}

/* INPUTS */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    background: rgba(0, 0, 0, 0.8);
    border: 1px solid #0ff;
    border-radius: 12px;
    color: #0ff;
    font-family: 'Share Tech Mono', monospace;
    padding: 8px;
}
.stTextInput > div > div > input:focus {
    border-color: #0f0;
    box-shadow: 0 0 8px #0ff;
}

/* EXPANDER, TABS */
.streamlit-expanderHeader {
    background: rgba(0, 0, 0, 0.7);
    border: 1px solid #0ff;
    border-radius: 12px;
    color: #0ff;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
    background: rgba(0,0,0,0.5);
    padding: 5px;
    border-radius: 30px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 20px;
    padding: 5px 18px;
    font-weight: 600;
    color: #ccc;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0ff, #0f0);
    color: black;
}
.stCheckbox label {
    color: #0ff;
}
.stDataFrame {
    background: rgba(0,0,0,0.4);
    border-radius: 10px;
    border: 1px solid #0ff;
}
.footer {
    text-align: center;
    padding: 15px;
    color: #0ff;
    font-size: 9px;
    border-top: 1px solid rgba(0,255,255,0.2);
    margin-top: 25px;
}
h1, h2, h3 {
    font-family: 'Orbitron', monospace;
    color: #0ff;
}
hr {
    border-color: rgba(0,255,255,0.2);
}
/* Efeito de código binário */
.binary-line {
    font-family: 'Share Tech Mono', monospace;
    color: #0ff;
    background: rgba(0,0,0,0.6);
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 12px;
    letter-spacing: 2px;
    text-align: center;
    margin-bottom: 15px;
    border: 1px solid #0ff;
    white-space: nowrap;
    overflow-x: auto;
    text-shadow: 0 0 2px #0ff;
}
</style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
if IMAGEM_SIDEBAR:
    st.sidebar.image(IMAGEM_SIDEBAR, use_container_width=True)
else:
    st.sidebar.markdown("""
        <div class="sidebar-header">
            <div class="sidebar-title">🛡️ JOHN ACESSOS</div>
            <p style="color:#0ff; font-size:9px;">CENTRAL TÁTICA</p>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ ESTADO OPERACIONAL")
st.sidebar.markdown('<div class="info-item">🟢 CFTV: ATIVO</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🤖 IA: MONITORANDO</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🔒 CRIPTOGRAFIA: 256-BIT</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🗄️ BANCO DE DADOS: SEGURO</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📡 INFORMAÇÕES")
if "perfil" in st.session_state:
    st.sidebar.markdown(f"<div class='info-item'>👑 Perfil: {st.session_state.perfil}</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<div class='info-item'>👑 Perfil: ---</div>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">🟢 Status: Online</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="info-item">📦 Versão: 8.6</div>', unsafe_allow_html=True)

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

# ====================== TELA DE LOGIN COM CÓDIGO BINÁRIO ======================
if not st.session_state.logado:
    # HTML/JavaScript para a linha de código binário animada
    st.markdown("""
    <style>
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 85vh;
    }
    .login-box {
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 35px 25px;
        border: 1px solid #0ff;
        box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
        width: 100%;
        max-width: 420px;
        text-align: center;
    }
    .military-shield {
        width: 90px;
        height: 90px;
        margin: 0 auto 15px;
        background: radial-gradient(circle, rgba(0,255,255,0.15), transparent);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .military-shield span {
        font-size: 45px;
        filter: drop-shadow(0 0 5px #0ff);
    }
    .logo-title {
        font-size: 26px;
        font-weight: 900;
        background: linear-gradient(135deg, #fff, #0ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .logo-subtitle {
        font-size: 9px;
        color: #0ff;
        letter-spacing: 2px;
    }
    .binary-line {
        font-family: 'Share Tech Mono', monospace;
        background: rgba(0,0,0,0.6);
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #0ff;
        white-space: nowrap;
        overflow-x: auto;
        text-shadow: 0 0 2px #0ff;
    }
    .status-bar {
        margin-top: 20px;
        font-size: 9px;
        color: #0ff;
        border-top: 1px solid rgba(0,255,255,0.2);
        padding-top: 10px;
    }
    .status-item {
        display: inline-block;
        margin: 0 5px;
    }
    .blink {
        display: inline-block;
        width: 6px;
        height: 6px;
        background: #0f0;
        border-radius: 50%;
        margin-right: 4px;
    }
    </style>
    <div id="binary-container" style="margin-bottom:15px;"></div>
    <script>
        function generateRandomBinary(length = 50) {
            let binary = '';
            for (let i = 0; i < length; i++) {
                binary += Math.random() < 0.5 ? '0' : '1';
            }
            return binary;
        }
        function updateBinary() {
            const container = document.getElementById('binary-container');
            if (container) {
                const binaryString = generateRandomBinary(60);
                container.innerHTML = `<div class="binary-line">${binaryString}</div>`;
            }
        }
        setInterval(updateBinary, 300);
        updateBinary();
    </script>
    <div class="login-container">
        <div class="login-box">
            <div class="military-shield"><span>🛡️</span></div>
            <div class="logo-title">JOHN ACESSOS</div>
            <div class="logo-subtitle">CENTRAL TÁTICA</div>
            <div style="height: 15px;"></div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        # O campo senha virá depois do binário
        senha = st.text_input("", type="password", placeholder="Credencial de segurança", label_visibility="collapsed")
        submitted = st.form_submit_button("🔓 ACESSAR SISTEMA", use_container_width=True)
        if submitted:
            if senha == "fgxv4VP0/*":
                st.session_state.logado = True
                st.session_state.perfil = "ADMIN"
                st.rerun()
            elif senha == "JOHN123":
                st.session_state.logado = True
                st.session_state.perfil = "VIGILANTE"
                st.rerun()
            else:
                st.error("❌ ACESSO NEGADO")
    
    st.markdown("""
            <div class="status-bar">
                <div class="status-item"><span class="blink"></span> CFTV ONLINE</div>
                <div class="status-item"><span class="blink"></span> IA MONITORANDO</div>
                <div class="status-item"><span class="blink"></span> CRIPTOGRAFIA ATIVA</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ====================== HEADER APÓS LOGIN ======================
st.markdown(f"""
    <div class="admin-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #0ff, #0a0); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 20px;">🛡️</span>
                </div>
                <div>
                    <h1 style="margin:0; font-size: 16px;">JOHN ACESSOS - CENTRAL TÁTICA</h1>
                    <p style="margin:0; color: #0ff; font-size: 8px;">INTELIGÊNCIA DE DEFESA</p>
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
                <div style="font-size:24px;">👥</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">📋 CADASTRADOS</div><div class="card-value">{total_colaboradores}</div></div>
                <div style="font-size:24px;">📊</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">🏥 SETORES</div><div class="card-value">11</div></div>
                <div style="font-size:24px;">🏛️</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
        <div class="admin-card">
            <div style="display:flex; justify-content:space-between;">
                <div><div class="card-title">🎥 CFTV</div><div class="card-value">24/7</div></div>
                <div style="font-size:24px;">📹</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ====================== CADASTRO ======================
st.markdown("---")
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

# ====================== REGISTRO DE ENTRADA ======================
st.markdown("---")
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

# ====================== GESTÃO DE CADASTROS ======================
st.markdown("---")
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
                        <div style="background:rgba(0,255,255,0.1); border-radius:10px; padding:10px; border-left:3px solid #0ff;">
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

st.markdown("---")
st.markdown("""
    <div class="footer">
        🛡️ JOHN ACESSOS - CENTRAL TÁTICA | IA | DEFESA AVANÇADA
    </div>
""", unsafe_allow_html=True)
