"""
Professional Hubs - Legal Practice Management Dashboard
Complete Streamlit Application for Puerto Rico Law Firms
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import json
import os
from typing import Dict, List, Optional
import sqlite3
from dataclasses import dataclass
import uuid
import calendar  # CRITICAL: Import at top level to avoid Streamlit Cloud timeout
import tempfile  # For safe database location

from auth import require_auth

# =============================================================================
# CONFIGURATION
# =============================================================================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
FIRM_ID = int(os.getenv("FIRM_ID", "1"))

# Page configuration
st.set_page_config(
    page_title="Professional Hubs - Legal Practice Management",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="expanded"
)

authenticated, name, username, authenticator = require_auth()

if not authenticated:
    st.stop()

# Show logout button in sidebar
with st.sidebar:
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Welcome *{name}*')

# =============================================================================
# COLOR SCHEME - Navy Blue and Light Gray
# =============================================================================
COLORS = {
    "navy_primary": "#1e3a5f",
    "navy_dark": "#0d2137",
    "navy_light": "#2c5282",
    "gray_light": "#f7fafc",
    "gray_medium": "#e2e8f0",
    "gray_dark": "#718096",
    "white": "#ffffff",
    "success": "#38a169",
    "warning": "#d69e2e",
    "danger": "#e53e3e",
    "info": "#3182ce"
}

# =============================================================================
# CUSTOM CSS - Navy Blue and Light Gray Theme (No Emojis)
# =============================================================================
st.markdown(f"""
    <style>
    /* Main container */
    .main {{
        background-color: {COLORS["gray_light"]};
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: {COLORS["navy_primary"]};
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {COLORS["white"]};
    }}
    
    /* Header styling */
    .header-container {{
        background: linear-gradient(135deg, {COLORS["navy_primary"]} 0%, {COLORS["navy_dark"]} 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        color: {COLORS["white"]};
    }}
    
    .header-title {{
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: {COLORS["white"]};
    }}
    
    .header-subtitle {{
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.25rem;
        color: {COLORS["gray_medium"]};
    }}
    
    /* Card styling */
    .metric-card {{
        background: {COLORS["white"]};
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid {COLORS["navy_primary"]};
    }}
    
    .metric-number {{
        font-size: 2.5rem;
        font-weight: 700;
        color: {COLORS["navy_primary"]};
    }}
    
    .metric-label {{
        color: {COLORS["gray_dark"]};
        font-size: 0.875rem;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Section headers */
    .section-header {{
        color: {COLORS["navy_primary"]};
        font-size: 1.25rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid {COLORS["navy_light"]};
    }}
    
    /* Alert boxes */
    .alert-success {{
        background-color: #c6f6d5;
        border-left: 4px solid {COLORS["success"]};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #22543d;
    }}
    
    .alert-warning {{
        background-color: #fefcbf;
        border-left: 4px solid {COLORS["warning"]};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #744210;
    }}
    
    .alert-danger {{
        background-color: #fed7d7;
        border-left: 4px solid {COLORS["danger"]};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #742a2a;
    }}
    
    .alert-info {{
        background-color: #bee3f8;
        border-left: 4px solid {COLORS["info"]};
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
        color: #2a4365;
    }}
    
    /* Notification card */
    .notification-card {{
        background: {COLORS["white"]};
        border: 1px solid {COLORS["gray_medium"]};
        border-left: 4px solid {COLORS["warning"]};
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 0.75rem;
    }}
    
    .notification-title {{
        font-weight: 600;
        color: {COLORS["navy_primary"]};
        margin-bottom: 0.5rem;
    }}
    
    .notification-detail {{
        font-size: 0.875rem;
        color: {COLORS["gray_dark"]};
    }}
    
    /* COI conflict badge */
    .conflict-badge {{
        background-color: {COLORS["danger"]};
        color: {COLORS["white"]};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
    }}
    
    .no-conflict-badge {{
        background-color: {COLORS["success"]};
        color: {COLORS["white"]};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
    }}
    
    /* Calendar styling */
    .calendar-container {{
        background: {COLORS["white"]};
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    
    .calendar-header {{
        background: {COLORS["navy_primary"]};
        color: {COLORS["white"]};
        padding: 0.75rem;
        text-align: center;
        border-radius: 4px 4px 0 0;
        font-weight: 600;
    }}
    
    /* Table styling */
    .dataframe {{
        font-size: 0.9rem;
    }}
    
    /* Button styling */
    .stButton>button {{
        background-color: {COLORS["navy_primary"]};
        color: {COLORS["white"]};
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }}
    
    .stButton>button:hover {{
        background-color: {COLORS["navy_dark"]};
    }}
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS["gray_medium"]};
        color: {COLORS["navy_primary"]};
        border-radius: 4px 4px 0 0;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS["navy_primary"]};
        color: {COLORS["white"]};
    }}
    
    /* Form styling */
    .stTextInput>div>div>input {{
        border: 1px solid {COLORS["gray_medium"]};
        border-radius: 4px;
    }}
    
    .stSelectbox>div>div {{
        border: 1px solid {COLORS["gray_medium"]};
        border-radius: 4px;
    }}
    
    /* Video call container */
    .video-container {{
        background: {COLORS["navy_dark"]};
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    
    .video-placeholder {{
        color: {COLORS["white"]};
        font-size: 1.25rem;
    }}
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# DATABASE INITIALIZATION (SQLite for local storage)
# =============================================================================
def get_db_path():
    """Get safe database path for Streamlit Cloud"""
    # Use temp directory for Streamlit Cloud compatibility
    if os.path.exists('/mount/src'):  # Streamlit Cloud
        db_dir = '/tmp'
    else:  # Local development
        db_dir = '.'
    return os.path.join(db_dir, 'professional_hubs.db')

def init_database():
    """Initialize SQLite database for local data storage"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    
    # Clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            segundo_apellido TEXT,
            empresa TEXT,
            direccion TEXT NOT NULL,
            direccion_postal TEXT,
            telefono TEXT NOT NULL,
            has_conflict INTEGER DEFAULT 0,
            conflict_details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cases table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            opposing_party TEXT,
            legal_area TEXT NOT NULL,
            case_type TEXT NOT NULL,
            collaborating_attorneys TEXT,
            opening_date DATE NOT NULL,
            status TEXT DEFAULT 'Activo',
            has_conflict INTEGER DEFAULT 0,
            conflict_details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')
    
    # Calendar events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date DATE NOT NULL,
            event_time TIME,
            event_type TEXT DEFAULT 'meeting',
            description TEXT,
            case_id INTEGER,
            client_id INTEGER,
            outlook_synced INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # AI Call Agent notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intake_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caller_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            case_type TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            reviewed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Video calls table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            scheduled_date DATE NOT NULL,
            scheduled_time TIME NOT NULL,
            duration_minutes INTEGER DEFAULT 30,
            participant_name TEXT,
            participant_email TEXT,
            case_id INTEGER,
            room_id TEXT,
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Forms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_name TEXT NOT NULL,
            form_type TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            case_id INTEGER,
            invoice_number TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            due_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        )
    ''')
    
    conn.commit()
    return conn

# Initialize database
conn = init_database()

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "My Office"
    
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
    
if 'intake_notifications' not in st.session_state:
    # Sample intake notifications for demo
    st.session_state.intake_notifications = [
        {
            "id": 1,
            "caller_name": "Maria Rodriguez",
            "phone": "(787) 555-0123",
            "email": "maria.rodriguez@email.com",
            "case_type": "Familia",
            "description": "Consulta sobre proceso de divorcio y custodia de menores.",
            "status": "pending",
            "created_at": datetime.now() - timedelta(hours=2)
        },
        {
            "id": 2,
            "caller_name": "Carlos Mendez",
            "phone": "(787) 555-0456",
            "email": "carlos.mendez@email.com",
            "case_type": "Civil",
            "description": "Disputa contractual con proveedor de servicios.",
            "status": "pending",
            "created_at": datetime.now() - timedelta(hours=5)
        }
    ]

if 'video_call_active' not in st.session_state:
    st.session_state.video_call_active = False

# =============================================================================
# PUERTO RICO LEGAL AREAS AND CASE TYPES
# =============================================================================
LEGAL_AREAS = [
    "Civil",
    "Criminal",
    "Familia",
    "Laboral",
    "Corporativo",
    "Bienes Raices",
    "Inmigracion",
    "Quiebras",
    "Propiedad Intelectual",
    "Administrativo",
    "Ambiental",
    "Tributario"
]

CASE_TYPES = {
    "Civil": ["Danos y Perjuicios", "Cobro de Dinero", "Incumplimiento de Contrato", "Desahucio", "Interdicto", "Declaratoria de Herederos"],
    "Criminal": ["Delito Grave", "Delito Menos Grave", "Ley 54", "Drogas", "Violencia Domestica", "Fraude"],
    "Familia": ["Divorcio", "Custodia", "Pension Alimentaria", "Adopcion", "Tutela", "Patria Potestad"],
    "Laboral": ["Despido Injustificado", "Discriminacion", "Acoso Laboral", "Reclamacion Salarial", "CFSE"],
    "Corporativo": ["Incorporacion", "Fusiones y Adquisiciones", "Contratos Comerciales", "Cumplimiento Regulatorio"],
    "Bienes Raices": ["Compraventa", "Hipoteca", "Titulo", "Deslinde", "Servidumbre", "Expropiacion"],
    "Inmigracion": ["Visa de Trabajo", "Residencia Permanente", "Naturalizacion", "Deportacion", "Asilo"],
    "Quiebras": ["Capitulo 7", "Capitulo 11", "Capitulo 13", "Reestructuracion de Deuda"],
    "Propiedad Intelectual": ["Patentes", "Marcas", "Derechos de Autor", "Secretos Comerciales"],
    "Administrativo": ["Permisos", "Licencias", "Apelaciones Administrativas", "CRIM"],
    "Ambiental": ["Permisos Ambientales", "Cumplimiento EPA", "JCA", "Remediacion"],
    "Tributario": ["Hacienda PR", "IRS", "Planificacion Tributaria", "Auditorias"]
}

# =============================================================================
# COI (CONFLICT OF INTEREST) CHECK FUNCTIONS
# =============================================================================
def check_coi_api(nombre: str, apellido: str, segundo_apellido: str = None, nombre_empresa: str = None) -> Dict:
    """Check for conflicts of interest via the existing API (with offline mode support)"""
    try:
        headers = {
            "X-Firm-ID": str(FIRM_ID),
            "Content-Type": "application/json"
        }

        payload = {}
        if nombre:
            payload["nombre"] = nombre
        if apellido:
            payload["apellido"] = apellido
        if segundo_apellido:
            payload["segundo_apellido"] = segundo_apellido
        if nombre_empresa:
            payload["nombre_empresa"] = nombre_empresa

        response = requests.post(
            f"{API_BASE_URL}/api/v1/conflictos/verificar",
            headers=headers,
            json=payload,
            timeout=5  # Reduced timeout for faster failover
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"total_conflictos": 0, "conflictos": [], "error": f"API Error: {response.status_code}", "offline": False}

    except requests.exceptions.ConnectionError:
        # Graceful degradation - API not available (offline mode)
        return {"total_conflictos": 0, "conflictos": [], "error": "Modo sin conexion - solo busqueda local", "offline": True}
    except requests.exceptions.Timeout:
        return {"total_conflictos": 0, "conflictos": [], "error": "API timeout - solo busqueda local", "offline": True}
    except Exception as e:
        return {"total_conflictos": 0, "conflictos": [], "error": f"Error: {str(e)}", "offline": True}

def check_coi_local(nombre: str, apellido: str, opposing_party: str = None) -> Dict:
    """Check for conflicts against local client database"""
    cursor = conn.cursor()
    conflicts = []
    
    # Check against existing clients
    cursor.execute('''
        SELECT id, nombre, apellido, segundo_apellido, empresa 
        FROM clients 
        WHERE LOWER(nombre) LIKE ? OR LOWER(apellido) LIKE ? OR LOWER(empresa) LIKE ?
    ''', (f'%{nombre.lower()}%', f'%{apellido.lower()}%', f'%{nombre.lower()}%'))
    
    client_matches = cursor.fetchall()
    for match in client_matches:
        conflicts.append({
            "type": "client",
            "id": match[0],
            "name": f"{match[1]} {match[2]} {match[3] or ''}".strip(),
            "empresa": match[4],
            "confidence": "alta"
        })
    
    # Check against opposing parties in cases
    if opposing_party:
        cursor.execute('''
            SELECT id, opposing_party, client_name, case_type 
            FROM cases 
            WHERE LOWER(opposing_party) LIKE ? OR LOWER(client_name) LIKE ?
        ''', (f'%{opposing_party.lower()}%', f'%{opposing_party.lower()}%'))
        
        case_matches = cursor.fetchall()
        for match in case_matches:
            conflicts.append({
                "type": "opposing_party",
                "case_id": match[0],
                "opposing_party": match[1],
                "client_name": match[2],
                "case_type": match[3],
                "confidence": "alta"
            })
    
    return {
        "total_conflictos": len(conflicts),
        "conflictos": conflicts,
        "checked_name": f"{nombre} {apellido}"
    }

# =============================================================================
# DATABASE HELPER FUNCTIONS
# =============================================================================
def get_all_clients():
    """Get all clients from database"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients ORDER BY created_at DESC')
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_all_cases():
    """Get all cases from database"""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cases ORDER BY created_at DESC')
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_active_cases_count():
    """Get count of active cases"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'Activo'")
    return cursor.fetchone()[0]

def get_today_meetings():
    """Get today's meetings"""
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute('SELECT * FROM calendar_events WHERE event_date = ?', (today,))
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_today_video_calls():
    """Get today's video calls"""
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("SELECT * FROM video_calls WHERE scheduled_date = ? AND status = 'scheduled'", (today,))
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_calendar_events(month: int, year: int):
    """Get calendar events for a specific month"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM calendar_events 
        WHERE strftime('%m', event_date) = ? AND strftime('%Y', event_date) = ?
        ORDER BY event_date, event_time
    ''', (f'{month:02d}', str(year)))
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def add_client(client_data: Dict) -> int:
    """Add a new client and return the ID"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clients (email, nombre, apellido, segundo_apellido, empresa, direccion, direccion_postal, telefono, has_conflict, conflict_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        client_data['email'],
        client_data['nombre'],
        client_data['apellido'],
        client_data.get('segundo_apellido', ''),
        client_data.get('empresa', ''),
        client_data['direccion'],
        client_data.get('direccion_postal', ''),
        client_data['telefono'],
        client_data.get('has_conflict', 0),
        client_data.get('conflict_details', '')
    ))
    conn.commit()
    return cursor.lastrowid

def add_case(case_data: Dict) -> int:
    """Add a new case and return the ID"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cases (client_id, client_name, opposing_party, legal_area, case_type, collaborating_attorneys, opening_date, status, has_conflict, conflict_details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        case_data['client_id'],
        case_data['client_name'],
        case_data.get('opposing_party', ''),
        case_data['legal_area'],
        case_data['case_type'],
        case_data.get('collaborating_attorneys', ''),
        case_data['opening_date'],
        case_data.get('status', 'Activo'),
        case_data.get('has_conflict', 0),
        case_data.get('conflict_details', '')
    ))
    conn.commit()
    return cursor.lastrowid

def add_calendar_event(event_data: Dict) -> int:
    """Add a new calendar event"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO calendar_events (title, event_date, event_time, event_type, description, case_id, client_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        event_data['title'],
        event_data['event_date'],
        event_data.get('event_time', ''),
        event_data.get('event_type', 'meeting'),
        event_data.get('description', ''),
        event_data.get('case_id'),
        event_data.get('client_id')
    ))
    conn.commit()
    return cursor.lastrowid

