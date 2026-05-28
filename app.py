import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

st.set_page_config(
    page_title="ACCESS GATE",
    layout="wide",
    page_icon="🔐",
    initial_sidebar_state="expanded"
)

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

    /* NOVO ESTILO DO PAINEL */
    .box-painel {
        border: 3px solid #67e8f9;
        border-radius: 14px;
        padding: 35px 15px;
        text-align: center;
        background: rgba(15, 23, 42, 0.75);
        box-shadow: 0 0 18px rgba(0,255,255,0.25);
        transition: 0.3s;
        min-height: 220px;
    }

    .box-painel:hover {
        transform: scale(1.03);
        box-shadow: 0 0 30px rgba(0,255,255,0.6);
    }

    .titulo-box {
        font-size: 28px;
        font-weight: 800;
        color: #67e8f9;
        margin-bottom: 35px;
    }

    .numero-box {
        font-size: 70px;
        font-weight: 900;
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
if "logado" not in st.session_state:
    st.session_state.logado = False

if "perfil" not in st.session_state:
    st.session_state.perfil = ""

# ====================== LOGIN ======================
if not st.session_state.logado:

    st.markdown(
        "<h1 style='text-align:center; margin:40px 0 30px 0;'>🔐 ACCESS GATE</h1>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown("""
            <div style='text-align:center; margin:30px 0;'>
                <div style='width: 320px; height: 320px; margin: 0 auto;
                            border: 8px solid #00f5ff;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            box-shadow: 0 0 90px #00f5ff,
                                        inset 0 0 60px rgba(0, 245, 255, 0.7);'>

                    <div style='text-align:center;'>
                        <div style='font-size: 110px; margin-bottom: 10px;'>🔑</div>

                        <span style='font-size: 32px;
                                     font-weight: 900;
                                     color:#00f5ff;'>
                                     BIOMETRIC
                        </span><br>

                        <span style='font-size: 32px;
                                     font-weight: 900;
                                     color:#00f5ff;'>
                                     LOGIN
                        </span><br>

                        <span style='color:#00ff9d;
                                     font-size: 24px;
                                     font-weight: bold;'>
                                     READY
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<h3 style='text-align:center; color:#00f5ff;'>OU USE CREDENCIAIS</h3>",
            unsafe_allow_html=True
        )

        senha = st.text_input(
            "Digite a senha de acesso:",
            type="password",
            key="senha_login"
        )

        if st.button(
            "🔓 ENTRAR NO SISTEMA",
            key="login_btn",
            use_container_width=True
        ):

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
    st.markdown(
        f"**PERFIL:** <span style='color:#67e8f9;'>{st.session_state.perfil}</span>",
        unsafe_allow_html=True
    )

with col3:
    if st.button("🚪 DESCONECTAR", key="sair_final"):
        st.session_state.logado = False
        st.rerun()

# ====================== CADASTRO ======================
st.subheader("➕ Cadastro de Nova Pessoa")

with st.expander("📋 Adicionar Novo Colaborador / Prestador", expanded=True):

    col_a, col_b, col_c = st.columns(3)

    novo_cpf = col_a.text_input(
        "CPF *",
        key="novo_cpf",
        placeholder="000.000.000-00"
    )

    novo_nome = col_b.text_input(
        "Nome Completo *",
        key="novo_nome"
    )

    novo_empresa = col_c.text_input(
        "Empresa",
        key="novo_empresa"
    )

    if st.button(
        "💾 Salvar Cadastro",
        key="salvar_cadastro",
        type="primary"
    ):

        if novo_cpf and novo_nome:

            supabase.table("Pessoas").insert({
                "cpf": novo_cpf.strip(),
                "nome": novo_nome.strip(),
                "empresa": novo_empresa.strip() if novo_empresa else ""
            }).execute()

            st.success("✅ Cadastro salvo com sucesso!")
            st.rerun()

        else:
            st.error("❌ CPF e Nome Completo são obrigatórios.")

# ====================== REGISTRO DE ENTRADA ======================
st.subheader("📋 Registrar Nova Entrada")

tipo = st.radio(
    "Tipo de Pessoa:",
    ["Colaborador Interno", "Prestador de Serviço"],
    horizontal=True
)

if tipo == "Colaborador Interno":

    destinos = [
        "C.C",
        "Hemodinâmica",
        "OPME",
        "CME",
        "Endoscopia",
        "Manutenção",
        "Laboratório",
        "Farmacia"
    ]

else:

    destinos = [
        "C.C",
        "GRSA",
        "Brasanitas"
    ]

c1, c2, c3 = st.columns([2, 2, 1])

cpf_input = c1.text_input("CPF:", key="cpf_entrada")

setor_escolhido = c2.selectbox(
    "Destino:",
    destinos,
    key="destino"
)

if c3.button(
    "✅ Registrar Entrada",
    type="primary",
    key="btn_entrada"
):

    if cpf_input:

        p = supabase.table("Pessoas") \
            .select("*") \
            .eq("cpf", cpf_input) \
            .execute().data

        if p:

            supabase.table("movimentacao").insert({
                "cpf": p[0]['cpf'],
                "nome": p[0]['nome'],
                "empresa": p[0].get('empresa', ''),
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "data_saida": ""
            }).execute()

            st.success(
                f"✅ Entrada registrada para **{setor_escolhido}**!"
            )

            st.rerun()

        else:
            st.error("❌ CPF não cadastrado.")

    else:
        st.warning("Digite o CPF.")

# ====================== PESSOAS PRESENTES ======================
st.subheader("📍 Pessoas Presentes no Hospital")

dados = supabase.table("movimentacao") \
    .select("*") \
    .eq("data_saida", "") \
    .execute().data

if dados:

    tabs = st.tabs(["Todos", "C.C", "GRSA", "Brasanitas"])

    with tabs[0]:

        for p in dados:

            c1, c2, c3 = st.columns([3, 3, 2])

            c1.write(f"**{p['nome']}** → {p['setor_destino']}")
            c2.write(f"Empresa: {p.get('empresa', 'N/A')}")

            if c3.button("🚪 Saída", key=f"saida_{p['id']}"):

                supabase.table("movimentacao").update({
                    "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")
                }).eq("id", p['id']).execute()

                st.rerun()

    for i, setor in enumerate(["C.C", "GRSA", "Brasanitas"], 1):

        with tabs[i]:

            for p in [r for r in dados if r.get('setor_destino') == setor]:

                c1, c2, c3 = st.columns([3, 3, 2])

                c1.write(f"**{p['nome']}**")
                c2.write(f"Empresa: {p.get('empresa', 'N/A')}")

                if c3.button("🚪 Saída", key=f"saida2_{p['id']}"):

                    supabase.table("movimentacao").update({
                        "data_saida": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }).eq("id", p['id']).execute()

                    st.rerun()

