import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐", initial_sidebar_state="expanded")

# ====================== CARREGAR IMAGENS ======================
# ⚠️ ALTERE OS NOMES DOS ARQUIVOS CONFORME SUAS IMAGENS ⚠️
# Coloque as imagens na mesma pasta do seu script

def carregar_imagem(nome_arquivo, nome_descricao):
    """Tenta carregar uma imagem e retorna None se não encontrar"""
    try:
        return Image.open(nome_arquivo)
    except:
        return None

# Configure aqui os nomes dos seus arquivos de imagem
# Exemplo: "logo.png", "fundo_login.jpg", "icone.png"
IMAGEM_LOGIN = carregar_imagem("login_image.png", "Login")
IMAGEM_SIDEBAR = carregar_imagem("sidebar_logo.png", "Sidebar")
IMAGEM_HEADER = carregar_imagem("header_logo.png", "Header")

# ====================== ESTILO ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0f1e 0%, #0f172a 100%);
        color: #e0f2fe;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar personalizada */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid #334155;
    }
    
    .sidebar-title {
        font-size: 26px;
        font-weight: 700;
        background: linear-gradient(135deg, #67e8f9, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 25px 0 15px 0;
    }
    
    h1 {
        background: linear-gradient(135deg, #67e8f9, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 34px !important;
        font-weight: 700;
        margin: 0 !important;
    }
    
    /* Botões principais */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        border: none;
        cursor: pointer;
    }
    
    div.stButton > button:not([key="sair_final"]):not([key="login_btn"]) {
        background: linear-gradient(90deg, #10b981, #34d399);
        color: #0f172a;
        border: 1px solid #34d399;
    }
    
    div.stButton > button:not([key="sair_final"]):not([key="login_btn"]):hover {
        background: linear-gradient(90deg, #34d399, #6ee7b7);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    div.stButton > button[key="sair_final"] {
        background: linear-gradient(90deg, #ef4444, #f87171);
        color: white;
    }
    
    div.stButton > button[key="sair_final"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
    }
    
    div.stButton > button[key="login_btn"] {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        color: white;
        font-size: 18px;
        font-weight: 700;
    }
    
    div.stButton > button[key="login_btn"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #e0f2fe;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #34d399;
        box-shadow: 0 0 0 2px rgba(52, 211, 153, 0.2);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: #0f172a;
    }
    
    /* Cards/Metrics */
    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    
    /* Alertas */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 20px;
    }
    
    .stRadio label {
        font-weight: 500;
    }
    
    /* Campo de pesquisa com lupa */
    .search-container {
        position: relative;
        margin-bottom: 20px;
    }
    
    .search-container input {
        padding-left: 40px !important;
    }
    
    .search-icon {
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 18px;
        color: #67e8f9;
        z-index: 1;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
# Adicionar logo na sidebar
if IMAGEM_SIDEBAR:
    st.sidebar.image(IMAGEM_SIDEBAR, use_container_width=True)

st.sidebar.markdown("<div class='sidebar-title'>🔐 ACCESS GATE</div>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Menu com ícones
st.sidebar.markdown("### 📌 MENU PRINCIPAL")
st.sidebar.markdown("- 🏠 **Dashboard**")
st.sidebar.markdown("- 👥 **Colaboradores**")
st.sidebar.markdown("- 🔧 **Prestadores**")
st.sidebar.markdown("- 🕒 **Histórico**")
st.sidebar.markdown("- ⚙️ **Configurações**")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ INFORMAÇÕES")
st.sidebar.markdown("Versão: **2.0.0**")
st.sidebar.markdown("Status: 🟢 **Online**")

# ====================== SESSÃO ======================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "perfil" not in st.session_state:
    st.session_state.perfil = ""
if "search_term" not in st.session_state:
    st.session_state.search_term = ""

# ====================== LOGIN ======================
if not st.session_state.logado:
    # Container centralizado
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Card de login
        with st.container():
            st.markdown("""
                <div style="
                    background: rgba(30, 41, 59, 0.8);
                    backdrop-filter: blur(10px);
                    border-radius: 24px;
                    padding: 40px;
                    border: 1px solid #334155;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                ">
            """, unsafe_allow_html=True)
            
            # Título
            st.markdown("<h1 style='text-align:center;'>🔐 ACCESS GATE</h1>", unsafe_allow_html=True)
            
            # Imagem de login (substitui o círculo)
            if IMAGEM_LOGIN:
                st.image(IMAGEM_LOGIN, use_container_width=True)
            else:
                # Fallback visual se não tiver imagem
                st.markdown("""
                    <div style='text-align:center; margin: 20px 0;'>
                        <div style='
                            width: 200px; 
                            height: 200px; 
                            margin: 0 auto; 
                            background: linear-gradient(135deg, #10b981, #3b82f6);
                            border-radius: 50%; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center;
                            box-shadow: 0 0 50px rgba(16, 185, 129, 0.5);
                        '>
                            <div style='font-size: 80px;'>🔑</div>
                        </div>
                        <p style='margin-top: 15px; font-size: 20px; font-weight: bold; color: #67e8f9;'>
                            ACESSO SEGURO
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 25px 0; border-color: #334155;'>", unsafe_allow_html=True)
            
            # Formulário de login
            st.markdown("<h3 style='text-align:center; color:#67e8f9;'>🔑 ACESSO COM SENHA</h3>", unsafe_allow_html=True)
            
            senha = st.text_input(
                "Digite sua senha de acesso:", 
                type="password", 
                key="senha_login",
                placeholder="••••••••"
            )
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🔓 ENTRAR NO SISTEMA", key="login_btn", use_container_width=True):
                    if senha == "fgxv4VP0/*":
                        st.session_state.logado = True
                        st.session_state.perfil = "ADMIN"
                        st.rerun()
                    elif senha == "JOHN123":
                        st.session_state.logado = True
                        st.session_state.perfil = "VIGILANTE"
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta! Tente novamente.")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# ====================== HEADER ======================
col1, col2, col3, col4 = st.columns([1, 6, 2, 2])

with col1:
    if IMAGEM_HEADER:
        st.image(IMAGEM_HEADER, width=60)
    else:
        st.markdown("<div style='font-size: 40px;'>🔐</div>", unsafe_allow_html=True)

with col2:
    st.title("ACCESS GATE - PAINEL DE CONTROLE")

with col3:
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #1e293b, #334155);
            padding: 8px 16px;
            border-radius: 20px;
            text-align: center;
        '>
            <span style='font-size: 14px;'>👤 PERFIL</span><br>
            <span style='color:#67e8f9; font-weight: bold;'>{st.session_state.perfil}</span>
        </div>
    """, unsafe_allow_html=True)

with col4:
    if st.button("🚪 DESCONECTAR", key="sair_final", use_container_width=True):
        st.session_state.logado = False
        st.rerun()

st.markdown("---")

# ====================== DASHBOARD RÁPIDO ======================
# Mostrar métricas rápidas
col_metric1, col_metric2, col_metric3 = st.columns(3)

# Buscar dados para métricas
pessoas_presentes = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
total_presentes = len(pessoas_presentes)
total_colaboradores = len(supabase.table("Pessoas").select("*").execute().data)

with col_metric1:
    st.metric("📍 Pessoas Presentes", total_presentes, delta=None)
with col_metric2:
    st.metric("👥 Total Cadastrados", total_colaboradores, delta=None)
with col_metric3:
    st.metric("📊 Movimentações Hoje", "---", delta=None)

st.markdown("---")

# ====================== CADASTRO SIMPLIFICADO ======================
st.subheader("➕ Cadastro de Nova Pessoa")

with st.expander("📋 Adicionar Novo Colaborador / Prestador", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("CPF *", key="novo_cpf", placeholder="000.000.000-00")
    novo_nome = col_b.text_input("Nome Completo *", key="novo_nome", placeholder="Digite o nome completo")
    novo_empresa = col_c.text_input("Empresa", key="novo_empresa", placeholder="Empresa (opcional)")
    
    if st.button("💾 Salvar Cadastro", key="salvar_cadastro", type="primary"):
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
                st.error(f"❌ Erro ao salvar: {e}")
        else:
            st.error("❌ CPF e Nome Completo são obrigatórios.")

# ====================== REGISTRO DE ENTRADA ======================
st.subheader("📋 Registrar Nova Entrada")

tipo = st.radio("Tipo de Pessoa:", ["Colaborador Interno", "Prestador de Serviço"], horizontal=True)

if tipo == "Colaborador Interno":
    destinos = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Laboratório", "Farmacia"]
else:
    destinos = ["C.C", "GRSA", "Brasanitas"]

c1, c2, c3 = st.columns([2, 2, 1])
cpf_input = c1.text_input("CPF:", key="cpf_entrada", placeholder="Digite o CPF")
setor_escolhido = c2.selectbox("Destino:", destinos, key="destino")

if c3.button("✅ Registrar Entrada", type="primary", key="btn_entrada"):
    if cpf_input:
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input.strip()).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'],
                "nome": p[0]['nome'],
                "empresa": p[0].get('empresa', ''),
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "data_saida": ""
            }).execute()
            st.success(f"✅ Entrada registrada para **{setor_escolhido}**!")
            st.rerun()
        else:
            st.error("❌ CPF não cadastrado. Cadastre primeiro na seção acima.")
    else:
        st.warning("⚠️ Digite o CPF.")

# ====================== PESSOAS PRESENTES ======================
st.subheader("📍 Pessoas Presentes no Hospital")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    tabs = st.tabs(["📊 Todos", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"])
    
    with tabs[0]:
        for p in dados:
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
                col1.write(f"**👤 {p['nome']}**")
                col2.write(f"📍 {p['setor_destino']}")
                col3.write(f"🏢 {p.get('empresa', 'N/A')}")
                if col4.button("🚪 Registrar Saída", key=f"saida_{p['id']}"):
                    supabase.table("movimentacao").update({
                        "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }).eq("id", p['id']).execute()
                    st.success(f"✅ Saída registrada para {p['nome']}")
                    st.rerun()
                st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

    for i, setor in enumerate(["C.C", "GRSA", "Brasanitas"], 1):
        with tabs[i]:
            pessoas_setor = [r for r in dados if r.get('setor_destino') == setor]
            if pessoas_setor:
                for p in pessoas_setor:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
                        col1.write(f"**👤 {p['nome']}**")
                        col2.write(f"🏢 {p.get('empresa', 'N/A')}")
                        col3.write(f"🕒 Entrada: {p['data_entrada']}")
                        if col4.button("🚪 Saída", key=f"saida2_{p['id']}"):
                            supabase.table("movimentacao").update({
                                "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                            }).eq("id", p['id']).execute()
                            st.rerun()
                        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
            else:
                st.info(f"📭 Nenhuma pessoa no setor {setor}")
else:
    st.info("🏢 Nenhuma pessoa presente no momento.")

# ====================== HISTÓRICO E GESTÃO ======================
with st.expander("🕒 Histórico Completo de Movimentações"):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        df = pd.DataFrame(todos_dados)
        st.dataframe(df, use_container_width=True, height=400)
        
        st.markdown("---")
        col_del1, col_del2, col_del3 = st.columns([1, 2, 1])
        with col_del2:
            id_excluir = st.number_input("ID para excluir:", min_value=1, step=1, key="id_excluir")
            if st.button("🗑️ Excluir Registro", key="del_reg", use_container_width=True):
                try:
                    supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
                    st.success(f"✅ Registro {id_excluir} excluído!")
                    st.rerun()
                except:
                    st.error("❌ Erro ao excluir. Verifique o ID.")
    else:
        st.info("📭 Nenhum registro encontrado.")

# ====================== GESTÃO DE CADASTROS (ADMIN) ======================
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        
        # Buscar todos os cadastros
        todos_colaboradores = supabase.table("Pessoas").select("id, nome, cpf, empresa").order("nome").execute().data
        
        if todos_colaboradores:
            
            # ========== BARRA DE PESQUISA COM LUPA ==========
            st.markdown("### 🔍 Pesquisar Cadastro")
            
            # Criar colunas para pesquisa e lupa visual
            col_search1, col_search2 = st.columns([5, 1])
            
            with col_search1:
                # Campo de pesquisa com placeholder e ícone visual
                search_term = st.text_input(
                    "🔎",  # Emoji de lupa como label visual
                    placeholder="Digite o nome, CPF ou empresa para pesquisar...",
                    key="search_exclusao",
                    label_visibility="collapsed"
                )
            
            with col_search2:
                # Botão de limpar pesquisa
                if st.button("🗑️ Limpar", key="clear_search", use_container_width=True):
                    st.session_state.search_term = ""
                    st.rerun()
            
            # Filtrar resultados baseado na pesquisa
            if search_term:
                search_lower = search_term.lower()
                resultados_filtrados = [
                    p for p in todos_colaboradores 
                    if search_lower in p['nome'].lower() 
                    or search_lower in p['cpf'].lower() 
                    or search_lower in p.get('empresa', '').lower()
                ]
                st.info(f"🔍 **{len(resultados_filtrados)}** resultado(s) encontrado(s) para: **{search_term}**")
            else:
                resultados_filtrados = todos_colaboradores
                st.info(f"📋 Total de cadastros: **{len(resultados_filtrados)}** pessoas")
            
            # Exibir tabela com resultados filtrados
            if resultados_filtrados:
                df_cadastros = pd.DataFrame(resultados_filtrados)
                st.dataframe(df_cadastros, use_container_width=True, height=300)
                
                st.markdown("---")
                st.subheader("🗑️ Excluir Cadastro")
                
                # Criar lista para seleção apenas com resultados filtrados
                lista_nomes = [f"{p['nome']} - CPF: {p['cpf']} {f'- Emp: {p["empresa"]}' if p.get('empresa') else ''}" for p in resultados_filtrados]
                
                # Selectbox para escolher qual excluir
                selecionado = st.selectbox(
                    "Selecione a pessoa para excluir:", 
                    lista_nomes,
                    key="select_excluir"
                )
                
                # Mostrar informações da pessoa selecionada
                pessoa_selecionada = resultados_filtrados[lista_nomes.index(selecionado)]
                st.warning(f"⚠️ **Pessoa selecionada:** {pessoa_selecionada['nome']} (CPF: {pessoa_selecionada['cpf']})")
                
                # Confirmação dupla para exclusão
                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    confirmar = st.checkbox("✅ Confirmar que deseja excluir este cadastro permanentemente")
                with col_confirm2:
                    with st.popover("🗑️ Clique para excluir", use_container_width=True):
                        st.error("⚠️ **ATENÇÃO!** Esta ação é irreversível!")
                        if st.button("⚠️ SIM, EXCLUIR PERMANENTEMENTE", key="del_cad", use_container_width=True):
                            try:
                                supabase.table("Pessoas").delete().eq("cpf", pessoa_selecionada['cpf']).execute()
                                st.success(f"✅ Cadastro de **{pessoa_selecionada['nome']}** excluído com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro ao excluir: {e}")
                
                if not confirmar:
                    st.info("🔒 Marque a confirmação para habilitar a exclusão")
            
            else:
                st.warning(f"⚠️ Nenhum resultado encontrado para: **{search_term}**")
                if st.button("🔄 Mostrar todos os cadastros", key="show_all"):
                    st.rerun()
        
        else:
            st.info("📭 Nenhum cadastro encontrado no sistema.")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #64748b; font-size: 12px;'>
        ACCESS GATE - Sistema de Controle de Acesso © 2024
    </div>
""", unsafe_allow_html=True)
