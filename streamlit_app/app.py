"""
Professional Hubs - Conflict Checker
Streamlit Frontend Application - FIXED FOR DEPLOYMENT
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", st.secrets.get("API_BASE_URL", "http://localhost:8000"))
FIRM_ID = int(os.getenv("FIRM_ID", st.secrets.get("FIRM_ID", "1")))

# Page configuration
st.set_page_config(
    page_title="Professional Hubs - Conflict Checker",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 2rem;
    }

    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }

    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }

    /* Search box styling */
    .search-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }

    /* Confidence badges */
    .confidence-high {
        background-color: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.875rem;
    }

    .confidence-medium {
        background-color: #f59e0b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 0.875rem;
    }

    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }

    .stat-label {
        color: #6b7280;
        font-size: 0.875rem;
        margin-top: 0.5rem;
    }

    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }

    /* Alert boxes */
    .alert-success {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .alert-warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    .alert-danger {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }

    /* Logo styling */
    .logo-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }

    .logo-text {
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'current_user' not in st.session_state:
    st.session_state.current_user = "Usuario"


def log_search(search_term: str, results_count: int, user: str):
    """Log search activity with timestamp"""
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "search_term": search_term,
        "results_count": results_count
    }
    st.session_state.search_history.insert(0, log_entry)

    # Keep only last 100 searches
    if len(st.session_state.search_history) > 100:
        st.session_state.search_history = st.session_state.search_history[:100]


def search_conflicts(nombre: str = None, apellido: str = None, segundo_apellido: str = None, nombre_empresa: str = None) -> Optional[Dict]:
    """Search for conflicts via API"""
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
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error API: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("⚠️ No se puede conectar al servidor API. Verifique que el servidor esté ejecutándose.")
        return None
    except Exception as e:
        st.error(f"Error al buscar conflictos: {str(e)}")
        return None


def render_confidence_badge(nivel: str, score: float) -> str:
    """Render HTML confidence badge"""
    if nivel == "alta":
        return f'<span class="confidence-high">ALTA ({score:.1f}%)</span>'
    else:
        return f'<span class="confidence-medium">MEDIA ({score:.1f}%)</span>'


def render_results_table(conflicts: List[Dict]):
    """Render conflicts results as a styled table"""
    if not conflicts:
        st.info("✅ No se encontraron conflictos de interés.")
        return

    # Prepare data for DataFrame
    table_data = []
    for conflict in conflicts:
        table_data.append({
            "Cliente": conflict["cliente_nombre"],
            "Asunto": conflict["asunto_nombre"],
            "Estado": conflict["estado_asunto"].upper(),
            "Campo Coincidente": conflict["campo_coincidente"],
            "Tipo": conflict["tipo_coincidencia"].replace("_", " ").title(),
            "Confianza": conflict["nivel_confianza"].upper(),
            "Similitud": f"{conflict['similitud_score']:.1f}%"
        })

    df = pd.DataFrame(table_data)

    # Style the dataframe
    def highlight_confidence(row):
        if row["Confianza"] == "ALTA":
            return ['background-color: #fee2e2'] * len(row)
        elif row["Confianza"] == "MEDIA":
            return ['background-color: #fef3c7'] * len(row)
        return [''] * len(row)

    styled_df = df.style.apply(highlight_confidence, axis=1)

    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def render_header():
    """Render page header"""
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">⚖️ Professional Hubs</h1>
            <p class="header-subtitle">Sistema de Verificación de Conflictos de Interés</p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with settings and history"""
    with st.sidebar:
        # Logo replacement - using styled text instead of image
        st.markdown("""
            <div class="logo-container">
                <p class="logo-text">⚖️ Professional Hubs</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User settings
        st.subheader("👤 Usuario")
        st.session_state.current_user = st.text_input(
            "Nombre del usuario",
            value=st.session_state.current_user,
            help="Nombre del abogado realizando la búsqueda"
        )

        st.markdown("---")

        # API settings
        st.subheader("⚙️ Configuración")
        st.caption(f"**API:** {API_BASE_URL}")
        st.caption(f"**Firma ID:** {FIRM_ID}")

        # Test API connection
        if st.button("🔄 Probar Conexión API"):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Conectado al servidor")
                else:
                    st.error("❌ Error de conexión")
            except:
                st.error("❌ No se puede conectar")

        st.markdown("---")

        # Search history
        st.subheader("📜 Historial de Búsquedas")

        if st.session_state.search_history:
            st.caption(f"Últimas {min(10, len(st.session_state.search_history))} búsquedas")

            for entry in st.session_state.search_history[:10]:
                with st.expander(f"{entry['timestamp']} - {entry['user']}", expanded=False):
                    st.caption(f"**Búsqueda:** {entry['search_term']}")
                    st.caption(f"**Resultados:** {entry['results_count']}")

            if st.button("🗑️ Limpiar Historial"):
                st.session_state.search_history = []
                st.rerun()
        else:
            st.info("Sin búsquedas recientes")


def main():
    """Main application"""
    # Render UI components
    render_header()
    render_sidebar()

    # Search interface
    st.markdown("### 🔍 Búsqueda de Conflictos")

    # Tabs for person vs company search
    tab1, tab2 = st.tabs(["👤 Persona Natural", "🏢 Empresa"])

    with tab1:
        st.markdown("#### Buscar por nombre de persona")

        col1, col2, col3 = st.columns(3)

        with col1:
            nombre = st.text_input(
                "Nombre",
                placeholder="Ej: José",
                help="Primer nombre de la persona"
            )

        with col2:
            apellido = st.text_input(
                "Primer Apellido",
                placeholder="Ej: García",
                help="Primer apellido"
            )

        with col3:
            segundo_apellido = st.text_input(
                "Segundo Apellido",
                placeholder="Ej: Rivera",
                help="Segundo apellido (opcional)"
            )

        search_person = st.button("🔎 Buscar Persona", type="primary", use_container_width=True)

        if search_person:
            if not nombre and not apellido:
                st.warning("⚠️ Debe proporcionar al menos nombre o apellido")
            else:
                with st.spinner("Buscando conflictos..."):
                    results = search_conflicts(
                        nombre=nombre,
                        apellido=apellido,
                        segundo_apellido=segundo_apellido
                    )

                    if results:
                        # Log search
                        search_term = " ".join(filter(None, [nombre, apellido, segundo_apellido]))
                        log_search(search_term, results["total_conflictos"], st.session_state.current_user)

                        # Display results
                        st.markdown("---")
                        st.markdown(f"### 📊 Resultados: {results['termino_busqueda']}")

                        # Stats cards
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-number">{results['total_conflictos']}</div>
                                    <div class="stat-label">Total Conflictos</div>
                                </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            alta = sum(1 for c in results['conflictos'] if c['nivel_confianza'] == 'alta')
                            st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-number" style="color: #ef4444;">{alta}</div>
                                    <div class="stat-label">Confianza Alta</div>
                                </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            media = sum(1 for c in results['conflictos'] if c['nivel_confianza'] == 'media')
                            st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-number" style="color: #f59e0b;">{media}</div>
                                    <div class="stat-label">Confianza Media</div>
                                </div>
                            """, unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Alert based on results
                        if alta > 0:
                            st.markdown(f"""
                                <div class="alert-danger">
                                    <strong>⚠️ ATENCIÓN:</strong> Se encontraron {alta} conflicto(s) de alta confianza.
                                    Revisar antes de aceptar el caso.
                                </div>
                            """, unsafe_allow_html=True)
                        elif media > 0:
                            st.markdown(f"""
                                <div class="alert-warning">
                                    <strong>⚡ PRECAUCIÓN:</strong> Se encontraron {media} conflicto(s) de confianza media.
                                    Verificar antes de proceder.
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div class="alert-success">
                                    <strong>✅ SIN CONFLICTOS:</strong> No se encontraron conflictos de interés.
                                </div>
                            """, unsafe_allow_html=True)

                        # Results table
                        st.markdown("#### Detalles de Conflictos Encontrados")
                        render_results_table(results['conflictos'])

                        # Export option
                        if results['conflictos']:
                            df = pd.DataFrame(results['conflictos'])
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Exportar a CSV",
                                data=csv,
                                file_name=f"conflictos_{search_term.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )

    with tab2:
        st.markdown("#### Buscar por nombre de empresa")

        nombre_empresa = st.text_input(
            "Nombre de Empresa",
            placeholder="Ej: Corporación ABC",
            help="Nombre completo de la empresa"
        )

        search_company = st.button("🔎 Buscar Empresa", type="primary", use_container_width=True)

        if search_company:
            if not nombre_empresa:
                st.warning("⚠️ Debe proporcionar el nombre de la empresa")
            else:
                with st.spinner("Buscando conflictos..."):
                    results = search_conflicts(nombre_empresa=nombre_empresa)

                    if results:
                        # Log search
                        log_search(nombre_empresa, results["total_conflictos"], st.session_state.current_user)

                        # Display results (same as person search)
                        st.markdown("---")
                        st.markdown(f"### 📊 Resultados: {results['termino_busqueda']}")

                        # Stats cards
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-number">{results['total_conflictos']}</div>
                                    <div class="stat-label">Total Conflictos</div>
                                </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            alta = sum(1 for c in results['conflictos'] if c['nivel_confianza'] == 'alta')
                            st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-number" style="color: #ef4444;">{alta}</div>
                                    <div class="stat-label">Confianza Alta</div>
                                </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            media = sum(1 for c in results['conflictos'] if c['nivel_confianza'] == 'media')
                            st.markdown(f"""
                                <div class="stat-card">
                                    <div class="stat-number" style="color: #f59e0b;">{media}</div>
                                    <div class="stat-label">Confianza Media</div>
                                </div>
                            """, unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Alert based on results
                        if alta > 0:
                            st.markdown(f"""
                                <div class="alert-danger">
                                    <strong>⚠️ ATENCIÓN:</strong> Se encontraron {alta} conflicto(s) de alta confianza.
                                </div>
                            """, unsafe_allow_html=True)
                        elif media > 0:
                            st.markdown(f"""
                                <div class="alert-warning">
                                    <strong>⚡ PRECAUCIÓN:</strong> Se encontraron {media} conflicto(s) de confianza media.
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                                <div class="alert-success">
                                    <strong>✅ SIN CONFLICTOS:</strong> No se encontraron conflictos de interés.
                                </div>
                            """, unsafe_allow_html=True)

                        # Results table
                        st.markdown("#### Detalles de Conflictos Encontrados")
                        render_results_table(results['conflictos'])

                        # Export option
                        if results['conflictos']:
                            df = pd.DataFrame(results['conflictos'])
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Exportar a CSV",
                                data=csv,
                                file_name=f"conflictos_{nombre_empresa.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #6b7280; font-size: 0.875rem;'>"
        "Professional Hubs © 2025 | Sistema de Verificación de Conflictos para Bufetes de Puerto Rico"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":