# =========================================================
# ====================== NOVO HISTÓRICO ===================
# =========================================================

st.subheader("📊 Painel de Prestadores e Setores")

historico_visual = supabase.table("movimentacao") \
    .select("*") \
    .eq("data_saida", "") \
    .execute().data

prestadores_total = len(historico_visual)

grsa_total = len([
    x for x in historico_visual
    if x.get("setor_destino") == "GRSA"
])

brasanitas_total = len([
    x for x in historico_visual
    if x.get("setor_destino") == "Brasanitas"
])

cc_total = len([
    x for x in historico_visual
    if x.get("setor_destino") == "C.C"
])

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="box-painel">
            <div class="titulo-box">
                PRESTADOR<br>DE SERVIÇO
            </div>

            <div class="numero-box">
                {prestadores_total}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="box-painel">
            <div class="titulo-box">
                GRSA
            </div>

            <div class="numero-box">
                {grsa_total}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="box-painel">
            <div class="titulo-box">
                BRASANITAS
            </div>

            <div class="numero-box">
                {brasanitas_total}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="box-painel">
            <div class="titulo-box">
                C.C
            </div>

            <div class="numero-box">
                {cc_total}
            </div>
        </div>
    """, unsafe_allow_html=True)

# ====================== HISTÓRICO DETALHADO ======================

with st.expander("🕒 Histórico Completo"):

    todos_dados = supabase.table("movimentacao") \
        .select("*") \
        .order("id", desc=True) \
        .execute().data

    if todos_dados:

        df = pd.DataFrame(todos_dados)

        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )

        st.markdown("---")

        id_excluir = st.number_input(
            "ID para excluir:",
            min_value=1,
            step=1
        )

        if st.button("🗑️ Excluir Registro", key="del_reg"):

            supabase.table("movimentacao") \
                .delete() \
                .eq("id", id_excluir) \
                .execute()

            st.success("✅ Registro excluído com sucesso!")
            st.rerun()

# ====================== GESTÃO DE CADASTROS ======================
if st.session_state.perfil == "ADMIN":

    with st.expander("⚙️ Gestão de Cadastros", expanded=False):

        st.markdown("""
        <style>
        .titulo-gestao {
            font-size: 24px;
            font-weight: 700;
            color: #67e8f9;
            margin-bottom: 15px;
        }

        .caixa-info {
            background: rgba(15, 23, 42, 0.75);
            padding: 20px;
            border-radius: 12px;
            border: 2px solid #67e8f9;
            margin-top: 10px;
            box-shadow: 0 0 15px rgba(0,255,255,0.2);
        }

        .texto-info {
            font-size: 17px;
            color: white;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(
            "<div class='titulo-gestao'>🔎 Pesquisa Inteligente de Cadastros</div>",
            unsafe_allow_html=True
        )

        # ====================== CAMPO DE PESQUISA ======================
        pesquisa_nome = st.text_input(
            "Pesquisar por Nome ou CPF:",
            placeholder="Digite o nome do colaborador...",
            key="pesquisa_cadastro"
        )

        # ====================== CONSULTA ======================
        todos_colaboradores = supabase.table("Pessoas") \
            .select("*") \
            .order("nome") \
            .execute().data

        # ====================== FILTRO ======================
        if pesquisa_nome:

            filtrados = [
                p for p in todos_colaboradores
                if pesquisa_nome.lower() in p["nome"].lower()
                or pesquisa_nome in p["cpf"]
            ]

        else:
            filtrados = todos_colaboradores

        # ====================== RESULTADOS ======================
        if filtrados:

            lista_nomes = [
                f"{p['nome']} (CPF: {p['cpf']})"
                for p in filtrados
            ]

            selecionado = st.selectbox(
                "Selecione o cadastro:",
                lista_nomes,
                key="select_cadastro"
            )

            # ====================== CPF SELECIONADO ======================
            cpf_selecionado = selecionado.split("(CPF: ")[1].replace(")", "")

            # ====================== BUSCAR DADOS ======================
            pessoa = next(
                (
                    p for p in filtrados
                    if p["cpf"] == cpf_selecionado
                ),
                None
            )

            if pessoa:

                st.markdown("""
                <div class='caixa-info'>
                """, unsafe_allow_html=True)

                st.markdown(
                    f"<div class='texto-info'><b>👤 Nome Atual:</b> {pessoa['nome']}</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div class='texto-info'><b>🆔 CPF:</b> {pessoa['cpf']}</div>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div class='texto-info'><b>🏢 Empresa:</b> {pessoa.get('empresa', 'N/A')}</div>",
                    unsafe_allow_html=True
                )

                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")

                st.markdown("## ✏️ Editar Cadastro")

                # ====================== CAMPOS DE EDIÇÃO ======================
                novo_nome_edit = st.text_input(
                    "Nome Completo",
                    value=pessoa["nome"],
                    key="edit_nome"
                )

                novo_cpf_edit = st.text_input(
                    "CPF",
                    value=pessoa["cpf"],
                    key="edit_cpf"
                )

                nova_empresa_edit = st.text_input(
                    "Empresa",
                    value=pessoa.get("empresa", ""),
                    key="edit_empresa"
                )

                st.markdown("")

                col_edit1, col_edit2 = st.columns(2)

                # ====================== SALVAR ALTERAÇÕES ======================
                with col_edit1:

                    if st.button(
                        "💾 Salvar Alterações",
                        key="salvar_edit",
                        use_container_width=True
                    ):

                        try:

                            supabase.table("Pessoas").update({
                                "nome": novo_nome_edit.strip(),
                                "cpf": novo_cpf_edit.strip(),
                                "empresa": nova_empresa_edit.strip()
                            }).eq("cpf", cpf_selecionado).execute()

                            st.success("✅ Cadastro atualizado com sucesso!")

                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erro ao atualizar: {e}")

                # ====================== EXCLUIR CADASTRO ======================
                with col_edit2:

                    if st.button(
                        "🗑️ Excluir Cadastro",
                        key="del_cad",
                        use_container_width=True
                    ):

                        try:

                            supabase.table("Pessoas") \
                                .delete() \
                                .eq("cpf", cpf_selecionado) \
                                .execute()

                            st.success("✅ Cadastro excluído com sucesso!")

                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Erro ao excluir: {e}")

        else:

            st.warning("⚠️ Nenhum cadastro encontrado.")
