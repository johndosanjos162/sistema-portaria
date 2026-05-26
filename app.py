import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# 1. CONFIGURAÇÃO
url = st.secrets["https://xcynavoumdgwaeiwnqfi.supabase.co"]
key = st.secrets["postgresql://postgres:[YOUR-PASSWORD]@db.xcynavoumdgwaeiwnqfi.supabase.co:5432/postgres"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Sistema de Portaria", layout="wide")
st.title("🏢 Sistema de Portaria")

# 2. ABAS DO SISTEMA
tab1, tab2 = st.tabs(["Cadastro/Movimentação", "Histórico de Acessos"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("cadastro_mov", clear_on_submit=True):
            st.subheader("Registrar Acesso")
            n_cpf = st.text_input("CPF:")
            n_nome = st.text_input("Nome Completo:")
            n_setor = st.selectbox("Setor de Destino:", ["C.C", "Hemodinâmica", "OPME", "CME", "Endoscopia", "Manutenção", "Eng.Clínicaa", "Laboratório", "SSGA", "Farmacia 6°And", "Dispensário", "RT","Onco"])
            n_tipo = st.radio("Tipo de Movimentação:", ["Entrada", "Saída"])
            
            if st.form_submit_button("Confirmar Registro"):
                try:
                    data = {
                        "cpf": n_cpf,
                        "nome": n_nome,
                        "setor_destino": n_setor,
                        "tipo": n_tipo,
                        "horario": datetime.now().isoformat()
                    }
                    supabase.table("Movimentacoes").insert(data).execute()
                    st.success(f"{n_tipo} registrada com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

with tab2:
    st.subheader("📋 Histórico Recente")
    if st.button("Atualizar Histórico"):
        try:
            # Busca os registros ordenados pelo mais recente
            response = supabase.table("Movimentacoes").select("*").order("horario", desc=True).execute()
            registros = response.data
            
            if registros:
                st.table(registros)
            else:
                st.info("Nenhum registro encontrado.")
        except Exception as e:
            st.error(f"Erro ao buscar histórico: {e}")

# 3. LIMPEZA E ORGANIZAÇÃO
st.sidebar.info("Use o menu acima para navegar entre o registro e o histórico.")
