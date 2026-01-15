"""
Professional Hubs - Legal Practice Management
Main Streamlit Application

A modern, professional UI for Puerto Rico law firms.
"""

import streamlit as st
from utils.api_client import api_client

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Professional Hubs",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS FOR PROFESSIONAL APPEARANCE
# ============================================================================

st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Card styling */
    .feature-card {
        background: linear-gradient(145deg, #1a1f2e 0%, #252b3d 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 16px;
        padding: 1.75rem;
        height: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .feature-card:hover {
        border-color: rgba(102, 126, 234, 0.5);
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
    }
    
    .feature-card h3 {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }
    
    .feature-card p {
        color: #a0aec0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    /* Stats styling */
    .stat-card {
        background: linear-gradient(145deg, #1e2433 0%, #262d3d 100%);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .stat-label {
        color: #a0aec0;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-online {
        background: rgba(72, 187, 120, 0.15);
        color: #48bb78;
        border: 1px solid rgba(72, 187, 120, 0.3);
    }
    
    .status-offline {
        background: rgba(245, 101, 101, 0.15);
        color: #f56565;
        border: 1px solid rgba(245, 101, 101, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Button overrides */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h2 style="color: #667eea; margin: 0;">⚖️ Professional Hubs</h2>
        <p style="color: #718096; font-size: 0.85rem; margin-top: 0.5rem;">
            Legal Practice Management
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # API Status Check
    health = api_client.health_check()
    if health["status"] == "healthy":
        st.markdown("""
        <div style="text-align: center;">
            <span class="status-badge status-online">🟢 Sistema Activo</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align: center;">
            <span class="status-badge status-offline">🔴 Sistema Desconectado</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # Navigation info
    st.markdown("""
    <div style="padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px; margin-top: 1rem;">
        <p style="color: #a0aec0; font-size: 0.85rem; margin: 0;">
            <strong style="color: #667eea;">Navegación</strong><br><br>
            Use el menú de páginas arriba para acceder a:<br><br>
            📋 <strong>Verificar Conflictos</strong><br>
            👥 <strong>Gestión de Clientes</strong><br>
            📁 <strong>Gestión de Asuntos</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding-top: 1rem;">
        <p style="color: #4a5568; font-size: 0.75rem;">
            Versión 1.0.0<br>
            © 2025 Professional Hubs
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.markdown("""
<div class="main-header">
    <h1>⚖️ Professional Hubs</h1>
    <p>Sistema de Gestión de Práctica Legal para Bufetes de Puerto Rico</p>
</div>
""", unsafe_allow_html=True)

# Welcome message
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h2 style="color: #e2e8f0; font-weight: 600;">Bienvenido a Professional Hubs</h2>
    <p style="color: #a0aec0; font-size: 1.05rem; line-height: 1.7;">
        La plataforma integral para la administración de su bufete. Verifique conflictos de interés, 
        gestione clientes y asuntos, todo desde una interfaz moderna y fácil de usar.
    </p>
</div>
""", unsafe_allow_html=True)

# Feature cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <h3>Verificación de Conflictos</h3>
        <p>
            Búsqueda inteligente con coincidencia difusa. Detecta conflictos de interés 
            comparando contra clientes existentes y partes relacionadas.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">👥</div>
        <h3>Gestión de Clientes</h3>
        <p>
            Administre su base de clientes con soporte completo para el formato de 
            nombres de Puerto Rico (nombre, apellido, segundo apellido).
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📁</div>
        <h3>Control de Asuntos</h3>
        <p>
            Organice casos legales, asigne partes relacionadas y mantenga 
            un registro completo de cada asunto de su bufete.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Quick stats section
st.markdown("""
<h3 style="color: #e2e8f0; margin-bottom: 1.5rem;">📊 Resumen Rápido</h3>
""", unsafe_allow_html=True)

# Fetch stats from API
clientes_result = api_client.listar_clientes(limit=1000)
asuntos_result = api_client.listar_asuntos(limit=1000)
partes_result = api_client.listar_partes_relacionadas(limit=1000)

num_clientes = len(clientes_result.get("data", [])) if clientes_result.get("success") else 0
num_asuntos = len(asuntos_result.get("data", [])) if asuntos_result.get("success") else 0
num_partes = len(partes_result.get("data", [])) if partes_result.get("success") else 0

stat1, stat2, stat3, stat4 = st.columns(4)

with stat1:
    st.markdown(f"""
    <div class="stat-card">
        <p class="stat-number">{num_clientes}</p>
        <p class="stat-label">Clientes Activos</p>
    </div>
    """, unsafe_allow_html=True)

with stat2:
    st.markdown(f"""
    <div class="stat-card">
        <p class="stat-number">{num_asuntos}</p>
        <p class="stat-label">Asuntos Abiertos</p>
    </div>
    """, unsafe_allow_html=True)

with stat3:
    st.markdown(f"""
    <div class="stat-card">
        <p class="stat-number">{num_partes}</p>
        <p class="stat-label">Partes Relacionadas</p>
    </div>
    """, unsafe_allow_html=True)

with stat4:
    st.markdown(f"""
    <div class="stat-card">
        <p class="stat-number">✓</p>
        <p class="stat-label">Sistema Listo</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# Getting started section
st.markdown("""
<h3 style="color: #e2e8f0; margin-bottom: 1rem;">🚀 Comenzar</h3>
<p style="color: #a0aec0; margin-bottom: 1.5rem;">
    Seleccione una opción del menú lateral o use los botones abajo para comenzar.
</p>
""", unsafe_allow_html=True)

btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 1])

with btn_col1:
    if st.button("🔍 Verificar Conflicto", use_container_width=True):
        st.switch_page("pages/1_🔍_Verificar_Conflictos.py")

with btn_col2:
    if st.button("👥 Gestionar Clientes", use_container_width=True):
        st.switch_page("pages/2_👥_Clientes.py")

with btn_col3:
    if st.button("📁 Ver Asuntos", use_container_width=True):
        st.switch_page("pages/3_📁_Asuntos.py")