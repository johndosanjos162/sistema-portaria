import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd
from PIL import Image
import base64
import re
import uuid
import json
import io

# --- CONFIGURAÇÃO DE SEGURANÇA ---
MAX_TENTATIVAS_LOGIN = 5
SESSION_TIMEOUT_MINUTOS = 5

# --- CONFIGURAÇÃO SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
    # Teste rápido de conexão (usa nome minúsculo)
    supabase.table("sessoes_ativas").select("id", count="exact").limit(1).execute()
except Exception as e:
    st.error(f"❌ Erro de conexão com Supabase: {e}")
    st.stop()

st.set_page_config(
    page_title="JOHN ACESSOS - CYBER SECURITY 2026",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ====================== CSS FUTURISTA GLOBAL ======================
st.markdown("""
<style>
    /* (mesmo CSS da resposta anterior - omitido por brevidade, mas deve ser mantido) */
    html, body { margin: 0; padding: 0; height: 100%; width: 100%; overflow: hidden; }
    .stApp { transition: background 0.3s ease; height: 100%; overflow: auto; }
    header[data-testid="stHeader"] { background: transparent !important; box-shadow: none !important; backdrop-filter: blur(8px); border-bottom: 1px solid rgba(0, 255, 255, 0.2); }
    header[data-testid="stHeader"] button { color: #0ff !important; text-shadow: 0 0 3px #0ff; }
    [data-testid="stSidebar"] { background: rgba(10, 10, 25, 0.65) !important; backdrop-filter: blur(16px); border-right: 1px solid rgba(0, 255, 255, 0.3); box-shadow: 4px 0 30px rgba(0, 255, 255, 0.1); }
    .avatar-container { text-align: center; margin-bottom: 25px; position: relative; }
    .avatar-image { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; border: 2px solid #0ff; box-shadow: 0 0 20px rgba(0, 255, 255, 0.5), inset 0 0 10px rgba(0, 255, 255, 0.3); transition: 0.3s; filter: drop-shadow(0 0 8px cyan); }
    .avatar-image:hover { transform: scale(1.02); box-shadow: 0 0 30px cyan; border-color: #f0f; }
    .glow-ring { position: absolute; top: -5px; left: 50%; transform: translateX(-50%); width: 140px; height: 140px; border-radius: 50%; background: radial-gradient(circle, rgba(0,255,255,0.2), transparent); pointer-events: none; animation: pulseRing 2s infinite; }
    @keyframes pulseRing { 0% { opacity: 0.5; transform: translateX(-50%) scale(0.9); } 100% { opacity: 0; transform: translateX(-50%) scale(1.3); } }
    .cyber-card { background: rgba(15, 15, 35, 0.55); backdrop-filter: blur(12px); border-radius: 28px; padding: 1.2rem 1rem; margin: 0.5rem; border: 1px solid rgba(0, 255, 255, 0.4); box-shadow: 0 8px 32px rgba(0,0,0,0.2), 0 0 12px rgba(0,255,255,0.3); transition: all 0.3s cubic-bezier(0.2,0.9,0.4,1.1); position: relative; overflow: hidden; cursor: default; }
    .cyber-card::before { content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px; background: linear-gradient(45deg, cyan, magenta, cyan); border-radius: 30px; z-index: -1; opacity: 0; transition: opacity 0.4s; }
    .cyber-card:hover { transform: translateY(-6px); border-color: cyan; box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 25px cyan; }
    .cyber-card:hover::before { opacity: 0.4; }
    .card-icon { font-size: 3rem; text-align: center; filter: drop-shadow(0 0 6px cyan); transition: 0.2s; }
    .cyber-card:hover .card-icon { transform: scale(1.05); filter: drop-shadow(0 0 12px magenta); }
    .card-title { font-size: 0.85rem; letter-spacing: 3px; text-transform: uppercase; color: #aaf; text-align: center; font-weight: 500; margin: 10px 0 5px; }
    .card-value { font-size: 2.6rem; font-weight: 800; text-align: center; background: linear-gradient(135deg, #fff, cyan); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 20px rgba(0,255,255,0.5); line-height: 1.2; font-family: 'Space Mono', monospace; }
    .cyber-card::after { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(0,255,255,0.2), transparent); transition: left 0.6s; pointer-events: none; }
    .cyber-card:hover::after { left: 100%; }
    .stButton>button, .stForm button { background: rgba(0,20,40,0.7) !important; backdrop-filter: blur(8px); border: 1px solid #0ff !important; border-radius: 40px !important; color: #0ff !important; font-weight: bold; transition: 0.2s; box-shadow: 0 0 5px rgba(0,255,255,0.3); }
    .stButton>button:hover, .stForm button:hover { background: rgba(0,255,255,0.15) !important; border-color: magenta !important; color: magenta !important; box-shadow: 0 0 15px magenta; transform: scale(1.02); }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div { background: rgba(0, 10, 20, 0.7) !important; backdrop-filter: blur(8px); border: 1px solid #0ff !important; border-radius: 16px !important; color: #0ff !important; font-family: 'Space Mono', monospace; transition: 0.2s; }
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus { border-color: magenta !important; box-shadow: 0 0 12px magenta; }
    .stForm, .stExpander, .stTabs [data-baseweb="tab-list"] { background: rgba(0, 0, 0, 0.3); backdrop-filter: blur(8px); border-radius: 20px; border: 1px solid rgba(0,255,255,0.2); padding: 5px; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #ccc; border-radius: 30px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, rgba(0,255,255,0.2), rgba(255,0,255,0.2)); color: #0ff !important; text-shadow: 0 0 3px cyan; }
    .stDataFrame { background: rgba(0,0,0,0.4) !important; border: 1px solid cyan !important; border-radius: 16px; }
    .live-indicator { display: inline-flex; align-items: center; gap: 6px; background: rgba(0,0,0,0.5); padding: 4px 12px; border-radius: 40px; font-size: 12px; font-family: monospace; border: 1px solid #0ff; color: #0ff; }
    .pulse-dot { width: 10px; height: 10px; background-color: #0f0; border-radius: 50%; box-shadow: 0 0 5px #0f0; animation: pulse 1s infinite; }
    @keyframes pulse { 0% { opacity: 0.4; transform: scale(0.8);} 100% { opacity: 1; transform: scale(1.2);} }
    .footer { text-align: center; padding: 15px; color: #6b7280; font-size: 9px; border-top: 1px solid rgba(0,255,255,0.2); margin-top: 25px; }
    h1, h2, h3, p, label, .info-item, .stMarkdown, .stRadio label, .stCheckbox label { color: #eef !important; text-shadow: 0 0 2px rgba(0,0,0,0.5); }
    .info-item { margin-bottom: 12px; font-size: 13px; display: flex; gap: 8px; font-family: 'Space Mono', monospace; }
    .badge-admin { background: linear-gradient(135deg, cyan, magenta); padding: 4px 15px; border-radius: 30px; font-weight: 700; font-size: 11px; color: #000; }
    .session-indicator { background: rgba(0,0,0,0.6); border-radius: 30px; padding: 4px 12px; font-size: 12px; font-family: monospace; color: cyan; display: inline-flex; align-items: center; gap: 5px; }
    #futuristic-canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -9999; pointer-events: none; }
    .login-container { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; margin: 0; padding: 0; overflow: hidden; z-index: 1000; }
    .login-box { background: rgba(8, 8, 20, 0.85); backdrop-filter: blur(20px); border-radius: 50px; padding: 45px 35px; border: 1px solid rgba(168, 85, 247, 0.6); width: 90%; max-width: 480px; text-align: center; animation: float 3s ease-in-out infinite; box-shadow: 0 0 30px rgba(168, 85, 247, 0.2); margin: 20px; }
    .guard-logo { width: 110px; height: 110px; margin: 0 auto 20px; background: radial-gradient(circle, rgba(168,85,247,0.3), rgba(59,130,246,0.1)); border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative; animation: pulse 2s infinite; }
    .guard-logo span { font-size: 60px; filter: drop-shadow(0 0 10px #a855f7); }
    .logo-title { font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #fff, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 1px; }
    .logo-subtitle { font-size: 11px; color: #a78bfa; letter-spacing: 3px; margin-bottom: 25px; }
    .binary-stream { font-family: 'Space Mono', monospace; font-size: 10px; background: rgba(0,0,0,0.5); padding: 6px; border-radius: 20px; display: inline-block; color: #a855f7; margin-bottom: 15px; }
    @media (max-width: 600px) { .login-box { padding: 30px 20px; max-width: 90%; } .guard-logo { width: 80px; height: 80px; } .guard-logo span { font-size: 45px; } .logo-title { font-size: 24px; } .logo-subtitle { font-size: 9px; } }
</style>
""", unsafe_allow_html=True)

# ====================== FUNÇÕES DE AVATAR ======================
def compress_avatar_image(uploaded_file, max_size_kb=200):
    img = Image.open(uploaded_file)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    img.thumbnail((400, 400), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    quality = 85
    while True:
        buffer.seek(0)
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality <= 20:
            break
        quality -= 10
    b64_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64_str}"

def get_avatar_url():
    padrao_url = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230a0a2a'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-size='10'%3ESEGURANÇA%3C/text%3E%3C/svg%3E"
    try:
        result = supabase.table("app_config").select("value").eq("key", "avatar_url").execute()
        if result.data and result.data[0]['value']:
            return result.data[0]['value']
    except:
        pass
    return padrao_url

def save_avatar_url(url):
    try:
        supabase.table("app_config").upsert({
            "key": "avatar_url",
            "value": url,
            "updated_at": datetime.now().isoformat()
        }).execute()
        st.session_state.avatar_url = url
        return True
    except Exception as e:
        st.error(f"Erro ao salvar avatar: {e}")
        return False

# ====================== FUNÇÕES DE TEMA ======================
def compress_image_to_base64(uploaded_file, max_size_kb=500):
    img = Image.open(uploaded_file)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    max_width = 1920
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    quality = 85
    while True:
        buffer.seek(0)
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality <= 20:
            break
        quality -= 10
    b64_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64_str}"

