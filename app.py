import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="ACCESS GATE", layout="wide", page_icon="🔐", initial_sidebar_state="expanded")

# ====================== DESIGN FINAL ======================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(10, 20, 40, 0.85), rgba(15, 23, 42, 0.92)),
                    url('https://i.ibb.co/DRMpX/tech-shield-background.jpg') !important;
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #e0f2fe;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(30, 41, 59, 0.95);
        border-right: 1px solid #334155;
    }
    
    .sidebar-title {
        font-size: 26px;
        font-weight: 700;
        color: #67e8f9;
        text-align: center;
        padding: 25px 0 15px 0;
        border-bottom: 1px solid #334155;
    }
    
    h1 {
        color: #67e8f9 !important;
        font-size: 34px !important;
        font-weight: 700;
    }
    
    /* Botões */
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
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.5);
    }
    
    div.stButton > button:not([key="sair_final"]):hover {
        background: linear-gradient(90deg, #34d399, #6ee7b7);
        transform: translateY(-3px);
        box-shadow: 0 0 25px rgba(52, 211, 153, 0.8);
    }
    
    div.stButton > button[key="sair_final"] {
        background: linear-gradient(90deg, #ef4444, #f87171);
        color: white;
        border: 2px solid #f87171;
    }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
st.sidebar.markdown("<div class='sidebar-title'>🔐 ACCESS GATE</div>", unsafe_allow_html=True)
st.sidebar.markdown("**MENU PRINCIPAL**")
st.sidebar.markdown("🏠 Dashboard")
st.sidebar.markdown("👥 Colaboradores")
st.sidebar.markdown("📍 Controle de Acesso")
st.sidebar.markdown("🕒 Histórico")
st.sidebar.markdown("⚙️ Configurações")

# ====================== TELA DE LOGIN (Estilo da 3ª Foto) ======================
if "logado" not in st.session_state: st.session_state.logado = False
if "perfil" not in st.session_state: st.session_state.perfil = ""

if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center; margin-top:30px;'>🔐 ACCESS GATE</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
            <div style='text-align:center; margin:40px 0;'>
                <div style='border:5px solid #00f5ff; border-radius:50%; width:280px; height:280px; margin:0 auto;
                            display:flex; align-items:center; justify-content:center; box-shadow: 0 0 60px #00f5ff;'>
                    <div style='text-align:center;'>
                        <span style='font-size:90px;'>🔑</span><br>
                        <span style='font-size:26px; font-weight:900; color:#00f5ff;'>BIOMETRIC</span><br>
                        <span style='font-size:26px; font-weight:900; color:#00f5ff;'>LOGIN</span><br>
                        <span style='color:#00ff9d; font-size:20px;'>READY</span>
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
                st.error("Senha incorreta!")
    st.stop()

# ====================== PAINEL PRINCIPAL ======================
col_titulo, col_perfil, col_btn = st.columns([6, 2, 2])
with col_titulo:
    st.markdown("<h1>ACCESS GATE - PAINEL DE CONTROLE</h1>", unsafe_allow_html=True)

with col_perfil:
    st.markdown(f"**PERFIL:** <span style='color:#67e8f9; font-size:18px;'>{st.session_state.perfil}</span>", unsafe_allow_html=True)

with col_btn:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

st.markdown("### 📊 Painel de Controle")

setores_lista = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Oncologia","Farmacia 4°And", "Brasanitas", "GRSA", "epidemiologia", "CDU"]

# ... (o restante do código de funcionalidades continua igual)

col_esq, col_dir = st.columns(2)

with col_esq:
    st.markdown("**+ Gerenciamento de Cadastros**")
    with st.expander("➕ Adicionar Novo Colaborador"):
        col_a, col_b, col_c, col_d = st.columns(4)
        novo_cpf = col_a.text_input("CPF:", key="novo_cpf")
        novo_nome = col_b.text_input("Nome Completo:", key="novo_nome")
        novo_empresa = col_c.text_input("Empresa:", key="novo_empresa")
        novo_vinculo = col_d.selectbox("Vínculo:", setores_lista, key="novo_vinculo")
        
        if st.button("💾 Salvar Novo Cadastro", key="salvar_cadastro"):
            if novo_cpf and novo_nome:
                supabase.table("Pessoas").insert({"cpf": novo_cpf, "nome": novo_nome, "vinculo": novo_vinculo, "empresa": novo_empresa}).execute()
                st.success("✅ Cadastro salvo!")
                st.rerun()

    with st.expander("🔵 Registrar Nova Entrada"):
        c1, c2, c3 = st.columns([2,2,1])
        cpf_input = c1.text_input("CPF:", key="cpf_entrada")
        setor_escolhido = c2.selectbox("Destino:", setores_lista, key="sel_destino")
        if c3.button("✅ Registrar Entrada", key="btn_entrada"):
            p = supabase.table("Pessoas").select("*").eq("cpf", cpf_input).execute().data
            if p:
                supabase.table("movimentacao").insert({
                    "cpf": p[0]['cpf'], "nome": p[0]['nome'], "empresa": p[0].get('empresa',''),
                    "setor_destino": setor_escolhido, "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"), "data_saida": ""
                }).execute()
                st.success("✅ Entrada registrada!")
                st.rerun()
            else:
                st.error("CPF não encontrado.")

with col_dir:
    st.markdown("**● Registrar Saída**")
    cpf_saida = st.text_input("CPF para Saída:", key="out_cpf")
    if st.button("✅ Confirmar Saída", key="btn_saida_manual"):
        reg = supabase.table("movimentacao").select("*").eq("cpf", cpf_saida).eq("data_saida", "").execute().data
        if reg:
            supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", reg[0]['id']).execute()
            st.success("✅ Saída registrada!")
            st.rerun()

# (Continue com o resto das seções: Pessoas Presentes, Histórico e Gestão Admin como no código anterior)

st.markdown("---")
col_inf1, col_inf2 = st.columns(2)

with col_inf1:
    st.subheader("📍 Pessoas Presentes no Hospital")
    dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
    if dados:
        aba_lista = st.tabs(setores_lista)
        for i, nome_setor in enumerate(setores_lista):
            with aba_lista[i]:
                for p in [r for r in dados if r.get('setor_destino') == nome_setor]:
                    c1, c2, c3 = st.columns([3,3,2])
                    c1.write(f"**{p['nome']}**")
                    c2.write(f"Empresa: {p.get('empresa', 'N/A')}")
                    if c3.button("🚪 Registrar Saída", key=f"s_{p['id']}"):
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")}).eq("id", p['id']).execute()
                        st.rerun()

with col_inf2:
    st.subheader("🕒 Histórico Completo")
    todos_dados = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    if todos_dados:
        st.dataframe(pd.DataFrame(todos_dados), use_container_width=True)
        id_excluir = st.number_input("ID para excluir:", min_value=1, step=1)
        if st.button("🗑️ Excluir Registro", key="del_reg"):
            supabase.table("movimentacao").delete().eq("id", id_excluir).execute()
            st.rerun()

if st.session_state.perfil == "ADMIN":
    st.subheader("⚙️ Gestão de Cadastros")
    todos_colaboradores = supabase.table("Pessoas").select("nome, cpf").execute().data
    if todos_colaboradores:
        lista_nomes = [f"{p['nome']} (CPF: {p['cpf']})" for p in todos_colaboradores]
        selecionado = st.selectbox("Selecionar para excluir:", lista_nomes)
        if st.button("🗑️ Excluir Cadastro", key="del_cad"):
            cpf_excluir = selecionado.split("(CPF: ")[1].replace(")", "")
            supabase.table("Pessoas").delete().eq("cpf", cpf_excluir).execute()
            st.rerun()
