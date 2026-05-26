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

# CONEXÃO COM O GOOGLE SHEETS
# Substitua as letras abaixo pelo ID real da sua planilha do Google
ID_PLANILHA = "1-j0vduIJNpbKthmabUA7Ud8ZnMLazq4RBkhLodf190M"

URL_CADASTRO = f"https://docs.google.com/spreadsheets/d/{1-j0vduIJNpbKthmabUA7Ud8ZnMLazq4RBkhLodf190M}/gviz/tq?tqx=out:csv&sheet=cadastro"
URL_MOVIMENTACAO = f"https://docs.google.com/spreadsheets/d/{1-j0vduIJNpbKthmabUA7Ud8ZnMLazq4RBkhLodf190M}/gviz/tq?tqx=out:csv&sheet=movimentacao"

# CARREGAR DADOS DA NUVEM GOOGLE SHEETS
try:
    df_cadastro = pd.read_csv(URL_CADASTRO).fillna("")
    if "CPF" in df_cadastro.columns:
        df_cadastro["CPF"] = df_cadastro["CPF"].astype(str).str.replace(".0", "", regex=False).str.strip()
except Exception as e:
    st.error("Erro ao conectar com a aba 'cadastro' do Google Sheets. Verifique o ID ou as permissões de partilha.")
    st.stop()

try:
    df_movimentacao = pd.read_csv(URL_MOVIMENTACAO).fillna("")
    if "CPF" in df_movimentacao.columns:
        df_movimentacao["CPF"] = df_movimentacao["CPF"].astype(str).str.replace(".0", "", regex=False).str.strip()
except Exception as e:
    st.error("Erro ao conectar com a aba 'movimentacao' do Google Sheets. Verifique o ID ou as permissões de partilha.")
    st.stop()

# --- SESSÃO 1: PORTARIA ---
st.title("🔏 Sistema de Controle de Acesso Web")
st.subheader("Registrar Nova Entrada")
cpf_digitado = st.text_input("Digite o CPF para buscar (somente números):", max_chars=11, key="cpf_entrada")

if cpf_digitado:
    cpf_limpo = str(cpf_digitado).strip()
    usuario_encontrado = df_cadastro[df_cadastro['CPF'] == cpf_limpo]
    
    if not usuario_encontrado.empty:
        nome_pessoa = usuario_encontrado.iloc[0]['Nome']
        empresa_pessoa = usuario_encontrado.iloc[0]['Vinculo']
        st.success(f"👤 **Pessoa localizada!**")
        st.text(f"Nome: {nome_pessoa}")
        st.text(f"Empresa/Vínculo: {empresa_pessoa}")
        
        destinos = ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Onco"]
        destino_selecionado = st.selectbox("Selecione o Setor de Destino:", destinos)
        
        if st.button("🔵 CONFIRMAR REGISTRO DE ENTRADA"):
            df_movimentacao['Saida'] = df_movimentacao['Saida'].astype(str)
            st.info("Para gravar dados de volta diretamente no Google Sheets na nuvem pública, configure o st.connection('gsheets') nas propriedades do Streamlit Cloud.")
            st.success(f"Entrada processada na tela para {nome_pessoa} com destino a {destino_selecionado}!")
    else:
        st.error("❌ CPF não localizado no banco de dados.")