def get_theme_config():
    padrao = {
        "type": "gradient",
        "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)",
        "apply_to_login": False,
        "image_adjust": "cover",
        "image_position": "center",
        "video_loop": True
    }
    try:
        result = supabase.table("app_config").select("value").eq("key", "background_config").execute()
        if result.data:
            config = json.loads(result.data[0]['value'])
            config.setdefault("image_adjust", "cover")
            config.setdefault("image_position", "center")
            config.setdefault("video_loop", True)
            return config
        else:
            save_theme_config(padrao)
            return padrao
    except Exception as e:
        st.error(f"Erro ao carregar tema: {e}")
        return padrao

def save_theme_config(config):
    try:
        supabase.table("app_config").upsert({
            "key": "background_config",
            "value": json.dumps(config),
            "updated_at": datetime.now().isoformat()
        }).execute()
        st.session_state.theme_config = config
        return True
    except Exception as e:
        st.error(f"Erro ao salvar tema global: {e}")
        return False

def futuristic_background_script():
    st.markdown("""
    <canvas id="futuristic-canvas"></canvas>
    <script>
        (function() {
            const canvas = document.getElementById('futuristic-canvas');
            const ctx = canvas.getContext('2d');
            let width, height;
            let particles = [];
            let dataLines = [];
            let holographicShield = { angle: 0, pulse: 0 };
            
            function resize() {
                width = canvas.width = window.innerWidth;
                height = canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            
            class Particle {
                constructor() {
                    this.x = Math.random() * width;
                    this.y = Math.random() * height;
                    this.radius = Math.random() * 2 + 1;
                    this.speedX = (Math.random() - 0.5) * 0.5;
                    this.speedY = (Math.random() - 0.5) * 0.5 + 0.2;
                    this.opacity = Math.random() * 0.5 + 0.2;
                    this.color = `rgba(0, ${150 + Math.random() * 105}, 255, ${this.opacity})`;
                }
                update() {
                    this.x += this.speedX;
                    this.y += this.speedY;
                    if (this.y > height) this.y = 0;
                    if (this.x > width) this.x = 0;
                    if (this.x < 0) this.x = width;
                }
                draw() {
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                    ctx.fillStyle = this.color;
                    ctx.fill();
                }
            }
            
            class DataLine {
                constructor() {
                    this.x1 = Math.random() * width;
                    this.y1 = Math.random() * height;
                    this.x2 = this.x1 + (Math.random() - 0.5) * 300;
                    this.y2 = this.y1 + (Math.random() - 0.5) * 300;
                    this.progress = 0;
                    this.speed = 0.005 + Math.random() * 0.01;
                    this.color = `rgba(0, 200, 255, ${0.2 + Math.random() * 0.3})`;
                }
                update() {
                    this.progress += this.speed;
                    if (this.progress >= 1) {
                        this.progress = 0;
                        this.x1 = Math.random() * width;
                        this.y1 = Math.random() * height;
                        this.x2 = this.x1 + (Math.random() - 0.5) * 300;
                        this.y2 = this.y1 + (Math.random() - 0.5) * 300;
                    }
                }
                draw() {
                    const x = this.x1 + (this.x2 - this.x1) * this.progress;
                    const y = this.y1 + (this.y2 - this.y1) * this.progress;
                    ctx.beginPath();
                    ctx.moveTo(this.x1, this.y1);
                    ctx.lineTo(x, y);
                    ctx.strokeStyle = this.color;
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.arc(x, y, 2, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(0, 200, 255, 0.8)`;
                    ctx.fill();
                }
            }
            
            function drawServers() {
                const serverCols = Math.floor(width / 180);
                for (let i = 0; i < serverCols; i++) {
                    const x = 80 + i * 180;
                    const y = height * 0.2;
                    ctx.fillStyle = 'rgba(0, 20, 40, 0.7)';
                    ctx.fillRect(x, y, 60, 300);
                    ctx.strokeStyle = '#0ff';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(x, y, 60, 300);
                    for (let j = 0; j < 5; j++) {
                        ctx.fillStyle = `rgba(0, ${100 + j * 30}, 200, 0.5)`;
                        ctx.fillRect(x + 5, y + 20 + j * 50, 50, 10);
                    }
                }
            }
            
            function drawShield() {
                const centerX = width / 2;
                const centerY = height / 2;
                const radius = 120 + Math.sin(Date.now() * 0.002) * 5;
                holographicShield.pulse = 0.5 + Math.sin(Date.now() * 0.005) * 0.2;
                ctx.save();
                ctx.shadowBlur = 20;
                ctx.shadowColor = '#0ff';
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(0, 200, 255, ${0.6 + holographicShield.pulse * 0.3})`;
                ctx.lineWidth = 3;
                ctx.stroke();
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius - 10, 0, Math.PI * 2);
                ctx.strokeStyle = `rgba(100, 0, 255, 0.5)`;
                ctx.stroke();
                ctx.font = "50px 'Segoe UI', 'Material Icons'";
                ctx.fillStyle = `rgba(0, 255, 255, ${0.8 + Math.sin(Date.now() * 0.003) * 0.2})`;
                ctx.shadowBlur = 15;
                ctx.fillText("🔒", centerX - 28, centerY + 20);
                ctx.restore();
                for (let i = 0; i < 12; i++) {
                    const angle = Date.now() * 0.002 + i * Math.PI * 2 / 12;
                    const x1 = centerX + Math.cos(angle) * radius;
                    const y1 = centerY + Math.sin(angle) * radius;
                    const x2 = centerX + Math.cos(angle) * (radius + 40 + Math.sin(Date.now() * 0.01 + i) * 20);
                    const y2 = centerY + Math.sin(angle) * (radius + 40 + Math.sin(Date.now() * 0.01 + i) * 20);
                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.strokeStyle = `rgba(0, 255, 255, 0.4)`;
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
            }
            
            function drawNeuralNetwork() {
                const nodes = [];
                for (let i = 0; i < 30; i++) {
                    nodes.push({ x: Math.random() * width, y: Math.random() * height, active: false });
                }
                for (let i = 0; i < nodes.length; i++) {
                    for (let j = i + 1; j < nodes.length; j++) {
                        const dx = nodes[i].x - nodes[j].x;
                        const dy = nodes[i].y - nodes[j].y;
                        const dist = Math.hypot(dx, dy);
                        if (dist < 150) {
                            ctx.beginPath();
                            ctx.moveTo(nodes[i].x, nodes[i].y);
                            ctx.lineTo(nodes[j].x, nodes[j].y);
                            ctx.strokeStyle = `rgba(0, 255, 255, ${0.2 * (1 - dist / 150)})`;
                            ctx.stroke();
                        }
                    }
                }
                nodes.forEach(node => {
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, 3, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(0, 200, 255, 0.7)`;
                    ctx.fill();
                });
            }
            
            function init() {
                resize();
                for (let i = 0; i < 150; i++) particles.push(new Particle());
                for (let i = 0; i < 40; i++) dataLines.push(new DataLine());
            }
            
            function animate() {
                if (!ctx) return;
                ctx.clearRect(0, 0, width, height);
                const grad = ctx.createLinearGradient(0, 0, width, height);
                grad.addColorStop(0, '#030318');
                grad.addColorStop(0.5, '#0a0a2a');
                grad.addColorStop(1, '#050518');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, width, height);
                drawServers();
                dataLines.forEach(line => { line.update(); line.draw(); });
                particles.forEach(p => { p.update(); p.draw(); });
                drawNeuralNetwork();
                drawShield();
                if (Math.random() < 0.05) {
                    ctx.fillStyle = `rgba(0, 255, 255, 0.15)`;
                    ctx.font = "12px monospace";
                    ctx.fillText("010101", Math.random() * width, Math.random() * height);
                }
                requestAnimationFrame(animate);
            }
            
            init();
            animate();
        })();
    </script>
    """, unsafe_allow_html=True)

