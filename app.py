import streamlit as st
import pandas as pd
from datetime import datetime

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portaria Hospitalar Web", layout="centered")

# SISTEMA DE LOGIN SEGURO (BLOQUEIA TUDO ANTES DO LOGIN)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""
    st.session_state["nome_usuario"] = ""

if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso Restrito - Portaria Hospitalar")
    usuario_input = st.text_input("Username")
    senha_input = st.text_input("Password", type="password")
    if st.button("Entrar no Sistema", use_container_width=True):
        if usuario_input == "admin" and senha_input == "admin123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "admin"
            st.session_state["nome_usuario"] = "Administrador"
            st.rerun()
        elif usuario_input == "porteiro1" and senha_input == "hospital123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "porteiro1"
            st.session_state["nome_usuario"] = "Porteiro Central"
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

username = st.session_state["username"]
nome_usuario = st.session_state["nome_usuario"]

# BARRA LATERAL
if st.sidebar.button("Sair do Sistema"):
    st.session_state["autenticado"] = False
    st.rerun()
st.sidebar.markdown(f"**Operador Atual:**\n{nome_usuario}")

# CONEXÃO COM O GOOGLE SHEETS (BANCO DE DADOS NA NUVEM)
# Substitua as letras abaixo pelo ID real da sua planilha do Google
ID_PLANILHA = "1-j0vduIJNpbKthmabUA7Ud8ZnMLazq4RBkhLodf190M"

URL_CADASTRO = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/gviz/tq?tqx=out:csv&sheet=cadastro"
URL_MOVIMENTACAO = f"https://docs.google.com/spreadsheets/d/{ID_PLANILHA}/gviz/tq?tqx=out:csv&sheet=movimentacao"

# FUNÇÃO PARA ENVIAR DADOS AO GOOGLE SHEETS VIA FORMULÁRIO WEB (SIMPLIFICADO PARA STREAMLIT CLOUD)
def atualizar_google_sheets(df, aba):
    # Nota técnica: Para salvar dados de volta de forma 100% gratuita na nuvem pública,
    # o Streamlit lerá os dados. Como o Sheets está público via link para o app ler,
    # as funções locais usavam .to_csv. Na nuvem, usaremos a exibição em tempo real.
    pass

# CARREGAR DADOS DA NUVEM
try:
    df_cadastro = pd.read_csv(URL_CADASTRO).fillna("")
    df_movimentacao = pd.read_csv(URL_MOVIMENTACAO).fillna("")
except:
    st.error("Erro ao conectar com o Banco de Dados Google Sheets. Verifique o ID ou o compartilhamento.")
    st.stop()

# --- SESSÃO 1: PORTARIA ---
st.title("🔏 Sistema de Controle de Acesso Web")
st.subheader("Registrar Nova Entrada")
cpf_digitado = st.text_input("Digite o CPF para buscar (somente números):", max_chars=11, key="cpf_entrada")

if cpf_digitado:
    usuario_encontrado = df_cadastro[df_cadastro['CPF'].astype(str) == str(cpf_digitado)]
    if not usuario_encontrado.empty:
        nome_pessoa = usuario_encontrado.iloc[0]['Nome']
        empresa_pessoa = usuario_encontrado.iloc[0]['Vinculo']
        st.success(f"👤 **Pessoa localizada!**")
        st.text(f"Nome: {nome_pessoa}")
        st.text(f"Empresa/Vínculo: {empresa_pessoa}")
        
        destinos = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Onco"]
        destino_selecionado = st.selectbox("Selecione o Setor de Destino:", destinos)
        
        if st.button("🔵 CONFIRMAR REGISTRO DE ENTRADA"):
            horario_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            st.info("Para salvar registros permanentemente na nuvem gratuita, integre as credenciais de API do Google ou utilize o painel conectado.")
            st.success("Entrada processada na tela!")
    else:
        st.error("❌ CPF não localizado. Solicite o cadastro ao Administrador.")

st.markdown("---")
st.subheader("📋 Painel de Monitoramento (Histórico Geral)")
st.dataframe(df_movimentacao, use_container_width=True)