def add_video_call(call_data: Dict) -> int:
    """Add a new video call"""
    cursor = conn.cursor()
    room_id = str(uuid.uuid4())[:8]
    cursor.execute('''
        INSERT INTO video_calls (title, scheduled_date, scheduled_time, duration_minutes, participant_name, participant_email, case_id, room_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        call_data['title'],
        call_data['scheduled_date'],
        call_data['scheduled_time'],
        call_data.get('duration_minutes', 30),
        call_data.get('participant_name', ''),
        call_data.get('participant_email', ''),
        call_data.get('case_id'),
        room_id
    ))
    conn.commit()
    return cursor.lastrowid

def mark_notification_reviewed(notification_id: int):
    """Mark an intake notification as reviewed"""
    for notif in st.session_state.intake_notifications:
        if notif['id'] == notification_id:
            notif['status'] = 'reviewed'
            notif['reviewed_at'] = datetime.now()
            break

# =============================================================================
# SIDEBAR RENDERING
# =============================================================================
def render_sidebar():
    """Render the sidebar with tab navigation"""
    with st.sidebar:
        # Logo/Brand
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid {COLORS['navy_light']}; margin-bottom: 1rem;">
                <h2 style="color: {COLORS['white']}; margin: 0;">Professional Hubs</h2>
                <p style="color: {COLORS['gray_medium']}; font-size: 0.8rem; margin: 0;">Legal Practice Management</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Tab selector
        tab_options = ["My Office", "Legal Workshop"]
        selected_tab = st.radio(
            "Navigation",
            tab_options,
            index=tab_options.index(st.session_state.current_tab),
            label_visibility="collapsed"
        )
        st.session_state.current_tab = selected_tab
        
        st.markdown("---")
        
        # Menu items based on selected tab
        if st.session_state.current_tab == "My Office":
            menu_items = ["Dashboard", "Clients", "My Cases", "Civus IA"]
        else:  # Legal Workshop
            menu_items = ["Schedule", "Forms", "Calls", "Invoices", "Reports", "Settings", "Collaborators"]
        
        for item in menu_items:
            if st.button(item, key=f"menu_{item}", use_container_width=True):
                st.session_state.current_page = item
                st.rerun()
        
        # Connection status
        st.markdown("---")
        st.markdown(f"""
            <div style="padding: 0.5rem; background: {COLORS['navy_dark']}; border-radius: 4px; margin-top: 1rem;">
                <p style="color: {COLORS['gray_medium']}; font-size: 0.75rem; margin: 0;">API: {API_BASE_URL}</p>
                <p style="color: {COLORS['gray_medium']}; font-size: 0.75rem; margin: 0;">Firm ID: {FIRM_ID}</p>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# PAGE: DASHBOARD
# =============================================================================
def render_dashboard():
    """Render the main dashboard page"""
    # Header
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Dashboard</h1>
            <p class="header-subtitle">Panel de Control - {datetime.now().strftime('%A, %d de %B de %Y')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Pending Intake Notifications (Require Action)
    pending_notifications = [n for n in st.session_state.intake_notifications if n['status'] == 'pending']
    
    if pending_notifications:
        st.markdown('<p class="section-header">Notificaciones de Llamadas - Accion Requerida</p>', unsafe_allow_html=True)
        
        for notif in pending_notifications:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"""
                        <div class="notification-card">
                            <div class="notification-title">{notif['caller_name']}</div>
                            <div class="notification-detail"><strong>Telefono:</strong> {notif['phone']}</div>
                            <div class="notification-detail"><strong>Email:</strong> {notif['email']}</div>
                            <div class="notification-detail"><strong>Tipo de Caso:</strong> {notif['case_type']}</div>
                            <div class="notification-detail"><strong>Descripcion:</strong> {notif['description']}</div>
                            <div class="notification-detail"><strong>Recibido:</strong> {notif['created_at'].strftime('%Y-%m-%d %H:%M')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if st.button("Marcar Revisado", key=f"review_{notif['id']}"):
                        mark_notification_reviewed(notif['id'])
                        st.rerun()
    
    # Metrics Row
    st.markdown('<p class="section-header">Resumen</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        active_cases = get_active_cases_count()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{active_cases}</div>
                <div class="metric-label">Total Casos Activos</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        today_meetings = get_today_meetings()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(today_meetings)}</div>
                <div class="metric-label">Citas Hoy</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        today_calls = get_today_video_calls()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(today_calls)}</div>
                <div class="metric-label">Video Llamadas</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Calendar Section
    st.markdown('<p class="section-header">Calendario - Agenda</p>', unsafe_allow_html=True)
    
    # Calendar navigation
    col1, col2, col3, col4 = st.columns([1, 1, 2, 2])
    
    if 'calendar_month' not in st.session_state:
        st.session_state.calendar_month = datetime.now().month
    if 'calendar_year' not in st.session_state:
        st.session_state.calendar_year = datetime.now().year
    
    with col1:
        if st.button("Anterior"):
            st.session_state.calendar_month -= 1
            if st.session_state.calendar_month < 1:
                st.session_state.calendar_month = 12
                st.session_state.calendar_year -= 1
            st.rerun()
    
    with col2:
        if st.button("Siguiente"):
            st.session_state.calendar_month += 1
            if st.session_state.calendar_month > 12:
                st.session_state.calendar_month = 1
                st.session_state.calendar_year += 1
            st.rerun()
    
    with col3:
        if st.button("Hoy"):
            st.session_state.calendar_month = datetime.now().month
            st.session_state.calendar_year = datetime.now().year
            st.rerun()
    
    # Month/Year display
    months_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    st.markdown(f"""
        <div class="calendar-header">
            {months_es[st.session_state.calendar_month - 1]} {st.session_state.calendar_year}
        </div>
    """, unsafe_allow_html=True)
    
    # Get events for current month
    events = get_calendar_events(st.session_state.calendar_month, st.session_state.calendar_year)
    
    # Display calendar grid
    # calendar module imported at top level
    cal = calendar.Calendar(firstweekday=0)  # Monday first
    month_days = cal.monthdayscalendar(st.session_state.calendar_year, st.session_state.calendar_month)
    
    # Header row
    days_header = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
    cols = st.columns(7)
    for i, day in enumerate(days_header):
        with cols[i]:
            st.markdown(f"<div style='text-align: center; font-weight: bold; color: {COLORS['navy_primary']};'>{day}</div>", unsafe_allow_html=True)
    
    # Calendar days
    today = date.today()
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    current_date = date(st.session_state.calendar_year, st.session_state.calendar_month, day)
                    is_today = current_date == today
                    
                    # Check for events on this day
                    day_events = [e for e in events if e['event_date'] == current_date.isoformat()]
                    
                    bg_color = COLORS['navy_primary'] if is_today else (COLORS['gray_light'] if day_events else COLORS['white'])
                    text_color = COLORS['white'] if is_today else COLORS['navy_primary']
                    
                    event_dot = f"<span style='color: {COLORS['warning']};'>*</span>" if day_events else ""
                    
                    st.markdown(f"""
                        <div style='text-align: center; padding: 0.5rem; background: {bg_color}; border-radius: 4px; color: {text_color};'>
                            {day}{event_dot}
                        </div>
                    """, unsafe_allow_html=True)
    
    # Add Event Form
    with st.expander("Agregar Evento"):
        with st.form("add_event_form"):
            event_title = st.text_input("Titulo del Evento")
            event_date = st.date_input("Fecha", value=date.today())
            event_time = st.time_input("Hora")
            event_type = st.selectbox("Tipo", ["Reunion", "Audiencia", "Cita", "Plazo", "Recordatorio"])
            event_description = st.text_area("Descripcion")
            
            if st.form_submit_button("Guardar Evento"):
                if event_title:
                    add_calendar_event({
                        'title': event_title,
                        'event_date': event_date.isoformat(),
                        'event_time': event_time.strftime('%H:%M'),
                        'event_type': event_type,
                        'description': event_description
                    })
                    st.success("Evento guardado exitosamente")
                    st.rerun()
    
    # Conflict alerts from clients/cases
    clients = get_all_clients()
    cases = get_all_cases()
    
    conflict_clients = [c for c in clients if c.get('has_conflict', 0) == 1]
    conflict_cases = [c for c in cases if c.get('has_conflict', 0) == 1]
    
    if conflict_clients or conflict_cases:
        st.markdown('<p class="section-header">Alertas de Conflictos de Interes</p>', unsafe_allow_html=True)
        
        for client in conflict_clients:
            st.markdown(f"""
                <div class="alert-danger">
                    <strong>CONFLICTO - Cliente:</strong> {client['nombre']} {client['apellido']}<br>
                    <span style="font-size: 0.875rem;">{client.get('conflict_details', 'Conflicto detectado')}</span>
                </div>
            """, unsafe_allow_html=True)
        
        for case in conflict_cases:
            st.markdown(f"""
                <div class="alert-danger">
                    <strong>CONFLICTO - Caso:</strong> {case['client_name']} - {case['case_type']}<br>
                    <span style="font-size: 0.875rem;">{case.get('conflict_details', 'Conflicto detectado')}</span>
                </div>
            """, unsafe_allow_html=True)

# =============================================================================
# PAGE: CLIENTS
# =============================================================================
def render_clients():
    """Render the clients management page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Clientes</h1>
            <p class="header-subtitle">Gestion de Clientes</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Lista de Clientes", "Nuevo Cliente"])
    
    with tab1:
        clients = get_all_clients()
        
        if clients:
            # Create DataFrame for display
            df_data = []
            for client in clients:
                conflict_status = "CONFLICTO" if client.get('has_conflict', 0) == 1 else "OK"
                df_data.append({
                    "ID": client['id'],
                    "Nombre": client['nombre'],
                    "Apellido": client['apellido'],
                    "Empresa": client.get('empresa', ''),
                    "Email": client['email'],
                    "Telefono": client['telefono'],
                    "Direccion": client['direccion'],
                    "COI": conflict_status
                })
            
            df = pd.DataFrame(df_data)
            
            # Style the dataframe to highlight conflicts
            def highlight_conflicts(row):
                if row['COI'] == 'CONFLICTO':
                    return ['background-color: #fed7d7'] * len(row)
                return [''] * len(row)
            
            styled_df = df.style.apply(highlight_conflicts, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay clientes registrados. Agregue un nuevo cliente.")
    
    with tab2:
        st.markdown('<p class="section-header">Nuevo Cliente</p>', unsafe_allow_html=True)
        
        with st.form("new_client_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input("Email *")
                apellido = st.text_input("Apellido *")
                direccion = st.text_input("Direccion *")
                telefono = st.text_input("Telefono *")
            
            with col2:
                nombre = st.text_input("Nombre *")
                empresa = st.text_input("Empresa (Opcional)")
                direccion_postal = st.text_input("Direccion Postal (PO Box)")
                segundo_apellido = st.text_input("Segundo Apellido (Opcional)")
            
            submitted = st.form_submit_button("Crear Cliente", use_container_width=True)
            
            if submitted:
                if not all([email, nombre, apellido, direccion, telefono]):
                    st.error("Por favor complete todos los campos requeridos (*)")
                else:
                    # Automatic COI Check
                    with st.spinner("Verificando conflictos de interes..."):
                        # Check against API
                        api_result = check_coi_api(nombre, apellido, segundo_apellido, empresa)

                        # Check against local database
                        local_result = check_coi_local(nombre, apellido)

                        # Show offline mode warning if needed
                        if api_result.get('offline', False):
                            st.warning(f"⚠️ {api_result.get('error', 'API no disponible')} - Verificacion limitada a base de datos local")

                        total_conflicts = api_result.get('total_conflictos', 0) + local_result.get('total_conflictos', 0)

                        has_conflict = 1 if total_conflicts > 0 else 0
                        conflict_details = ""

                        if total_conflicts > 0:
                            conflict_details = f"API: {api_result.get('total_conflictos', 0)} conflictos. Local: {local_result.get('total_conflictos', 0)} conflictos."
                            st.markdown(f"""
                                <div class="alert-danger">
                                    <strong>ALERTA DE CONFLICTO</strong><br>
                                    Se detectaron {total_conflicts} posible(s) conflicto(s) de interes.<br>
                                    El cliente sera guardado con una marca de conflicto.
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div class="alert-success">
                                    <strong>Sin Conflictos</strong><br>
                                    No se detectaron conflictos de interes.
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Save client
                    client_id = add_client({
                        'email': email,
                        'nombre': nombre,
                        'apellido': apellido,
                        'segundo_apellido': segundo_apellido,
                        'empresa': empresa,
                        'direccion': direccion,
                        'direccion_postal': direccion_postal,
                        'telefono': telefono,
                        'has_conflict': has_conflict,
                        'conflict_details': conflict_details
                    })
                    
                    st.success(f"Cliente creado exitosamente (ID: {client_id})")
                    st.rerun()

# =============================================================================
# PAGE: MY CASES
# =============================================================================
def render_my_cases():
    """Render the cases management page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Mis Casos</h1>
            <p class="header-subtitle">Gestion de Casos Legales</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Lista de Casos", "Nuevo Caso"])
    
    with tab1:
        cases = get_all_cases()
        
        if cases:
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filtrar por Estado", ["Todos", "Activo", "Cerrado", "Pendiente"])
            with col2:
                area_filter = st.selectbox("Filtrar por Area Legal", ["Todas"] + LEGAL_AREAS)
            
            # Apply filters
            filtered_cases = cases
            if status_filter != "Todos":
                filtered_cases = [c for c in filtered_cases if c['status'] == status_filter]
            if area_filter != "Todas":
                filtered_cases = [c for c in filtered_cases if c['legal_area'] == area_filter]
            
            # Create DataFrame
            df_data = []
            for case in filtered_cases:
                conflict_status = "CONFLICTO" if case.get('has_conflict', 0) == 1 else "OK"
                df_data.append({
                    "ID": case['id'],
                    "Cliente": case['client_name'],
                    "Parte Contraria": case.get('opposing_party', ''),
                    "Area Legal": case['legal_area'],
                    "Tipo": case['case_type'],
                    "Fecha Apertura": case['opening_date'],
                    "Estado": case['status'],
                    "COI": conflict_status
                })
            
            df = pd.DataFrame(df_data)
            
            # Style to highlight conflicts
            def highlight_conflicts(row):
                if row['COI'] == 'CONFLICTO':
                    return ['background-color: #fed7d7'] * len(row)
                return [''] * len(row)
            
            styled_df = df.style.apply(highlight_conflicts, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay casos registrados. Agregue un nuevo caso.")
    
    with tab2:
        st.markdown('<p class="section-header">Nuevo Caso</p>', unsafe_allow_html=True)
        
        # Get clients for dropdown
        clients = get_all_clients()
        client_options = {f"{c['nombre']} {c['apellido']} ({c['email']})": c['id'] for c in clients}
        
        if not clients:
            st.warning("Debe agregar al menos un cliente antes de crear un caso.")
        else:
            with st.form("new_case_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_client = st.selectbox("Cliente *", list(client_options.keys()))
                    legal_area = st.selectbox("Area Legal *", LEGAL_AREAS)
                    opening_date = st.date_input("Fecha de Apertura *", value=date.today())
                    collaborating_attorneys = st.text_input("Abogados Colaboradores (separados por coma)")
                
                with col2:
                    opposing_party = st.text_input("Parte Contraria")
                    # Dynamic case types based on legal area
                    case_types = CASE_TYPES.get(legal_area, ["Otro"])
                    case_type = st.selectbox("Tipo de Caso *", case_types)
                    status = st.selectbox("Estado *", ["Activo", "Pendiente", "Cerrado"])
                
                submitted = st.form_submit_button("Crear Caso", use_container_width=True)
                
                if submitted:
                    client_id = client_options[selected_client]
                    client_name = selected_client.split(" (")[0]
                    
                    # COI Check for opposing party
                    has_conflict = 0
                    conflict_details = ""
                    
                    if opposing_party:
                        st.info("Verificando conflictos con parte contraria...")
                        local_result = check_coi_local(opposing_party.split()[0] if opposing_party else "", 
                                                       opposing_party.split()[-1] if opposing_party else "",
                                                       opposing_party)
                        
                        if local_result.get('total_conflictos', 0) > 0:
                            has_conflict = 1
                            conflict_details = f"Conflicto con parte contraria: {opposing_party}"
                            st.markdown(f"""
                                <div class="alert-danger">
                                    <strong>ALERTA DE CONFLICTO</strong><br>
                                    La parte contraria coincide con un cliente o caso existente.<br>
                                    {conflict_details}
                                </div>
                            """, unsafe_allow_html=True)
                    
                    # Save case
                    case_id = add_case({
                        'client_id': client_id,
                        'client_name': client_name,
                        'opposing_party': opposing_party,
                        'legal_area': legal_area,
                        'case_type': case_type,
                        'collaborating_attorneys': collaborating_attorneys,
                        'opening_date': opening_date.isoformat(),
                        'status': status,
                        'has_conflict': has_conflict,
                        'conflict_details': conflict_details
                    })
                    
                    st.success(f"Caso creado exitosamente (ID: {case_id})")
                    st.rerun()

# =============================================================================
# PAGE: CIVUS IA (AI Assistant)
# =============================================================================
def render_civus_ia():
    """Render the Civus IA assistant page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Civus IA</h1>
            <p class="header-subtitle">Asistente de Inteligencia Artificial Legal</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="section-header">Verificacion Manual de Conflictos</p>', unsafe_allow_html=True)
    
    with st.form("coi_check_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            search_nombre = st.text_input("Nombre")
            search_apellido = st.text_input("Apellido")
        
        with col2:
            search_segundo = st.text_input("Segundo Apellido")
            search_empresa = st.text_input("Nombre de Empresa")
        
        if st.form_submit_button("Verificar Conflictos", use_container_width=True):
            if not any([search_nombre, search_apellido, search_empresa]):
                st.warning("Ingrese al menos un criterio de busqueda")
            else:
                with st.spinner("Buscando conflictos..."):
                    # API search
                    api_result = check_coi_api(search_nombre, search_apellido, search_segundo, search_empresa)
                    
                    # Local search
                    local_result = check_coi_local(search_nombre or "", search_apellido or "")
                    
                    st.markdown('<p class="section-header">Resultados de Busqueda</p>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Resultados API (Base de datos externa)**")
                        if api_result.get('error'):
                            if api_result.get('offline', False):
                                st.info(f"ℹ️ {api_result['error']}")
                            else:
                                st.warning(f"⚠️ API: {api_result['error']}")
                        elif api_result.get('total_conflictos', 0) > 0:
                            for conflict in api_result.get('conflictos', []):
                                st.markdown(f"""
                                    <div class="alert-danger">
                                        <strong>Conflicto Encontrado</strong><br>
                                        Cliente: {conflict.get('cliente_nombre', 'N/A')}<br>
                                        Asunto: {conflict.get('asunto_nombre', 'N/A')}<br>
                                        Confianza: {conflict.get('nivel_confianza', 'N/A')}
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div class="alert-success">Sin conflictos en base de datos externa</div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**Resultados Locales**")
                        if local_result.get('total_conflictos', 0) > 0:
                            for conflict in local_result.get('conflictos', []):
                                st.markdown(f"""
                                    <div class="alert-danger">
                                        <strong>Conflicto Local</strong><br>
                                        Tipo: {conflict.get('type', 'N/A')}<br>
                                        Nombre: {conflict.get('name', conflict.get('opposing_party', 'N/A'))}<br>
                                        Confianza: {conflict.get('confidence', 'N/A')}
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div class="alert-success">Sin conflictos en base de datos local</div>
                            """, unsafe_allow_html=True)

# =============================================================================
# PAGE: SCHEDULE (Legal Workshop)
# =============================================================================
def render_schedule():
    """Render the schedule page with Outlook integration info"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Agenda</h1>
            <p class="header-subtitle">Calendario y Programacion</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Outlook Integration Section
    st.markdown('<p class="section-header">Integracion con Outlook</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div class="alert-info">
                <strong>Sincronizacion con Microsoft Outlook</strong><br>
                Configure la integracion con su calendario de Outlook para sincronizar automaticamente sus citas y reuniones.
            </div>
        """, unsafe_allow_html=True)
        
        outlook_email = st.text_input("Correo de Outlook", placeholder="usuario@outlook.com")
        
        if st.button("Conectar con Outlook"):
            st.info("La integracion con Outlook requiere configuracion del servidor. Contacte al administrador.")
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">--</div>
                <div class="metric-label">Estado: No Conectado</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Statistics
    st.markdown('<p class="section-header">Estadisticas</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(get_today_meetings())}</div>
                <div class="metric-label">Hoy</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cursor = conn.cursor()
        week_start = date.today() - timedelta(days=date.today().weekday())
        week_end = week_start + timedelta(days=6)
        cursor.execute('SELECT COUNT(*) FROM calendar_events WHERE event_date BETWEEN ? AND ?', 
                      (week_start.isoformat(), week_end.isoformat()))
        week_count = cursor.fetchone()[0]
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{week_count}</div>
                <div class="metric-label">Esta Semana</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        cursor.execute('SELECT COUNT(*) FROM calendar_events WHERE strftime("%m", event_date) = ? AND strftime("%Y", event_date) = ?',
                      (f'{date.today().month:02d}', str(date.today().year)))
        month_count = cursor.fetchone()[0]
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{month_count}</div>
                <div class="metric-label">Este Mes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        cursor.execute('SELECT COUNT(*) FROM calendar_events')
        total_count = cursor.fetchone()[0]
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{total_count}</div>
                <div class="metric-label">Total Eventos</div>
            </div>
        """, unsafe_allow_html=True)

# =============================================================================
# PAGE: CALLS (Video Calls)
# =============================================================================
def render_calls():
    """Render the video calls page with in-app calling"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Video Llamadas</h1>
            <p class="header-subtitle">Sistema de Videoconferencias</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Llamadas Programadas", "Nueva Llamada", "Sala de Video"])
    
    with tab1:
        calls = get_today_video_calls()
        
        if calls:
            for call in calls:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                        <div class="notification-card">
                            <div class="notification-title">{call['title']}</div>
                            <div class="notification-detail"><strong>Fecha:</strong> {call['scheduled_date']}</div>
                            <div class="notification-detail"><strong>Hora:</strong> {call['scheduled_time']}</div>
                            <div class="notification-detail"><strong>Participante:</strong> {call.get('participant_name', 'N/A')}</div>
                            <div class="notification-detail"><strong>Sala ID:</strong> {call.get('room_id', 'N/A')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Iniciar Llamada", key=f"start_call_{call['id']}"):
                        st.session_state.video_call_active = True
                        st.session_state.active_call_room = call.get('room_id', '')
                        st.rerun()
        else:
            st.info("No hay llamadas programadas para hoy.")
    
    with tab2:
        st.markdown('<p class="section-header">Programar Nueva Video Llamada</p>', unsafe_allow_html=True)
        
        with st.form("new_video_call_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                call_title = st.text_input("Titulo de la Llamada *")
                call_date = st.date_input("Fecha *", value=date.today())
                participant_name = st.text_input("Nombre del Participante")
            
            with col2:
                call_time = st.time_input("Hora *")
                duration = st.selectbox("Duracion", [15, 30, 45, 60, 90], index=1)
                participant_email = st.text_input("Email del Participante")
            
            if st.form_submit_button("Programar Llamada", use_container_width=True):
                if call_title:
                    call_id = add_video_call({
                        'title': call_title,
                        'scheduled_date': call_date.isoformat(),
                        'scheduled_time': call_time.strftime('%H:%M'),
                        'duration_minutes': duration,
                        'participant_name': participant_name,
                        'participant_email': participant_email
                    })
                    st.success(f"Llamada programada exitosamente (ID: {call_id})")
                    st.rerun()
    
    with tab3:
        st.markdown('<p class="section-header">Sala de Video</p>', unsafe_allow_html=True)
        
        if st.session_state.video_call_active:
            st.markdown(f"""
                <div class="video-container">
                    <div class="video-placeholder">
                        <p style="font-size: 3rem; margin-bottom: 1rem;">Camara</p>
                        <p>Video llamada en progreso</p>
                        <p style="font-size: 0.875rem; margin-top: 1rem;">
                            Sala: {st.session_state.get('active_call_room', 'N/A')}
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Silenciar Microfono", use_container_width=True):
                    st.info("Microfono silenciado")
            with col2:
                if st.button("Desactivar Video", use_container_width=True):
                    st.info("Video desactivado")
            with col3:
                if st.button("Terminar Llamada", use_container_width=True, type="primary"):
                    st.session_state.video_call_active = False
                    st.rerun()
        else:
            st.markdown("""
                <div class="alert-info">
                    No hay ninguna llamada activa. Seleccione una llamada programada o inicie una nueva.
                </div>
            """, unsafe_allow_html=True)
            
            quick_room = st.text_input("ID de Sala (para unirse)")
            if st.button("Iniciar Llamada Rapida"):
                st.session_state.video_call_active = True
                st.session_state.active_call_room = quick_room or str(uuid.uuid4())[:8]
                st.rerun()

# =============================================================================
# PAGE: FORMS
# =============================================================================
def render_forms():
    """Render the forms management page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Formularios</h1>
            <p class="header-subtitle">Plantillas y Formularios Legales</p>
        </div>
    """, unsafe_allow_html=True)
    
    form_types = [
        "Contrato de Servicios Legales",
        "Poder General",
        "Poder Especial",
        "Formulario de Intake",
        "Cuestionario de Divorcio",
        "Cuestionario de Quiebra",
        "Autorizacion de Expediente Medico",
        "Acuerdo de Confidencialidad"
    ]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<p class="section-header">Tipos de Formularios</p>', unsafe_allow_html=True)
        for form_type in form_types:
            st.button(form_type, key=f"form_{form_type}", use_container_width=True)
    
    with col2:
        st.markdown('<p class="section-header">Vista Previa</p>', unsafe_allow_html=True)
        st.info("Seleccione un formulario para ver la vista previa y opciones de edicion.")

# =============================================================================
# PAGE: INVOICES
# =============================================================================
def render_invoices():
    """Render the invoices page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Facturacion</h1>
            <p class="header-subtitle">Gestion de Facturas</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Lista de Facturas", "Nueva Factura"])
    
    with tab1:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT i.*, c.nombre, c.apellido 
            FROM invoices i 
            JOIN clients c ON i.client_id = c.id 
            ORDER BY i.created_at DESC
        ''')
        invoices = cursor.fetchall()
        
        if invoices:
            df_data = []
            for inv in invoices:
                df_data.append({
                    "Numero": inv[3],
                    "Cliente": f"{inv[-2]} {inv[-1]}",
                    "Monto": f"${inv[4]:,.2f}",
                    "Estado": inv[5],
                    "Vencimiento": inv[6],
                    "Creada": inv[7]
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay facturas registradas.")
    
    with tab2:
        st.markdown('<p class="section-header">Nueva Factura</p>', unsafe_allow_html=True)
        
        clients = get_all_clients()
        client_options = {f"{c['nombre']} {c['apellido']}": c['id'] for c in clients}
        
        if clients:
            with st.form("new_invoice_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_client = st.selectbox("Cliente *", list(client_options.keys()))
                    amount = st.number_input("Monto *", min_value=0.0, step=0.01)
                
                with col2:
                    invoice_number = st.text_input("Numero de Factura *", value=f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")
                    due_date = st.date_input("Fecha de Vencimiento", value=date.today() + timedelta(days=30))
                
                if st.form_submit_button("Crear Factura", use_container_width=True):
                    if amount > 0:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO invoices (client_id, invoice_number, amount, due_date)
                            VALUES (?, ?, ?, ?)
                        ''', (client_options[selected_client], invoice_number, amount, due_date.isoformat()))
                        conn.commit()
                        st.success("Factura creada exitosamente")
                        st.rerun()
        else:
            st.warning("Agregue clientes primero.")

# =============================================================================
# PAGE: REPORTS
# =============================================================================
def render_reports():
    """Render the reports page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Reportes</h1>
            <p class="header-subtitle">Informes y Estadisticas</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        clients = get_all_clients()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(clients)}</div>
                <div class="metric-label">Total Clientes</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cases = get_all_cases()
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{len(cases)}</div>
                <div class="metric-label">Total Casos</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        active = len([c for c in cases if c['status'] == 'Activo'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{active}</div>
                <div class="metric-label">Casos Activos</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        conflicts = len([c for c in clients if c.get('has_conflict', 0) == 1])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{conflicts}</div>
                <div class="metric-label">Alertas COI</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Cases by legal area
    if cases:
        st.markdown('<p class="section-header">Casos por Area Legal</p>', unsafe_allow_html=True)
        area_counts = {}
        for case in cases:
            area = case['legal_area']
            area_counts[area] = area_counts.get(area, 0) + 1
        
        df = pd.DataFrame(list(area_counts.items()), columns=['Area Legal', 'Cantidad'])
        st.bar_chart(df.set_index('Area Legal'))

# =============================================================================
# PAGE: SETTINGS
# =============================================================================
def render_settings():
    """Render the settings page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Configuracion</h1>
            <p class="header-subtitle">Ajustes del Sistema</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["General", "Integraciones", "Base de Datos"])
    
    with tab1:
        st.markdown('<p class="section-header">Configuracion General</p>', unsafe_allow_html=True)
        
        firm_name = st.text_input("Nombre del Bufete", value="Mi Bufete Legal")
        firm_email = st.text_input("Email del Bufete")
        firm_phone = st.text_input("Telefono")
        firm_address = st.text_area("Direccion")
        
        if st.button("Guardar Configuracion"):
            st.success("Configuracion guardada")
    
    with tab2:
        st.markdown('<p class="section-header">Integraciones</p>', unsafe_allow_html=True)
        
        st.markdown("**API de Conflictos**")
        api_url = st.text_input("URL del API", value=API_BASE_URL)
        api_firm_id = st.number_input("Firm ID", value=FIRM_ID, min_value=1)
        
        if st.button("Probar Conexion API"):
            try:
                response = requests.get(f"{api_url}/health", timeout=5)
                if response.status_code == 200:
                    st.success("Conexion exitosa con el API")
                else:
                    st.error(f"Error: {response.status_code}")
            except:
                st.error("No se pudo conectar al API")
        
        st.markdown("---")
        st.markdown("**Microsoft Outlook**")
        st.info("La integracion con Outlook requiere credenciales de Microsoft Azure AD.")
    
    with tab3:
        st.markdown('<p class="section-header">Base de Datos Local</p>', unsafe_allow_html=True)
        
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases")
        case_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM calendar_events")
        event_count = cursor.fetchone()[0]
        
        st.write(f"Clientes: {client_count}")
        st.write(f"Casos: {case_count}")
        st.write(f"Eventos: {event_count}")
        
        if st.button("Limpiar Base de Datos", type="primary"):
            st.warning("Esta accion eliminara todos los datos. Use con precaucion.")

# =============================================================================
# PAGE: COLLABORATORS
# =============================================================================
def render_collaborators():
    """Render the collaborators page"""
    st.markdown(f"""
        <div class="header-container">
            <h1 class="header-title">Colaboradores</h1>
            <p class="header-subtitle">Gestion de Equipo</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("Funcion de colaboradores disponible en version multi-usuario.")
    
    st.markdown('<p class="section-header">Agregar Colaborador</p>', unsafe_allow_html=True)
    
    with st.form("add_collaborator"):
        col1, col2 = st.columns(2)
        
        with col1:
            collab_name = st.text_input("Nombre Completo")
            collab_email = st.text_input("Email")
        
        with col2:
            collab_role = st.selectbox("Rol", ["Abogado Asociado", "Paralegal", "Asistente", "Pasante"])
            collab_areas = st.multiselect("Areas de Practica", LEGAL_AREAS)
        
        if st.form_submit_button("Invitar Colaborador"):
            st.info("Invitacion enviada (simulado)")

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point"""
    render_sidebar()
    
    # Route to appropriate page based on current selection
    page = st.session_state.current_page
    
    if page == "Dashboard":
        render_dashboard()
    elif page == "Clients":
        render_clients()
    elif page == "My Cases":
        render_my_cases()
    elif page == "Civus IA":
        render_civus_ia()
    elif page == "Schedule":
        render_schedule()
    elif page == "Forms":
        render_forms()
    elif page == "Calls":
        render_calls()
    elif page == "Invoices":
        render_invoices()
    elif page == "Reports":
        render_reports()
    elif page == "Settings":
        render_settings()
    elif page == "Collaborators":
        render_collaborators()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()