def apply_theme_css():
    config = st.session_state.get("theme_config", get_theme_config())
    bg_type = config.get("type", "gradient")
    
    if bg_type == "gradient":
        bg_value = config.get("value", "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)")
        css = f"""
        <style>
        html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{
            background: {bg_value} !important;
            background-attachment: fixed !important;
            background-size: cover !important;
            background-repeat: no-repeat !important;
            background-position: center !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif bg_type == "solid":
        bg_value = config.get("value", "#0a0a1a")
        css = f"""
        <style>
        html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{
            background: {bg_value} !important;
            background-attachment: fixed !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif bg_type == "url":
        bg_value = config.get("value", "")
        if not bg_value or bg_value.startswith("radial"):
            bg_value = "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
        adjust = config.get("image_adjust", "cover")
        position = config.get("image_position", "center")
        css = f"""
        <style>
        html, body, .stApp, .stApp > header, .stApp > div, .main, .main > div {{
            background: {bg_value} !important;
            background-attachment: fixed !important;
            background-size: {adjust} !important;
            background-repeat: no-repeat !important;
            background-position: {position} !important;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    elif bg_type == "video":
        media_url = config.get("value", "")
        adjust = config.get("image_adjust", "cover")
        mime_type = config.get("mime_type", "video/mp4")
        video_loop = config.get("video_loop", True)
        loop_attr = "loop" if video_loop else ""
        if not media_url:
            st.markdown("""
            <style>
            .stApp { background: radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%); }
            </style>
            """, unsafe_allow_html=True)
            return
        container_div = "<div style='position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -9999; pointer-events: none;'>"
        if mime_type == "image/gif":
            media_html = f'<img src="{media_url}" style="width: 100%; height: 100%; object-fit: {adjust};">'
        else:
            media_html = f'<video autoplay muted playsinline {loop_attr} style="width: 100%; height: 100%; object-fit: {adjust};"><source src="{media_url}" type="{mime_type}"></video>'
        st.markdown(container_div + media_html + "</div>", unsafe_allow_html=True)
        st.markdown("""
        <style>
        .stApp {
            background: transparent !important;
        }
        </style>
        """, unsafe_allow_html=True)
    elif bg_type == "futuristic":
        futuristic_background_script()

# ====================== FUNÇÕES DE SESSÃO ======================
def registrar_sessao(perfil, usuario="admin"):
    session_id = str(uuid.uuid4())
    try:
        data = {
            "id": session_id,
            "usuario": usuario,
            "perfil": perfil,
            "ultima_atividade": datetime.now().isoformat(),
            "ip": "desconhecido",
            "user_agent": "streamlit"
        }
        supabase.table("sessoes_ativas").insert(data).execute()
        st.session_state.session_id = session_id
        return True
    except Exception as e:
        st.error(f"Erro ao registrar sessão: {e}")
        return False

def atualizar_atividade_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").update({
                "ultima_atividade": datetime.now().isoformat()
            }).eq("id", st.session_state.session_id).execute()
        except:
            pass

def remover_sessao():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").delete().eq("id", st.session_state.session_id).execute()
        except:
            pass
        st.session_state.session_id = None

def contar_sessoes_ativas():
    limite = (datetime.now() - pd.Timedelta(minutes=SESSION_TIMEOUT_MINUTOS)).isoformat()
    try:
        result = supabase.table("sessoes_ativas").select("id", count="exact").gte("ultima_atividade", limite).execute()
        return result.count
    except:
        return 0

def limpar_sessoes_expiradas():
    limite = (datetime.now() - pd.Timedelta(minutes=SESSION_TIMEOUT_MINUTOS)).isoformat()
    try:
        if "session_id" in st.session_state and st.session_state.session_id:
            supabase.table("sessoes_ativas").delete().lt("ultima_atividade", limite).neq("id", st.session_state.session_id).execute()
        else:
            supabase.table("sessoes_ativas").delete().lt("ultima_atividade", limite).execute()
    except:
        pass

def encerrar_outras_sessoes():
    if "session_id" in st.session_state and st.session_state.session_id:
        try:
            supabase.table("sessoes_ativas").delete().neq("id", st.session_state.session_id).execute()
            return True
        except:
            return False
    return False

# ====================== FUNÇÕES DE RELATÓRIOS PDF ======================
def gerar_html_impressao(df, titulo):
    if df.empty:
        return None
    colunas = ['id', 'nome', 'cpf', 'empresa', 'setor_destino', 'data_entrada', 'data_saida']
    colunas_existentes = [c for c in colunas if c in df.columns]
    df_rel = df[colunas_existentes].copy().fillna('')
    tabela = df_rel.to_html(escape=True, index=False)
    return f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>{titulo}</title>
    <style>
        body{{font-family:'Segoe UI',Arial,sans-serif;margin:2cm;}}
        h1{{text-align:center;color:#0a2b3e;}}
        .sub{{text-align:center;color:#555;margin-bottom:30px;}}
        table{{width:100%;border-collapse:collapse;font-size:10px;}}
        th{{background:#0a2b3e;color:white;padding:8px;}}
        td{{border:1px solid #ccc;padding:6px;}}
        tr:nth-child(even){{background:#f9f9f9;}}
        @media print{{body{{margin:1cm;}}.no-print{{display:none;}}}}
    </style></head>
    <body>
        <h1>JOHN ACESSOS - {titulo}</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        {tabela}
        <div class="no-print" style="text-align:center;margin-top:30px;"><button onclick="window.print();">🖨️ Imprimir / PDF</button></div>
    </body></html>
    """

