import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# --- CONFIGURAÇÃO ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Access Gate", layout="wide", page_icon="🔐")

# ====================== DESIGN FUTURISTA ======================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0A1F2E 0%, #05131F 100%);
        color: #ffffff;
    }
    
    h1 {
        color: #00f5ff !important;
        text-align: center;
        font-size: 42px !important;
        text-shadow: 0 0 20px #00f5ff;
        letter-spacing: 3px;
    }
    
    .st-expander {
        background-color: rgba(10, 31, 46, 0.85) !important;
        border: 2px solid #00f5ff !important;
        border-radius: 15px !important;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
    }
    
    div.stButton > button {
        background-color: #003344;
        color: #00f5ff;
        border: 2px solid #00f5ff;
        border-radius: 12px;
        font-weight: bold;
        padding: 12px 24px;
        transition: all 0.3s;
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.4);
    }
    
    div.stButton > button:hover {
        background-color: #00f5ff;
        color: #000;
        box-shadow: 0 0 25px #00f
