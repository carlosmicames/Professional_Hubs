"""
Lexos - Legal Practice Management
Main Streamlit Application

A modern, professional UI for Puerto Rico law firms.
NO EMOJIS - Uses SVG icons and Bootstrap icons only.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.api_client import api_client

# ============================================================================
# CONSTANTS
# ============================================================================

THEME_OCEAN_BLUE = "#0077B6"
THEME_OCEAN_BLUE_LIGHT = "#00A8E8"
THEME_OCEAN_BLUE_DARK = "#005f8a"

# SVG Icons (inline for sidebar and UI elements)
ICONS = {
    "dashboard": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M0 1.5A1.5 1.5 0 0 1 1.5 0h2A1.5 1.5 0 0 1 5 1.5v2A1.5 1.5 0 0 1 3.5 5h-2A1.5 1.5 0 0 1 0 3.5v-2zM1.5 1a.5.5 0 0 0-.5.5v2a.5.5 0 0 0 .5.5h2a.5.5 0 0 0 .5-.5v-2a.5.5 0 0 0-.5-.5h-2zM0 8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V8zm1 3v2a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2H1zm14-1V8a1 1 0 0 0-1-1H2a1 1 0 0 0-1 1v2h14zM2 8.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0 4a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 0 1h-6a.5.5 0 0 1-.5-.5z"/></svg>',
    "clients": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816zM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275zM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/></svg>',
    "cases": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M9.828 3h3.982a2 2 0 0 1 1.992 2.181l-.637 7A2 2 0 0 1 13.174 14H2.825a2 2 0 0 1-1.991-1.819l-.637-7a1.99 1.99 0 0 1 .342-1.31L.5 3a2 2 0 0 1 2-2h3.672a2 2 0 0 1 1.414.586l.828.828A2 2 0 0 0 9.828 3zm-8.322.12C1.72 3.042 1.95 3 2.19 3h5.396l-.707-.707A1 1 0 0 0 6.172 2H2.5a1 1 0 0 0-1 .981l.006.139z"/></svg>',
    "agenda": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/></svg>',
    "calls": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M1.885.511a1.745 1.745 0 0 1 2.61.163L6.29 2.98c.329.423.445.974.315 1.494l-.547 2.19a.678.678 0 0 0 .178.643l2.457 2.457a.678.678 0 0 0 .644.178l2.189-.547a1.745 1.745 0 0 1 1.494.315l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.634 18.634 0 0 1-7.01-4.42 18.634 18.634 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877L1.885.511z"/></svg>',
    "invoices": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M4 10.781c.148 1.667 1.513 2.85 3.591 3.003V15h1.043v-1.216c2.27-.179 3.678-1.438 3.678-3.3 0-1.59-.947-2.51-2.956-3.028l-.722-.187V3.467c1.122.11 1.879.714 2.07 1.616h1.47c-.166-1.6-1.54-2.748-3.54-2.875V1H7.591v1.233c-1.939.23-3.27 1.472-3.27 3.156 0 1.454.966 2.483 2.661 2.917l.61.162v4.031c-1.149-.17-1.94-.8-2.131-1.718H4zm3.391-3.836c-1.043-.263-1.6-.825-1.6-1.616 0-.944.704-1.641 1.8-1.828v3.495l-.2-.05zm1.591 1.872c1.287.323 1.852.859 1.852 1.769 0 1.097-.826 1.828-2.2 1.939V8.73l.348.086z"/></svg>',
    "google": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 48 48"><path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/><path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/><path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/><path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/></svg>',
    "check": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg>',
    "warning": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/></svg>',
    "plus": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/></svg>',
    "share": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M11 2.5a2.5 2.5 0 1 1 .603 1.628l-6.718 3.12a2.499 2.499 0 0 1 0 1.504l6.718 3.12a2.5 2.5 0 1 1-.488.876l-6.718-3.12a2.5 2.5 0 1 1 0-3.256l6.718-3.12A2.5 2.5 0 0 1 11 2.5z"/></svg>',
    "gear": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/><path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115l.094-.319z"/></svg>',
    "arrow_left": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8z"/></svg>',
    "arrow_right": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8z"/></svg>',
    "scale": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M8 0a.5.5 0 0 1 .5.5v.12c.86.02 1.67.15 2.37.37l.15-.14a.5.5 0 0 1 .7.7l-.12.13c.84.46 1.42 1.1 1.7 1.85l.2-.04a.5.5 0 0 1 .16.98l-.17.03c.05.2.07.4.07.6 0 1.74-1.4 3.26-3.45 4.04l1.02 1.27A.5.5 0 0 1 10.74 11H8.5v3.5a.5.5 0 0 1-1 0V11H5.26a.5.5 0 0 1-.39-.81l1.02-1.27C3.85 8.1 2.45 6.58 2.45 4.84c0-.2.02-.4.07-.6l-.17-.03a.5.5 0 0 1 .16-.98l.2.04c.28-.75.86-1.39 1.7-1.85l-.12-.13a.5.5 0 1 1 .7-.7l.15.14c.7-.22 1.51-.35 2.37-.37V.5A.5.5 0 0 1 8 0zm0 1.62c-2.64 0-4.55 1.5-4.55 3.22s1.91 3.22 4.55 3.22 4.55-1.5 4.55-3.22-1.91-3.22-4.55-3.22z"/></svg>',
}

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Lexos",
    page_icon="data:image/svg+xml," + ICONS["scale"].replace("#", "%23"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

if "clientes_page_index" not in st.session_state:
    st.session_state.clientes_page_index = 0

if "casos_page_index" not in st.session_state:
    st.session_state.casos_page_index = 0

if "casos_page_size" not in st.session_state:
    st.session_state.casos_page_size = 10

if "agenda_view" not in st.session_state:
    st.session_state.agenda_view = "Mes"

if "clientes_tab" not in st.session_state:
    st.session_state.clientes_tab = "Mis Clientes"

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown(f"""
<style>
    /* Main container */
    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }}

    /* Header styling */
    .main-header {{
        background: linear-gradient(135deg, {THEME_OCEAN_BLUE} 0%, {THEME_OCEAN_BLUE_DARK} 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 119, 182, 0.3);
    }}

    .main-header h1 {{
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }}

    /* Card styling */
    .stat-card {{
        background: linear-gradient(145deg, #1e2433 0%, #262d3d 100%);
        border: 1px solid rgba(0, 119, 182, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        height: 100%;
    }}

    .stat-card h3 {{
        color: {THEME_OCEAN_BLUE};
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}

    .stat-card .stat-number {{
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin: 0.5rem 0;
    }}

    .stat-card .stat-label {{
        color: #a0aec0;
        font-size: 0.85rem;
    }}

    .info-card {{
        background: linear-gradient(145deg, #1a1f2e 0%, #252b3d 100%);
        border: 1px solid rgba(0, 119, 182, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }}

    .info-card h4 {{
        color: {THEME_OCEAN_BLUE};
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }}

    .info-card p {{
        color: #a0aec0;
        font-size: 0.9rem;
        margin: 0;
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0e1117 0%, #1a1f2e 100%);
    }}

    .sidebar-nav-item {{
        display: flex;
        align-items: center;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.25rem;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #a0aec0;
    }}

    .sidebar-nav-item:hover {{
        background: rgba(0, 119, 182, 0.15);
        color: white;
    }}

    .sidebar-nav-item.active {{
        background: rgba(0, 119, 182, 0.2);
        color: {THEME_OCEAN_BLUE};
        border-left: 3px solid {THEME_OCEAN_BLUE};
    }}

    .sidebar-nav-item svg {{
        margin-right: 0.75rem;
        width: 18px;
        height: 18px;
    }}

    /* Button styling */
    .ocean-btn {{
        background: linear-gradient(135deg, {THEME_OCEAN_BLUE} 0%, {THEME_OCEAN_BLUE_DARK} 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.25rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
    }}

    .ocean-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 119, 182, 0.4);
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {THEME_OCEAN_BLUE} 0%, {THEME_OCEAN_BLUE_DARK} 100%);
        color: white;
        border: none;
    }}

    .stButton > button:hover {{
        background: linear-gradient(135deg, {THEME_OCEAN_BLUE_LIGHT} 0%, {THEME_OCEAN_BLUE} 100%);
        color: white;
    }}

    /* Status badges */
    .status-badge {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 500;
    }}

    .status-online {{
        background: rgba(72, 187, 120, 0.15);
        color: #48bb78;
        border: 1px solid rgba(72, 187, 120, 0.3);
    }}

    .status-offline {{
        background: rgba(245, 101, 101, 0.15);
        color: #f56565;
        border: 1px solid rgba(245, 101, 101, 0.3);
    }}

    /* Divider */
    .custom-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 119, 182, 0.3), transparent);
        margin: 1.5rem 0;
    }}

    /* Calendar grid */
    .calendar-grid {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
        background: #1a1f2e;
        border-radius: 8px;
        overflow: hidden;
    }}

    .calendar-header {{
        background: {THEME_OCEAN_BLUE};
        color: white;
        padding: 0.5rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.85rem;
    }}

    .calendar-day {{
        background: #252b3d;
        padding: 0.5rem;
        min-height: 60px;
        text-align: center;
        color: #a0aec0;
        font-size: 0.85rem;
    }}

    .calendar-day.today {{
        background: rgba(0, 119, 182, 0.2);
        color: {THEME_OCEAN_BLUE};
        font-weight: 600;
    }}

    .calendar-day.other-month {{
        color: #4a5568;
    }}

    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        color: #a0aec0;
    }}

    .stTabs [aria-selected="true"] {{
        background: rgba(0, 119, 182, 0.2);
        color: {THEME_OCEAN_BLUE};
    }}

    /* Form styling */
    .stTextInput > div > div > input {{
        background: #1a1f2e;
        border: 1px solid rgba(0, 119, 182, 0.3);
        color: white;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: {THEME_OCEAN_BLUE};
        box-shadow: 0 0 0 1px {THEME_OCEAN_BLUE};
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

def render_sidebar():
    with st.sidebar:
        # Logo/Brand
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                <span style="color: {THEME_OCEAN_BLUE};">{ICONS["scale"]}</span>
                <h2 style="color: {THEME_OCEAN_BLUE}; margin: 0; font-size: 1.5rem;">Lexos</h2>
            </div>
            <p style="color: #718096; font-size: 0.8rem; margin-top: 0.5rem;">
                Legal Practice Management
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # API Status
        health = api_client.health_check()
        if health["status"] == "healthy":
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <span class="status-badge status-online">Sistema Activo</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <span class="status-badge status-offline">Sistema Desconectado</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Navigation
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Clientes", "clients"),
            ("Mis Casos", "cases"),
            ("Agenda", "agenda"),
            ("Llamadas", "calls"),
            ("Facturas", "invoices"),
        ]

        for item_name, icon_key in nav_items:
            is_active = st.session_state.current_page == item_name
            active_class = "active" if is_active else ""

            if st.button(
                f"{item_name}",
                key=f"nav_{item_name}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_page = item_name
                st.rerun()

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Version
        st.markdown("""
        <div style="text-align: center; padding-top: 1rem;">
            <p style="color: #4a5568; font-size: 0.75rem;">
                Version 1.0.0<br>
                2025 Lexos
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

def render_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)

    # Citas del Dia section
    st.markdown("""
    <div class="info-card">
        <h4>Citas del Dia</h4>
        <p>No hay citas programadas para hoy</p>
    </div>
    """, unsafe_allow_html=True)

    # First row of stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>Total Casos</h3>
            <p class="stat-number">0</p>
            <p class="stat-label">casos activos en el sistema</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>Citas Hoy</h3>
            <p class="stat-number">0</p>
            <p class="stat-label">reuniones programadas.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>Video Llamadas</h3>
            <p class="stat-number">0</p>
            <p class="stat-label">0 min grabados</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Second row of stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>Distribucion de Casos por Tipo</h4>
            <p>No hay datos de caso disponibles</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>Resumen de Casos por Tipo</h4>
            <p>No hay datos de casos disponibles.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h4>Almacenamiento</h4>
            <p style="font-size: 1.5rem; color: white; margin-bottom: 0.5rem;">0 MB / 99MB</p>
            <p style="color: #718096;">Plan Basico</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# PAGE: CLIENTES
# ============================================================================

def render_clientes():
    st.markdown("""
    <div class="main-header">
        <h1>Clientes</h1>
    </div>
    """, unsafe_allow_html=True)

    # Tab selector using selectbox (to default to "Mis Clientes")
    tab_options = ["Empresa", "Perfil", "Estudios", "Areas de Derecho", "Gestion Geografico", "Planes", "Mis Clientes"]

    # Default to "Mis Clientes"
    default_index = tab_options.index(st.session_state.clientes_tab)

    selected_tab = st.selectbox(
        "Seccion",
        tab_options,
        index=default_index,
        key="clientes_tab_selector",
        label_visibility="collapsed"
    )

    st.session_state.clientes_tab = selected_tab

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    if selected_tab == "Mis Clientes":
        render_mis_clientes()
    elif selected_tab == "Empresa":
        st.markdown("""
        <div class="info-card">
            <h4>Configuracion de Empresa</h4>
            <p>Configuracion de la empresa pendiente de implementacion.</p>
        </div>
        """, unsafe_allow_html=True)
    elif selected_tab == "Perfil":
        st.markdown("""
        <div class="info-card">
            <h4>Perfil de Usuario</h4>
            <p>Perfil de usuario pendiente de implementacion.</p>
        </div>
        """, unsafe_allow_html=True)
    elif selected_tab == "Estudios":
        st.markdown("""
        <div class="info-card">
            <h4>Estudios</h4>
            <p>Seccion de estudios pendiente de implementacion.</p>
        </div>
        """, unsafe_allow_html=True)
    elif selected_tab == "Areas de Derecho":
        st.markdown("""
        <div class="info-card">
            <h4>Areas de Derecho</h4>
            <p>Configuracion de areas de derecho pendiente de implementacion.</p>
        </div>
        """, unsafe_allow_html=True)
    elif selected_tab == "Gestion Geografico":
        st.markdown("""
        <div class="info-card">
            <h4>Gestion Geografico</h4>
            <p>Configuracion geografica pendiente de implementacion.</p>
        </div>
        """, unsafe_allow_html=True)
    elif selected_tab == "Planes":
        st.markdown("""
        <div class="info-card">
            <h4>Planes de Suscripcion</h4>
            <p>Gestion de planes pendiente de implementacion.</p>
        </div>
        """, unsafe_allow_html=True)

def render_mis_clientes():
    st.subheader("Lista de Clientes")

    # Fetch clients from API
    result = api_client.listar_clientes(limit=1000)

    if result.get("success") and result.get("data"):
        clients_data = result["data"]

        # Transform to DataFrame with required columns
        df_data = []
        for client in clients_data:
            df_data.append({
                "Nombre": client.get("nombre", ""),
                "Apellido": client.get("apellido", ""),
                "Empresa": client.get("nombre_empresa", ""),
                "Correo": client.get("email", ""),
                "Telefono": client.get("telefono", ""),
                "Direccion": client.get("direccion", ""),
                "Direccion Postal": client.get("direccion_postal", ""),
                "Fecha Creacion": client.get("creado_en", "")[:10] if client.get("creado_en") else "",
                "Acciones": "OK"  # Placeholder - shows clear status
            })

        df = pd.DataFrame(df_data)

        # Editable table
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Acciones": st.column_config.TextColumn(
                    "Acciones",
                    help="Estado de alertas del cliente",
                    disabled=True,
                )
            }
        )
    else:
        # Empty table structure
        df = pd.DataFrame(columns=[
            "Nombre", "Apellido", "Empresa", "Correo", "Telefono",
            "Direccion", "Direccion Postal", "Fecha Creacion", "Acciones"
        ])
        st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # New Client Form
    st.subheader("Nuevo Cliente.")

    with st.form("nuevo_cliente_form"):
        # Row 1: Email, Nombre
        col1, col2 = st.columns(2)
        with col1:
            email = st.text_input("Email*", key="new_client_email")
        with col2:
            nombre = st.text_input("Nombre*", key="new_client_nombre")

        # Row 2: Apellido, Empresa
        col1, col2 = st.columns(2)
        with col1:
            apellido = st.text_input("Apellido*", key="new_client_apellido")
        with col2:
            empresa = st.text_input("Empresa", key="new_client_empresa")

        # Row 3: Direccion, Direccion Postal
        col1, col2 = st.columns(2)
        with col1:
            direccion = st.text_input("Direccion*", key="new_client_direccion")
        with col2:
            direccion_postal = st.text_input("Direccion Postal", key="new_client_direccion_postal")

        # Row 4: Telefono, spacer
        col1, col2 = st.columns(2)
        with col1:
            telefono = st.text_input("Telefono*", key="new_client_telefono")
        with col2:
            st.empty()  # Spacer

        # Submit button (right-aligned via columns)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col3:
            submitted = st.form_submit_button("Crear Cliente", use_container_width=True)

        if submitted:
            if not email or not nombre or not apellido or not direccion or not telefono:
                st.error("Por favor complete todos los campos requeridos (*)")
            else:
                # Create client via API
                result = api_client.crear_cliente(
                    nombre=nombre,
                    apellido=apellido,
                    nombre_empresa=empresa if empresa else None
                )
                if result.get("success"):
                    st.success("Cliente creado exitosamente")
                    st.rerun()
                else:
                    st.error(f"Error al crear cliente: {result.get('error', 'Error desconocido')}")

# ============================================================================
# PAGE: MIS CASOS
# ============================================================================

def render_mis_casos():
    st.markdown("""
    <div class="main-header">
        <h1>Mis Casos</h1>
    </div>
    """, unsafe_allow_html=True)

    # Right-aligned "Crear Nuevo" button
    col1, col2, col3 = st.columns([4, 1, 1])
    with col3:
        if st.button("Crear Nuevo", use_container_width=True):
            st.session_state.show_new_case_form = True

    # Fetch cases from API
    result = api_client.listar_asuntos(limit=1000)

    cases_data = []
    if result.get("success") and result.get("data"):
        for caso in result["data"]:
            cases_data.append({
                "Nombre": caso.get("nombre_asunto", ""),
                "Areas de Derecho": caso.get("area_derecho", "General"),
                "Tipo de Caso": caso.get("tipo_caso", ""),
                "Colaboradores": caso.get("colaboradores", ""),
                "Fecha de Creacion": caso.get("creado_en", "")[:10] if caso.get("creado_en") else "",
                "Accion Requerido": caso.get("accion_requerida", "No")
            })

    df = pd.DataFrame(cases_data) if cases_data else pd.DataFrame(columns=[
        "Nombre", "Areas de Derecho", "Tipo de Caso", "Colaboradores",
        "Fecha de Creacion", "Accion Requerido"
    ])

    # Pagination controls
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])

    with col1:
        page_size = st.selectbox(
            "Filas por pagina",
            [5, 10, 25, 50, 100],
            index=[5, 10, 25, 50, 100].index(st.session_state.casos_page_size),
            key="casos_page_size_select",
            label_visibility="collapsed"
        )
        st.session_state.casos_page_size = page_size

    total_pages = max(1, (len(df) + page_size - 1) // page_size)
    start_idx = st.session_state.casos_page_index * page_size
    end_idx = min(start_idx + page_size, len(df))

    with col3:
        st.write(f"Mostrando {start_idx + 1}-{end_idx} de {len(df)}")

    with col2:
        prev_col, next_col = st.columns(2)
        with prev_col:
            if st.button("Anterior", disabled=st.session_state.casos_page_index == 0, key="casos_prev"):
                st.session_state.casos_page_index -= 1
                st.rerun()
        with next_col:
            if st.button("Siguiente", disabled=st.session_state.casos_page_index >= total_pages - 1, key="casos_next"):
                st.session_state.casos_page_index += 1
                st.rerun()

    # Display paginated table
    paginated_df = df.iloc[start_idx:end_idx] if len(df) > 0 else df

    st.data_editor(
        paginated_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed"
    )

# ============================================================================
# PAGE: AGENDA
# ============================================================================

def render_agenda():
    st.markdown("""
    <div class="main-header">
        <h1>Agenda</h1>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>Hoy</h3>
            <p class="stat-number">0</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>Esta Semana</h3>
            <p class="stat-number">0</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>Este mes</h3>
            <p class="stat-number">0</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="stat-card">
            <h3>Eventos Totales</h3>
            <p class="stat-number">0</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons (right-aligned)
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

    with col2:
        st.button("Conectar", use_container_width=True, help="Conectar con Google Calendar")
    with col3:
        st.button("+ Agregar Evento", use_container_width=True)
    with col4:
        st.button("Compartir Horario", use_container_width=True)
    with col5:
        st.button("Configurar Horario", use_container_width=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # View selector
    view_options = ["Mes", "Semana", "Dia", "Agenda"]
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 4])

    for i, view in enumerate(view_options):
        with [col1, col2, col3, col4][i]:
            if st.button(view, key=f"view_{view}", use_container_width=True,
                        type="primary" if st.session_state.agenda_view == view else "secondary"):
                st.session_state.agenda_view = view
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Calendar view based on selection
    if st.session_state.agenda_view == "Mes":
        render_month_calendar()
    elif st.session_state.agenda_view == "Semana":
        st.markdown("""
        <div class="info-card">
            <h4>Vista Semanal</h4>
            <p>No hay eventos programados para esta semana.</p>
        </div>
        """, unsafe_allow_html=True)
    elif st.session_state.agenda_view == "Dia":
        st.markdown("""
        <div class="info-card">
            <h4>Vista Diaria</h4>
            <p>No hay eventos programados para hoy.</p>
        </div>
        """, unsafe_allow_html=True)
    else:  # Agenda
        st.markdown("""
        <div class="info-card">
            <h4>Agenda</h4>
            <p>No hay eventos proximos.</p>
        </div>
        """, unsafe_allow_html=True)

def render_month_calendar():
    import calendar

    today = date.today()
    cal = calendar.Calendar(firstweekday=6)  # Sunday start

    # Month navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <h3 style="text-align: center; color: white;">
            {calendar.month_name[today.month]} {today.year}
        </h3>
        """, unsafe_allow_html=True)

    # Calendar header
    days_header = ["Dom", "Lun", "Mar", "Mie", "Jue", "Vie", "Sab"]

    # Build calendar HTML
    calendar_html = '<div class="calendar-grid">'

    # Header row
    for day in days_header:
        calendar_html += f'<div class="calendar-header">{day}</div>'

    # Calendar days
    month_days = cal.monthdayscalendar(today.year, today.month)

    for week in month_days:
        for day in week:
            if day == 0:
                calendar_html += '<div class="calendar-day other-month"></div>'
            elif day == today.day:
                calendar_html += f'<div class="calendar-day today">{day}</div>'
            else:
                calendar_html += f'<div class="calendar-day">{day}</div>'

    calendar_html += '</div>'

    st.markdown(calendar_html, unsafe_allow_html=True)

# ============================================================================
# PAGE: LLAMADAS
# ============================================================================

def render_llamadas():
    st.markdown("""
    <div class="main-header">
        <h1>Llamadas</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <h4>Centro de Llamadas</h4>
        <p>Funcionalidad de llamadas pendiente de implementacion.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PAGE: FACTURAS
# ============================================================================

def render_facturas():
    st.markdown("""
    <div class="main-header">
        <h1>Facturas</h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <h4>Gestion de Facturas</h4>
        <p>Funcionalidad de facturacion pendiente de implementacion.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APP ROUTING
# ============================================================================

def main():
    render_sidebar()

    page = st.session_state.current_page

    if page == "Dashboard":
        render_dashboard()
    elif page == "Clientes":
        render_clientes()
    elif page == "Mis Casos":
        render_mis_casos()
    elif page == "Agenda":
        render_agenda()
    elif page == "Llamadas":
        render_llamadas()
    elif page == "Facturas":
        render_facturas()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