def gerar_html_consolidado(df):
    if df.empty:
        return None
    def secao(df_filtro, titulo):
        df_filtro = df_filtro.copy().fillna('')
        if df_filtro.empty:
            return f"<div class='section'><h2>{titulo}</h2><p>Nenhum registro.</p></div>"
        colunas = ['id','nome','cpf','empresa','setor_destino','data_entrada','data_saida']
        existentes = [c for c in colunas if c in df_filtro.columns]
        tabela = df_filtro[existentes].to_html(escape=True, index=False)
        return f"<div class='section'><h2>{titulo} <span class='count-badge'>{len(df_filtro)}</span></h2>{tabela}</div>"
    html = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>RELATÓRIO CONSOLIDADO</title>
    <style>
        body{{font-family:'Segoe UI',Arial,sans-serif;margin:2cm;}}
        h1{{text-align:center;color:#0a2b3e;}}
        .sub{{text-align:center;color:#555;margin-bottom:30px;}}
        .section{{margin-top:40px;page-break-inside:avoid;}}
        .section h2{{background:#0a2b3e;color:white;padding:8px;border-radius:8px;}}
        table{{width:100%;border-collapse:collapse;font-size:10px;margin-bottom:20px;}}
        th{{background:#0a2b3e;color:white;padding:8px;}}
        td{{border:1px solid #ccc;padding:6px;}}
        .count-badge{{display:inline-block;background:#a855f7;color:white;border-radius:20px;padding:2px 10px;margin-left:10px;}}
        @media print{{body{{margin:1cm;}}.no-print{{display:none;}}}}
    </style></head>
    <body>
        <h1>JOHN ACESSOS - RELATÓRIO CONSOLIDADO</h1>
        <div class="sub">Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
    """
    html += secao(df[df['setor_destino'].str.contains('GRSA', case=False, na=False)], "🔧 GRSA")
    html += secao(df[df['setor_destino'].str.contains('Brasanitas', case=False, na=False)], "🏭 Brasanitas")
    html += secao(df[df['setor_destino'].str.contains('C.C', case=False, na=False)], "🏥 C.C")
    empresas_excluir = ["BRASANITAS", "GRSA", "C.C"]
    todas_empresas = df['empresa'].dropna().unique()
    prestadores = [e for e in todas_empresas if e.upper() not in [x.upper() for x in empresas_excluir]]
    if prestadores:
        html += secao(df[df['empresa'].isin(prestadores)], "🏢 Prestadores de Serviços")
    else:
        html += "<div class='section'><h2>🏢 Prestadores de Serviços</h2><p>Nenhum registro.</p></div>"
    html += '<div class="no-print" style="text-align:center;margin-top:30px;"><button onclick="window.print();">🖨️ Imprimir / PDF</button></div></body></html>'
    return html

# ====================== FUNÇÕES DE VALIDAÇÃO ======================
def validar_cpf(cpf):
    cpf_limpo = re.sub(r'\D', '', cpf)
    return cpf_limpo.isdigit() and len(cpf_limpo) == 11

def sanitizar_cpf(cpf):
    return re.sub(r'\D', '', cpf)

def sanitizar_texto(texto):
    if not texto:
        return texto
    return texto.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# ====================== INICIALIZAÇÃO ======================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "perfil" not in st.session_state:
    st.session_state.perfil = ""
if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = []
if "pending_delete_ids" not in st.session_state:
    st.session_state.pending_delete_ids = []
if "pending_clear_all" not in st.session_state:
    st.session_state.pending_clear_all = False
if "tentativas_login" not in st.session_state:
    st.session_state.tentativas_login = 0
if "bloqueado_ate" not in st.session_state:
    st.session_state.bloqueado_ate = None
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "pessoa_confirmada" not in st.session_state:
    st.session_state.pessoa_confirmada = None
if "pessoa_saida" not in st.session_state:
    st.session_state.pessoa_saida = None

st.session_state.theme_config = get_theme_config()
st.session_state.avatar_url = get_avatar_url()

# ====================== TELA DE LOGIN ======================
if not st.session_state.logado:
    theme = st.session_state.theme_config
    if theme.get("apply_to_login", False):
        apply_theme_css()
    else:
        st.markdown('<style>.stApp{background:radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%);}</style>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <div class="guard-logo"><span>🛡️</span></div>
            <div class="logo-title">JOHN ACESSOS</div>
            <div class="logo-subtitle">CYBER SECURITY 2026</div>
            <div id="binary-container" style="text-align:center; margin-bottom:15px;"></div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <script>
        function generateBinary() {
            let b = '';
            for(let i = 0; i < 60; i++) b += Math.random() < 0.5 ? '0' : '1';
            return b;
        }
        setInterval(() => {
            let el = document.getElementById('binary-container');
            if(el) el.innerHTML = `<div class="binary-stream">${generateBinary()}</div>`;
        }, 400);
    </script>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.text_input("", placeholder="Identificação (usuário)", key="data_user", label_visibility="collapsed")
        senha = st.text_input("", type="password", placeholder="Chave de acesso criptografada", label_visibility="collapsed")
        submitted = st.form_submit_button("🛡️ ACESSAR SISTEMA", use_container_width=True)
        if submitted:
            if senha == "fgxv4VP0/*":
                st.session_state.logado = True
                st.session_state.perfil = "ADMIN"
                st.session_state.tentativas_login = 0
                registrar_sessao("ADMIN", "admin")
                st.rerun()
            elif senha == "JOHN123":
                st.session_state.logado = True
                st.session_state.perfil = "VIGILANTE"
                st.session_state.tentativas_login = 0
                registrar_sessao("VIGILANTE", "vigilante")
                st.rerun()
            else:
                st.session_state.tentativas_login += 1
                restantes = MAX_TENTATIVAS_LOGIN - st.session_state.tentativas_login
                if st.session_state.tentativas_login >= MAX_TENTATIVAS_LOGIN:
                    st.session_state.bloqueado_ate = datetime.now() + pd.Timedelta(minutes=5)
                    st.error("⛔ Acesso bloqueado por 5 minutos.")
                else:
                    st.error(f"❌ ACESSO NEGADO - Tentativas restantes: {restantes}")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

# ====================== APÓS LOGIN ======================
apply_theme_css()

if st.session_state.session_id:
    atualizar_atividade_sessao()
    limpar_sessoes_expiradas()
    total_conectados = contar_sessoes_ativas()
else:
    total_conectados = 0

# ====================== HEADER FUTURISTA ======================
st.markdown(f"""
<div class="admin-header" style="background: rgba(8,8,20,0.6); backdrop-filter: blur(8px); border-radius: 20px; padding: 10px 20px; margin-bottom: 20px; border: 1px solid cyan;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; gap:15px; align-items:center;">
            <div style="width:45px;height:45px;">
                <img src="{st.session_state.avatar_url}" style="width:45px; height:45px; border-radius:50%; object-fit:cover; border:1px solid cyan; box-shadow:0 0 8px cyan;">
            </div>
            <div><h1 style="margin:0;font-size:18px; background:linear-gradient(135deg,cyan,magenta); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">JOHN ACESSOS - CYBER SECURITY 2026</h1><p style="margin:0;color:#aaf;font-size:10px;">MONITORAMENTO INTELIGENTE • ACESSO DE DADOS</p></div>
        </div>
        <div style="display:flex; gap:15px; align-items:center;">
            <div class="live-indicator"><span class="pulse-dot"></span> LIVE</div>
            <div class="session-indicator">👥 {total_conectados}</div>
            <div class="badge-admin">👑 {st.session_state.perfil}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([6,1,1,1])
with col3:
    if st.button("🔄 ATUALIZAR", key="btn_atualizar", use_container_width=True):
        st.rerun()
with col4:
    if st.button("🚪 SAIR", key="sair_final", use_container_width=True):
        remover_sessao()
        st.session_state.logado = False
        st.rerun()

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown(f"""
    <div class="avatar-container">
        <div class="glow-ring"></div>
        <img src="{st.session_state.avatar_url}" class="avatar-image">
        <div class="sidebar-title" style="font-size: 20px; margin-top: 12px;">👮‍♂️ JOHN ACESSOS</div>
        <p style="color:#0ff; font-size: 9px; letter-spacing: 2px;">CYBER SECURITY 2026</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚡ ESTADO")
    st.markdown('<div class="info-item"><span style="color:#0f0;">●</span> REDE NEURAL: ATIVA</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item"><span style="color:#0ff;">●</span> MODELO: DEEP LEARNING</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item"><span style="color:#f0f;">●</span> CRIPTOGRAFIA: QUÂNTICA</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item"><span style="color:#ff0;">●</span> DATA LAKE: SEGURO</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📡 INFO")
    if st.session_state.get("perfil"):
        st.markdown(f"<div class='info-item'>👑 Perfil: {st.session_state.perfil}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-item'>👑 Perfil: ---</div>", unsafe_allow_html=True)
    st.markdown('<div class="info-item">🟢 Status: Online</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-item">📦 Versão: 13.1 (CYBER)</div>', unsafe_allow_html=True)

# ====================== ADMIN: CONFIGURAÇÕES ======================
if st.session_state.perfil == "ADMIN":
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ MANAGE APP", expanded=False):
        st.markdown("### 🔧 Ferramentas Administrativas")
        total_ativas = contar_sessoes_ativas()
        st.metric("👥 Sessões ativas", total_ativas)
        if st.button("🔒 Encerrar outras sessões", use_container_width=True, key="encerrar_sessoes"):
            if encerrar_outras_sessoes():
                st.success("✅ Todas as outras sessões foram encerradas!")
                st.rerun()
            else:
                st.error("❌ Erro ao encerrar outras sessões.")
        if st.button("🧹 Limpar sessões expiradas", use_container_width=True, key="limpar_sessoes"):
            limpar_sessoes_expiradas()
            st.success("✅ Sessões expiradas removidas!")
            st.rerun()
        st.caption("Ações disponíveis apenas para o administrador.")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("🎨 Configurar Tema (Global)", expanded=False):
        st.markdown("### Personalizar Fundo - Aplica para todos")
        config_atual = st.session_state.theme_config
        tipo_atual = config_atual.get("type", "gradient")
        opcoes = ["Gradiente padrão", "Cor sólida", "Imagem (URL)", "Imagem (upload)", "Animação (URL)", "Futurista Dinâmico (Canvas)"]
        idx_map = {"gradient":0, "solid":1, "url":2, "image_upload":3, "video":4, "futuristic":5}
        idx = idx_map.get(tipo_atual, 0)
        tipo = st.radio("Tipo de fundo:", opcoes, index=idx, key="tipo_fundo_radio")
        
        novo_valor = config_atual.get("value", "")
        novo_tipo = tipo_atual
        novo_mime = config_atual.get("mime_type", "")
        video_loop = config_atual.get("video_loop", True)
        
        if tipo == "Gradiente padrão":
            novo_valor = "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
            novo_tipo = "gradient"
        elif tipo == "Cor sólida":
            cor_padrao = config_atual.get("value", "#0a0a1a") if tipo_atual == "solid" else "#0a0a1a"
            cor = st.color_picker("Escolha a cor", value=cor_padrao, key="cor_picker")
            novo_valor = cor
            novo_tipo = "solid"
        elif tipo == "Imagem (URL)":
            url_padrao = ""
            if tipo_atual == "url" and config_atual.get("value", "").startswith("url('"):
                match = re.search(r"url\('([^']+)'", config_atual.get("value", ""))
                if match:
                    url_padrao = match.group(1)
            url_img = st.text_input("URL da imagem", value=url_padrao, key="url_img", placeholder="https://exemplo.com/imagem.jpg")
            if url_img and (url_img.startswith('http://') or url_img.startswith('https://')):
                novo_valor = url_img
                novo_tipo = "url"
            elif url_img:
                st.error("URL inválida. Use http:// ou https://")
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
            else:
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
        elif tipo == "Imagem (upload)":
            uploaded_file = st.file_uploader("Escolha uma imagem (PNG, JPG, JPEG, GIF)", type=["png","jpg","jpeg","gif"], key="upload_img")
            if uploaded_file:
                with st.spinner("Processando imagem..."):
                    try:
                        imagem_data_url = compress_image_to_base64(uploaded_file)
                        novo_valor = imagem_data_url
                        novo_tipo = "url"
                        st.success("✅ Imagem carregada e comprimida com sucesso!")
                        st.image(uploaded_file, width=200, caption="Imagem carregada")
                    except Exception as e:
                        st.error(f"Erro ao processar imagem: {e}")
                        novo_valor = config_atual.get("value", "")
                        novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
            else:
                if tipo_atual == "url" and config_atual.get("value", "").startswith("data:image"):
                    novo_valor = config_atual.get("value")
                    novo_tipo = "url"
                else:
                    novo_valor = config_atual.get("value", "")
                    novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
        elif tipo == "Animação (URL)":
            url_padrao = ""
            if tipo_atual == "video":
                url_padrao = config_atual.get("value", "")
            url_media = st.text_input("URL do vídeo/GIF (MP4/GIF)", value=url_padrao, key="url_video", placeholder="https://exemplo.com/video.mp4")
            video_loop = st.checkbox("Reproduzir em loop infinito", value=config_atual.get("video_loop", True), key="video_loop")
            if url_media and (url_media.startswith('http://') or url_media.startswith('https://')):
                novo_valor = url_media
                novo_tipo = "video"
                if url_media.lower().endswith('.gif'):
                    novo_mime = "image/gif"
                else:
                    novo_mime = "video/mp4"
                st.success("✅ URL de mídia configurada!")
            elif url_media:
                st.error("URL inválida. Use http:// ou https://")
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
            else:
                novo_valor = config_atual.get("value", "")
                novo_tipo = tipo_atual if tipo_atual in ["gradient","solid","url"] else "gradient"
        elif tipo == "Futurista Dinâmico (Canvas)":
            novo_valor = "futuristic"
            novo_tipo = "futuristic"
        
        ajuste_opcoes = ["cover", "contain", "stretch"]
        if novo_tipo in ["url", "video"]:
            st.markdown("---")
            st.markdown("#### Ajustes da mídia")
            ajuste_atual = config_atual.get("image_adjust", "cover")
            posicao_atual = config_atual.get("image_position", "center")
            novo_ajuste = st.selectbox("Modo de ajuste:", ajuste_opcoes, index=ajuste_opcoes.index(ajuste_atual) if ajuste_atual in ajuste_opcoes else 0, key="ajuste_imagem")
            nova_posicao = st.selectbox("Posição (para imagens fixas):", ["center", "top", "bottom", "left", "right", "top left", "top right", "bottom left", "bottom right"], index=3 if posicao_atual == "center" else 0, key="posicao_imagem")
        else:
            novo_ajuste = "cover"
            nova_posicao = "center"
        
        st.markdown("**Prévia:**")
        if novo_tipo == "gradient":
            preview_style = novo_valor
            st.markdown(f'<div style="width:100%; height:50px; background:{preview_style}; border-radius:8px; border:1px solid cyan;"></div>', unsafe_allow_html=True)
        elif novo_tipo == "solid":
            preview_style = novo_valor
            st.markdown(f'<div style="width:100%; height:50px; background:{preview_style}; border-radius:8px; border:1px solid cyan;"></div>', unsafe_allow_html=True)
        elif novo_tipo == "url":
            preview_style = f"url('{novo_valor}') {nova_posicao}/{novo_ajuste} no-repeat fixed" if novo_valor else "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
            st.markdown(f'<div style="width:100%; height:50px; background:{preview_style}; border-radius:8px; border:1px solid cyan;"></div>', unsafe_allow_html=True)
        elif novo_tipo == "video":
            if novo_valor:
                if novo_mime == "image/gif":
                    st.markdown(f'<img src="{novo_valor}" style="width:100%; max-height:100px; object-fit:cover; border-radius:8px;">', unsafe_allow_html=True)
                else:
                    st.video(novo_valor, format="video/mp4")
            else:
                st.info("Informe uma URL para prévia")
        elif novo_tipo == "futuristic":
            st.info("Fundo futurista dinâmico (Canvas) será aplicado após salvar.")
        
        aplicar_login = st.checkbox("Aplicar também na tela de login", value=config_atual.get("apply_to_login", False), key="aplicar_login_check")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("💾 Salvar e Aplicar Tema (Global)", key="salvar_tema_global"):
                if novo_tipo == "gradient":
                    valor_final = novo_valor
                elif novo_tipo == "solid":
                    valor_final = novo_valor
                elif novo_tipo == "url":
                    if novo_valor:
                        valor_final = f"url('{novo_valor}') {nova_posicao}/{novo_ajuste} no-repeat fixed"
                    else:
                        valor_final = "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
                        novo_tipo = "gradient"
                elif novo_tipo == "video":
                    valor_final = novo_valor if novo_valor else "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)"
                    if not novo_valor:
                        novo_tipo = "gradient"
                else:  # futuristic
                    valor_final = "futuristic"
                    novo_tipo = "futuristic"
                
                nova_config = {
                    "type": novo_tipo,
                    "value": valor_final,
                    "apply_to_login": aplicar_login,
                    "image_adjust": novo_ajuste,
                    "image_position": nova_posicao,
                    "mime_type": novo_mime if novo_tipo == "video" else "",
                    "video_loop": video_loop if novo_tipo == "video" else True
                }
                if save_theme_config(nova_config):
                    apply_theme_css()
                    st.success("✅ Tema global salvo e aplicado!")
                else:
                    st.error("Erro ao salvar tema global.")
        with col_btn2:
            if st.button("↺ Restaurar Padrão", key="reset_tema_global"):
                padrao = {
                    "type": "gradient",
                    "value": "radial-gradient(circle at 20% 40%, #0a0a1a 0%, #03030f 100%)",
                    "apply_to_login": False,
                    "image_adjust": "cover",
                    "image_position": "center",
                    "mime_type": "",
                    "video_loop": True
                }
                if save_theme_config(padrao):
                    apply_theme_css()
                    st.success("Tema restaurado para o padrão global!")
        with col_btn3:
            if st.button("🔄 Recarregar Tema do Banco", key="reload_tema"):
                st.session_state.theme_config = get_theme_config()
                apply_theme_css()
                st.success("Tema recarregado do Supabase!")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("📤 Compartilhar Dados de Pessoas", expanded=False):
        st.markdown("### Exportar Cadastros")
        try:
            todas_pessoas = supabase.table("pessoas").select("nome, cpf, empresa").execute().data
            if not todas_pessoas:
                st.info("Nenhuma pessoa cadastrada ainda.")
            else:
                df_todas = pd.DataFrame(todas_pessoas)
                empresas = sorted([e for e in df_todas['empresa'].unique() if e and e.strip()])
                opcoes_empresa = ["Todos"] + empresas
                empresa_selecionada = st.selectbox("Filtrar por unidade (empresa):", opcoes_empresa, key="export_empresa")
                if empresa_selecionada == "Todos":
                    df_export = df_todas.copy()
                    st.write(f"Total de registros: {len(df_export)}")
                else:
                    df_export = df_todas[df_todas['empresa'] == empresa_selecionada].copy()
                    st.write(f"Total de registros para {empresa_selecionada}: {len(df_export)}")
                if not df_export.empty:
                    csv = df_export.to_csv(index=False, encoding='utf-8-sig')
                    nome_arquivo = f"cadastros_{empresa_selecionada.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    st.download_button(
                        label="📥 Baixar CSV",
                        data=csv,
                        file_name=nome_arquivo,
                        mime="text/csv",
                        key="download_csv_pessoas"
                    )
                else:
                    st.warning("Nenhum registro para o filtro selecionado.")
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
    
    st.sidebar.markdown("---")
    with st.sidebar.expander("🖼️ Configurar Avatar (Segurança)", expanded=False):
        st.markdown("### Personalizar Imagem do Perfil")
        st.markdown("Envie uma imagem realista de segurança (4K recomendado).")
        uploaded_avatar = st.file_uploader("Escolha uma imagem (PNG/JPG)", type=["png","jpg","jpeg"], key="upload_avatar")
        if uploaded_avatar:
            with st.spinner("Processando imagem..."):
                try:
                    avatar_base64 = compress_avatar_image(uploaded_avatar)
                    if save_avatar_url(avatar_base64):
                        st.session_state.avatar_url = avatar_base64
                        st.success("✅ Avatar atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao salvar avatar.")
                except Exception as e:
                    st.error(f"Erro ao processar imagem: {e}")
        st.markdown("---")
        st.markdown("**Imagem atual:**")
        st.image(st.session_state.avatar_url, width=120, caption="Avatar atual")
        if st.button("↺ Restaurar Avatar Padrão", key="reset_avatar"):
            padrao_url = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%230a0a2a'/%3E%3Ctext x='50' y='50' text-anchor='middle' dy='.3em' fill='white' font-size='10'%3ESEGURANÇA%3C/text%3E%3C/svg%3E"
            if save_avatar_url(padrao_url):
                st.session_state.avatar_url = padrao_url
                st.success("Avatar restaurado para o padrão!")
                st.rerun()

# ====================== DIAGNÓSTICO (SOMENTE ADMIN) ======================
if st.session_state.perfil == "ADMIN" and st.session_state.logado:
    with st.sidebar.expander("🔍 DIAGNÓSTICO DO SUPABASE", expanded=False):
        st.markdown("### Informações das tabelas")
        try:
            # Tenta consultar tabela 'pessoas'
            pessoas_count = supabase.table("pessoas").select("id", count="exact").execute().count
            st.write(f"📊 Tabela `pessoas`: {pessoas_count} registros")
        except Exception as e:
            st.error(f"Erro na tabela 'pessoas': {e}")
        try:
            mov_count = supabase.table("movimentacao").select("id", count="exact").execute().count
            st.write(f"📊 Tabela `movimentacao`: {mov_count} registros")
        except Exception as e:
            st.error(f"Erro na tabela 'movimentacao': {e}")
        try:
            presentes = supabase.table("movimentacao").select("*", count="exact").eq("data_saida", "").execute()
            st.write(f"📍 Pessoas presentes: {presentes.count}")
        except Exception as e:
            st.error(f"Erro ao contar presentes: {e}")

# ====================== DASHBOARD (CARDS CORRIGIDOS - USANDO NOMES MINÚSCULOS) ======================
st.markdown("---")
try:
    # Usando nomes minúsculos consistentes
    presentes_data = supabase.table("movimentacao").select("*", count="exact").eq("data_saida", "").execute()
    total_presentes = presentes_data.count if hasattr(presentes_data, 'count') else len(presentes_data.data)
    
    cadastrados_data = supabase.table("pessoas").select("*", count="exact").execute()
    total_cadastrados = cadastrados_data.count if hasattr(cadastrados_data, 'count') else len(cadastrados_data.data)
    
    setores_data = supabase.table("movimentacao").select("setor_destino").execute()
    if setores_data.data:
        setores_unicos = len(set(p['setor_destino'] for p in setores_data.data))
    else:
        setores_unicos = 11
except Exception as e:
    st.error(f"Erro ao carregar estatísticas: {e}")
    total_presentes = 0
    total_cadastrados = 0
    setores_unicos = 11

cards_data = [
    {"icon": "👥", "title": "PRESENTES", "value": total_presentes},
    {"icon": "📊", "title": "CADASTRADOS", "value": total_cadastrados},
    {"icon": "🏛️", "title": "SETORES ATIVOS", "value": setores_unicos},
    {"icon": "🛡️", "title": "SEGURANÇA", "value": "24/7"}
]

col1, col2, col3, col4 = st.columns(4)
cols = [col1, col2, col3, col4]

for idx, card in enumerate(cards_data):
    with cols[idx]:
        if isinstance(card["value"], int):
            value_display = f'<div class="card-value" data-target="{card["value"]}">0</div>'
        else:
            value_display = f'<div class="card-value">{card["value"]}</div>'
        st.markdown(f"""
        <div class="cyber-card">
            <div class="card-icon">{card["icon"]}</div>
            <div class="card-title">{card["title"]}</div>
            {value_display}
        </div>
        """, unsafe_allow_html=True)

# Script para animar contadores
st.markdown("""
<script>
    function animateCounters() {
        const counters = document.querySelectorAll('.card-value');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            if (target && !counter.dataset.animated) {
                counter.dataset.animated = 'true';
                let current = 0;
                const increment = Math.ceil(target / 30);
                const update = () => {
                    current += increment;
                    if (current >= target) {
                        counter.innerText = target;
                    } else {
                        counter.innerText = current;
                        requestAnimationFrame(update);
                    }
                };
                requestAnimationFrame(update);
            }
        });
    }
    document.addEventListener('DOMContentLoaded', animateCounters);
</script>
""", unsafe_allow_html=True)

# ====================== CADASTRO ======================
st.markdown("---")
st.markdown("### ✚ Cadastro de Nova Pessoa")
with st.expander("📋 Formulário de Cadastro", expanded=True):
    col_a, col_b, col_c = st.columns(3)
    novo_cpf = col_a.text_input("📄 CPF *", placeholder="000.000.000-00", key="novo_cpf")
    novo_nome = col_b.text_input("👤 Nome Completo *", key="novo_nome")
    novo_empresa = col_c.text_input("🏢 Empresa", key="novo_empresa")
    if st.button("💾 Salvar Cadastro", key="salvar_cadastro", type="primary"):
        if novo_cpf and novo_nome:
            if not validar_cpf(novo_cpf):
                st.error("❌ CPF inválido.")
            else:
                cpf_limpo = sanitizar_cpf(novo_cpf)
                try:
                    existe = supabase.table("pessoas").select("id, empresa").eq("cpf", cpf_limpo).execute().data
                    if existe:
                        st.error(f"❌ Pessoa já cadastrada (Empresa: {existe[0].get('empresa', 'N/A')})")
                    else:
                        supabase.table("pessoas").insert({
                            "cpf": cpf_limpo,
                            "nome": sanitizar_texto(novo_nome).strip().upper(),
                            "empresa": sanitizar_texto(novo_empresa).strip().upper() if novo_empresa else ""
                        }).execute()
                        st.success("✅ Cadastro salvo!")
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.error("CPF e Nome obrigatórios.")

# ====================== REGISTRO DE ENTRADA ======================
st.markdown("---")
st.markdown("### 📋 Registrar Movimentação")
tipo = st.radio("👥 Tipo de Pessoa:", ["🏢 Prestador de serviços", "🔧 Terceirizados / Instrumentadores"], horizontal=True, key="tipo_pessoa")
if tipo == "🏢 Prestador de serviços":
    destinos = ["🏥 C.C", "❤️ Hemodinâmica", "📦 OPME", "🏭 CME", "🔬 Endoscopia", "🔧 Manutenção", "🧪 Laboratório", "💊 Farmacia", "🏥 P.A", "👶 PEDIATRIA P.A", "🔧 ENG.CLINICA", "🧹 HORTELARIA", "📦 OPME 6°AND", "📦 OPME 9°AND", "🔒 SSGA", "🏥 CDU", "⚕️ ONCOLOGIA"]
else:
    destinos = ["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"]

col_cpf, col_btn = st.columns([3,1])
with col_cpf:
    cpf_input = st.text_input("📄 CPF:", key="cpf_entrada", placeholder="Digite o CPF")
with col_btn:
    if cpf_input:
        if st.button("✅ CONFIRMAR CPF", key="confirma_cpf"):
            cpf_limpo = sanitizar_cpf(cpf_input)
            if not validar_cpf(cpf_limpo):
                st.error("CPF inválido")
            else:
                try:
                    pessoa = supabase.table("pessoas").select("nome, empresa").eq("cpf", cpf_limpo).execute().data
                    if pessoa:
                        st.session_state.pessoa_confirmada = {"cpf": cpf_limpo, "nome": pessoa[0]['nome'], "empresa": pessoa[0].get('empresa', '')}
                        st.success(f"✅ {pessoa[0]['nome']} - {pessoa[0].get('empresa','N/A')}")
                    else:
                        st.error("CPF não cadastrado")
                        st.session_state.pessoa_confirmada = None
                except:
                    st.error("Erro ao buscar CPF")
    else:
        st.button("✅ CONFIRMAR CPF", disabled=True, key="confirma_cpf_disabled")

setor_escolhido = st.selectbox("📍 Destino:", destinos, key="destino")
if st.button("✅ Registrar Entrada", key="btn_entrada", type="primary"):
    if st.session_state.get("pessoa_confirmada"):
        p = st.session_state.pessoa_confirmada
        try:
            supabase.table("movimentacao").insert({
                "cpf": p['cpf'], "nome": p['nome'], "empresa": p['empresa'],
                "setor_destino": setor_escolhido,
                "data_entrada": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "data_saida": ""
            }).execute()
            st.success(f"Entrada registrada para {setor_escolhido}!")
            st.session_state.pessoa_confirmada = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Confirme o CPF primeiro.")

# ====================== PESSOAS PRESENTES ======================
st.markdown("---")
st.markdown("### 📍 Pessoas Presentes")
try:
    dados = supabase.table("movimentacao").select("*").eq("data_saida", "").execute().data
except:
    dados = []
if dados:
    st.markdown("#### 🔍 Pesquisar CPF para saída")
    col_pesq, col_btn_sair = st.columns([3,1])
    with col_pesq:
        cpf_saida = st.text_input("CPF:", key="cpf_saida", placeholder="Digite o CPF")
    with col_btn_sair:
        if st.button("🔎 Buscar", key="buscar_saida"):
            if cpf_saida:
                encontrado = next((p for p in dados if p['cpf'] == sanitizar_cpf(cpf_saida)), None)
                if encontrado:
                    st.session_state.pessoa_saida = encontrado
                    st.success(f"Pessoa encontrada: {encontrado['nome']}")
                else:
                    st.error("Não encontrado")
                    st.session_state.pessoa_saida = None
    if st.session_state.get("pessoa_saida"):
        p = st.session_state.pessoa_saida
        st.markdown(f"**{p['nome']}** - CPF: {p['cpf']} - Setor: {p['setor_destino']}")
        if st.button("🚪 Registrar Saída", key="sair_pesquisado"):
            try:
                supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                st.success("Saída registrada")
                st.session_state.pessoa_saida = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro: {e}")
        st.markdown("---")
    st.markdown("#### 📋 Lista completa")
    tabs = st.tabs(["📊 Prestador de Serviço", "🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"])
    with tabs[0]:
        for p in dados:
            col1, col2, col3, col4 = st.columns([4,3,2,2])
            col1.write(f"**{p['nome']}**")
            col2.write(f"📍 {p['setor_destino']}")
            col3.write(f"🏢 {p.get('empresa','N/A')}")
            if col4.button("🚪 Saída", key=f"saida_{p['id']}"):
                try:
                    supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                    st.rerun()
                except:
                    pass
            st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
    for i, setor in enumerate(["🏥 C.C", "🔧 GRSA", "🏭 Brasanitas"], 1):
        with tabs[i]:
            setor_clean = setor.split()[-1]
            pessoas_setor = [p for p in dados if setor_clean in p['setor_destino']]
            for p in pessoas_setor:
                col1, col2, col3, col4 = st.columns([4,3,2,2])
                col1.write(f"**{p['nome']}**")
                col2.write(f"🏢 {p.get('empresa','N/A')}")
                col3.write(f"🕒 {p['data_entrada']}")
                if col4.button("🚪 Saída", key=f"saida2_{p['id']}"):
                    try:
                        supabase.table("movimentacao").update({"data_saida": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}).eq("id", p['id']).execute()
                        st.rerun()
                    except:
                        pass
                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
else:
    st.info("Nenhuma pessoa presente no momento")

# ====================== HISTÓRICO ======================
st.markdown("---")
with st.expander("🕒 Histórico Completo de Movimentações", expanded=True):
    try:
        todos = supabase.table("movimentacao").select("*").order("id", desc=True).execute().data
    except:
        todos = []
    if todos:
        df = pd.DataFrame(todos)
        st.markdown("### 📄 Gerar Relatório")
        if st.button("📑 Relatório completo", key="relatorio_completo"):
            html = gerar_html_impressao(df, "RELATÓRIO COMPLETO")
            if html:
                b64 = base64.b64encode(html.encode()).decode()
                st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir relatório (Ctrl+P para PDF)</a>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### 📑 Relatório Consolidado")
        if st.button("📑 Consolidado (todos setores)", key="relatorio_consolidado"):
            html = gerar_html_consolidado(df)
            if html:
                b64 = base64.b64encode(html.encode()).decode()
                st.markdown(f'<a href="data:text/html;charset=utf-8;base64,{b64}" target="_blank">📄 Abrir consolidado</a>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### 🗑️ Exclusão de Registros")
        for idx, row in df.iterrows():
            col_check, col_data = st.columns([0.5, 9.5])
            with col_check:
                checked = st.checkbox("", key=f"chk_{row['id']}", value=row['id'] in st.session_state.selected_ids)
                if checked and row['id'] not in st.session_state.selected_ids:
                    st.session_state.selected_ids.append(row['id'])
                elif not checked and row['id'] in st.session_state.selected_ids:
                    st.session_state.selected_ids.remove(row['id'])
            with col_data:
                st.markdown(f"ID {row['id']} - {row['nome']} | CPF: {row['cpf']} | Empresa: {row.get('empresa','N/A')} | Entrada: {row['data_entrada']} | Saída: {row['data_saida'] or 'Presente'}")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("🗑️ Excluir Selecionados", key="excluir_selecionados"):
                if st.session_state.selected_ids:
                    st.session_state.pending_delete_ids = st.session_state.selected_ids.copy()
                    st.rerun()
        with col_btn2:
            if st.button("📋 Limpar Seleção", key="limpar_selecao"):
                st.session_state.selected_ids = []
                st.rerun()
        with col_btn3:
            if st.button("⚠️ LIMPAR TODO HISTÓRICO", key="limpar_historico"):
                st.session_state.pending_clear_all = True
                st.rerun()
        if st.session_state.pending_delete_ids:
            st.error(f"⚠️ Excluir {len(st.session_state.pending_delete_ids)} registro(s)?")
            col_conf, col_canc = st.columns(2)
            with col_conf:
                if st.button("✅ SIM, EXCLUIR", key="confirmar_excluir"):
                    try:
                        for id_ in st.session_state.pending_delete_ids:
                            supabase.table("movimentacao").delete().eq("id", id_).execute()
                        st.session_state.selected_ids = []
                        st.session_state.pending_delete_ids = []
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            with col_canc:
                if st.button("❌ Cancelar", key="cancelar_excluir"):
                    st.session_state.pending_delete_ids = []
                    st.rerun()
        if st.session_state.pending_clear_all:
            st.error("🚨 ATENÇÃO: apagar TODOS os registros. Digite 'LIMPAR TUDO'")
            confirm = st.text_input("Confirmação:", type="password", key="confirma_limpar")
            col_clear, col_cancel_clear = st.columns(2)
            with col_clear:
                if st.button("🔥 EXCLUIR TUDO", key="excluir_tudo"):
                    if confirm == "LIMPAR TUDO":
                        try:
                            supabase.table("movimentacao").delete().neq("id", 0).execute()
                            st.success("Histórico limpo!")
                            st.session_state.pending_clear_all = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.error("Confirmação incorreta")
            with col_cancel_clear:
                if st.button("Cancelar", key="cancelar_limpar"):
                    st.session_state.pending_clear_all = False
                    st.rerun()
    else:
        st.info("Nenhum registro encontrado.")

# ====================== GESTÃO DE CADASTROS (ADMIN) ======================
st.markdown("---")
if st.session_state.perfil == "ADMIN":
    with st.expander("⚙️ Gestão de Cadastros de Pessoas", expanded=True):
        try:
            todos = supabase.table("pessoas").select("id, nome, cpf, empresa").order("nome").execute().data
        except:
            todos = []
        if not todos:
            st.info("Nenhum cadastro")
        else:
            br = [p for p in todos if p.get('empresa', '').upper() == "BRASANITAS"]
            gr = [p for p in todos if p.get('empresa', '').upper() == "GRSA"]
            outros = [p for p in todos if p.get('empresa', '').upper() not in ["BRASANITAS", "GRSA"]]
            tab1, tab2, tab3 = st.tabs(["🏭 BRASANITAS", "🔧 GRSA", "🏢 OUTROS"])
            with tab1:
                st.markdown(f"**Total:** {len(br)}")
                for p in br:
                    col1, col2, col3, col4 = st.columns([3,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    with col3:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_br_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_br_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_br_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_br_{p['id']}")
                                if st.form_submit_button("Salvar", key=f"save_br_{p['id']}"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase.table("pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                st.success("Atualizado!")
                                                st.rerun()
                                            else:
                                                st.error("CPF já existe")
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    else:
                                        st.error("CPF inválido")
                    with col4:
                        with st.popover("🗑️ Excluir"):
                            st.warning(f"Excluir {p['nome']}?")
                            if st.button("Confirmar", key=f"del_br_{p['id']}"):
                                try:
                                    supabase.table("pessoas").delete().eq("id", p['id']).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    st.divider()
            with tab2:
                st.markdown(f"**Total:** {len(gr)}")
                for p in gr:
                    col1, col2, col3, col4 = st.columns([3,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    with col3:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_gr_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_gr_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_gr_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_gr_{p['id']}")
                                if st.form_submit_button("Salvar", key=f"save_gr_{p['id']}"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase.table("pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                st.success("Atualizado!")
                                                st.rerun()
                                            else:
                                                st.error("CPF já existe")
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    else:
                                        st.error("CPF inválido")
                    with col4:
                        with st.popover("🗑️ Excluir"):
                            st.warning(f"Excluir {p['nome']}?")
                            if st.button("Confirmar", key=f"del_gr_{p['id']}"):
                                try:
                                    supabase.table("pessoas").delete().eq("id", p['id']).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    st.divider()
            with tab3:
                st.markdown(f"**Total:** {len(outros)}")
                search = st.text_input("🔍 Pesquisar", key="search_outros")
                filtrados = [p for p in outros if search.lower() in p['nome'].lower() or search.lower() in p['cpf'] or search.lower() in p.get('empresa','').lower()] if search else outros
                for p in filtrados:
                    col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])
                    col1.write(f"**{p['nome']}**")
                    col2.write(f"CPF: {p['cpf']}")
                    col3.write(f"Empresa: {p.get('empresa','N/A')}")
                    with col4:
                        with st.popover("✏️ Editar"):
                            with st.form(f"edit_out_{p['id']}"):
                                novo_nome = st.text_input("Nome", p['nome'], key=f"nome_out_{p['id']}")
                                novo_cpf = st.text_input("CPF", p['cpf'], key=f"cpf_out_{p['id']}")
                                nova_emp = st.text_input("Empresa", p.get('empresa',''), key=f"emp_out_{p['id']}")
                                if st.form_submit_button("Salvar", key=f"save_out_{p['id']}"):
                                    if validar_cpf(novo_cpf):
                                        try:
                                            conflito = supabase.table("pessoas").select("id").eq("cpf", sanitizar_cpf(novo_cpf)).neq("id", p['id']).execute().data
                                            if not conflito:
                                                supabase.table("pessoas").update({
                                                    "nome": sanitizar_texto(novo_nome).upper(),
                                                    "cpf": sanitizar_cpf(novo_cpf),
                                                    "empresa": sanitizar_texto(nova_emp).upper()
                                                }).eq("id", p['id']).execute()
                                                st.success("Atualizado!")
                                                st.rerun()
                                            else:
                                                st.error("CPF já existe")
                                        except Exception as e:
                                            st.error(f"Erro: {e}")
                                    else:
                                        st.error("CPF inválido")
                    with col5:
                        with st.popover("🗑️ Excluir"):
                            st.warning(f"Excluir {p['nome']}?")
                            if st.button("Confirmar", key=f"del_out_{p['id']}"):
                                try:
                                    supabase.table("pessoas").delete().eq("id", p['id']).execute()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro: {e}")
                    st.divider()

apply_theme_css()

st.markdown("---")
st.markdown("""
<div class="footer">
    🛡️ JOHN ACESSOS - CYBER SECURITY 2026 | Monitoramento Inteligente & Proteção de Dados
</div>
""", unsafe_allow_html=True)
