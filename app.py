import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐", initial_sidebar_state="expanded")

# ====================== ESTILO ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(10, 20, 40, 0.88), rgba(15, 23, 42, 0.95));
        color: #e0f2fe;
        font-family: 'Inter', sans-serif;
    }
    
    .sidebar-title {
        font-size: 26px;
        font-weight: 700;
        color: #67e8f9;
        text-align: center;
        padding: 25px 0 15px 0;
    }
    
    h1 {
        color: #67e8f9 !important;
        font-size: 34px !important;
        font-weight: 700;
    }
    
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:not([key="sair_final"]) {
        background: linear-gradient(90deg, #10b981, #34d399);
        color: #0f172a;
        border: 2px solid #34d399;
    }
    
    div.stButton > button:not([key="sair_final"]):hover {
        background: linear-gradient(90deg, #34d399, #6ee7b7);
        transform: translateY(-3px);
    }
    
    div.stButton > button[key="sair_final"] {
        background: linear-gradient(90deg, #ef4444, #f87171);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
st.sidebar.markdown("<div class='sidebar-title'>🔐 ACCESS GATE</div>", unsafe_allow_html=True)
st.sidebar.markdown("**MENU PRINCIPAL**")
st.sidebar.markdown("🏠 Dashboard")
st.sidebar.markdown("👥 Colaboradores")
st.sidebar.markdown("🔧 Prestadores de Serviço")
st.sidebar.markdown("🕒 Histórico")
st.sidebar.markdown("⚙️ Configurações")

# ====================== SESSÃO ======================
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

# ====================== LOGIN ======================
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center; margin:40px 0 30px 0;'>🔐 ACCESS GATE</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align:center; margin:30px 0;'>
                <div style='width: 320px; height: 320px; margin: 0 auto; border: 8px solid #00f5ff; 
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;
                            box-shadow: 0 0 90px #00f5ff, inset 0 0 60px rgba(0, 245, 255, 0.7);'>
                    <div style='text-align:center;'>
                        <div style='font-size: 110px; margin-bottom: 10px;'>🔑</div>
                        <span style='font-size: 32px; font-weight: 900; color:#00f5ff;'>BIOMETRIC</span><br>
                        <span style='font-size: 32px; font-weight: 900; color:#00f5ff;'>LOGIN</span><br>
                        <span style='color:#00ff9d; font-size: 24px; font-weight: bold;'>READY</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align:center; color:#00f5ff;'>OU USE CREDENCIAIS</h3>", unsafe_allow_html=True)
        
        senha = st.text_input("Digite a senha de acesso:", type="password", key="senha_login")
        
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
                st.error("❌ Senha incorreta!")
    st.stop()

# ====================== HEADER ======================
col1, col2, col3 = st.columns([5, 2, 2])
with col1:
    st.title("ACCESS GATE - PAINEL DE CONTROLE")
with col2:
    st.markdown(f"**PERFIL:** <span style='color:#67e8f9;'>{st.session_state.perfil}</span>", unsafe_allow_html=True)
with col3:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

# ====================== CADASTRO DE NOVA PESSOA (Limpo) ======================
st.subheader("➕ Cadastro de Nova Pessoa")

with st.expander("📋 Adicionar Novo Colaborador / Prestador", expanded=True):
    col_a, col_b, col_c, col_d = st.columns(4)
    novo_cpf = col_a.text_input("CPF *", key="novo_cpf", placeholder="000.000.000-00")
    novo_nome = col_b.text_input("Nome Completo *", key="novo_nome")
    novo_empresa = col_c.text_input("Empresa", key="novo_empresa")
    novo_vinculo = col_d.selectbox("Vínculo / Setor *", 
        ["C.C", "GRSA", "Brasanitas", "Hemodinâmica", "OPME", "CME", "Endoscopia", 
         "Manutenção", "Laboratório", "Farmacia 6°And", "Farmacia 4°And", "SSGA", "Outros"], 
        key="novo_vinculo")
    
    if st.button("💾 Salvar Cadastro", key="salvar_cadastro", type="primary"):
        if novo_cpf and novo_nome and novo_vinculo:
            supabase.table("Pessoas").insert({
                "cpf": novo_cpf.strip(),
                "nome": novo_nome.strip(),
                "empresa": novo_empresa.strip() if novo_empresa else "",
                "vinculo": novo_vinculo
            }).execute()
            st.success("✅ Cadastro salvo com sucesso!")
            st.rerun()
        else:
            st.error("❌ Os campos CPF, Nome e Vínculo são obrigatórios.")

# ====================== REGISTRO DE ENTRADA ======================
st.subheader("📋 Registrar Nova Entrada")

tipo = st.radio("Tipo de Pessoa:", ["Colaborador Interno", "Prestador de Serviço"], horizontal=True)

if tipo == "Colaborador Interno":
    destinos = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Laboratório", "Farmacia"]
else:
    destinos = ["C.C", "GRSA", "Brasanitas"]

c1, c2, c3 = st.columns([2, 2, 1])
cpf_input = c1.text_input("CPF:", key="cpf_entrada")
setor_escolhido = c2.selectbox("Destino:", destinos, key="destino")

if c3.button("✅ Registrar Entrada", type="primary", key="btn_entrada"):
    if cpf_input:
        p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
        if p:
            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'],
                "nome": p[0]['nome'],
                "empresa": p[0].get('empresa', ''),
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "data_saida": ""
            }).execute()
            st.success(f"✅ Entrada registrada para **{setor_escolhido}**!")
            st.rerun()
        else:
            st.error("❌ CPF não cadastrado.")
    else:
        st.warning("Digite o CPF.")

# ====================== PESSOAS PRESENTES ======================
st.subheader("📍 Pessoas Presentes no Hospital")
dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data

if dados:
    tabs = st.tabs(["Todos", "C.C", "GRSA", "Brasanitas"])
    with tabs[0]:
        for p in dados:
            c1, c2, c3 = st.columns([3, 3, 2])
            c1.write(f"**{p['nome']}** → {p['setor_destino']}")
            c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
            if c3.button("🚪 Saída", key=f"saida_{p['id']}"):
                supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                st.rerun()

    for i, setor in enumerate(["C.C", "GRSA", "Brasanitas"], 1):
        with tabs[i]:
            for p in [r for r in dados if r.get('setor_destino') == setor]:
                c1, c2, c3 = st.columns([3, 3, 2])
                c1.write(f"**{p['nome']}**")
                c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
                if c3.button("🚪 Saída", key=f"saida2_{p['id']}"):
                    supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                    st.rerun()

# ====================== HISTÓRICO E GESTÃO ======================
with st.expander("🕒 Histórico Completo"):
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        st.dataframe(pd.DataFrame(todos_dados), use_container_width=True)
        id_excluir = st.number_input("ID para excluir:", min_value=1, step=1)
        if st.button("🗑️ Excluir Registro", key="del_reg"):
            supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
            st.rerun()

if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros"):
        todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
        if todos_colaboradores:
            lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
            selecionado = st.selectbox("Selecionar para excluir:", lista_nomes)
            if st.button("🗑️ Excluir Cadastro", key="del_cad"):
                cpf_excluir = selecionado.split("(CPF: ")[1].replace(")", "")
                supabase.table("Pessoas").delete().eq("cpf", cpf_excluir).execute()
                st.rerun()
