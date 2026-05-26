import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DO BANCO DE DADOS (SQLite) ---
conn = sqlite3.connect('portaria.db', check_same_thread=False)
c = conn.cursor()
# Criação das tabelas se não existirem
c.execute('''CREATE TABLE IF NOT EXISTS cadastro (cpf TEXT PRIMARY KEY, nome TEXT, vinculo TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS movimentacao (id INTEGER PRIMARY KEY AUTOINCREMENT, cpf TEXT, nome TEXT, empresa TEXT, destino TEXT, entrada TEXT, saida TEXT)''')
conn.commit()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Portaria Hospitalar", layout="centered")

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["username"] = ""

if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso ao Sistema")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "admin"
            st.rerun()
        elif u == "porteiro1" and p == "hospital123":
            st.session_state["autenticado"] = True
            st.session_state["username"] = "porteiro1"
            st.rerun()
    st.stop()

# --- INTERFACE ---
st.title("🔏 Controle de Acesso")
if st.sidebar.button("Sair"):
    st.session_state["autenticado"] = False
    st.rerun()

# A. REGISTRO DE ENTRADA
st.subheader("📥 Nova Entrada")
cpf_busca = st.text_input("CPF (somente números):", max_chars=11)
if cpf_busca:
    usuario = c.execute("SELECT * FROM cadastro WHERE cpf=?", (cpf_busca,)).fetchone()
    if usuario:
        st.write(f"**Nome:** {usuario[1]} | **Vínculo:** {usuario[2]}")
        destino = st.selectbox("Destino:", ["C.C", "UTI", "Pronto Socorro", "CME"])
        if st.button("Confirmar Entrada"):
            c.execute("INSERT INTO movimentacao (cpf, nome, empresa, destino, entrada) VALUES (?,?,?,?,?)", 
                      (usuario[0], usuario[1], usuario[2], destino, datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            conn.commit()
            st.rerun()
    else:
        st.error("CPF não encontrado.")

# B. REGISTRO DE SAÍDA
st.subheader("📤 Registrar Saída")
abertos = pd.read_sql("SELECT * FROM movimentacao WHERE saida IS NULL", conn)
if not abertos.empty:
    selecionado = st.selectbox("Quem está saindo?", abertos['nome'].tolist())
    if st.button("Confirmar Saída"):
        c.execute("UPDATE movimentacao SET saida=? WHERE nome=? AND saida IS NULL", (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), selecionado))
        conn.commit()
        st.rerun()

# C. CADASTRO (ADMIN)
if st.session_state["username"] == "admin":
    with st.expander("📝 Gerenciar Cadastros"):
        n_cpf = st.text_input("CPF:")
        n_nome = st.text_input("Nome:")
        n_vinc = st.text_input("Vínculo:")
        if st.button("Salvar Pessoa"):
            c.execute("INSERT INTO cadastro VALUES (?,?,?)", (n_cpf, n_nome, n_vinc))
            conn.commit()
            st.success("Salvo!")

st.subheader("📋 Painel de Movimentação")
st.dataframe(pd.read_sql("SELECT * FROM movimentacao ORDER BY id DESC", conn))
