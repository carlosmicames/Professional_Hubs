"""
Professional Hubs - Conflict Checker Page
Verify conflicts of interest for potential new clients.
"""

import streamlit as st
import pandas as pd
from utils.api_client import api_client

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Verificar Conflictos | Professional Hubs",
    page_icon="🔍",
    layout="wide"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    .page-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .page-header h1 {
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
    }
    
    .page-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.5rem 0 0 0;
    }
    
    .search-container {
        background: linear-gradient(145deg, #1a1f2e 0%, #252b3d 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
    
    .result-card {
        background: linear-gradient(145deg, #1e2433 0%, #262d3d 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    
    .result-high {
        border-left-color: #f56565;
        background: linear-gradient(145deg, #2d1f1f 0%, #1e2433 100%);
    }
    
    .result-medium {
        border-left-color: #ed8936;
        background: linear-gradient(145deg, #2d2a1f 0%, #1e2433 100%);
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .confidence-alta {
        background: rgba(245, 101, 101, 0.2);
        color: #fc8181;
    }
    
    .confidence-media {
        background: rgba(237, 137, 54, 0.2);
        color: #f6ad55;
    }
    
    .no-conflict-card {
        background: linear-gradient(145deg, #1f2d1f 0%, #1e2433 100%);
        border: 1px solid rgba(72, 187, 120, 0.3);
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
        margin: 1.5rem 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# PAGE HEADER
# ============================================================================

st.markdown("""
<div class="page-header">
    <h1>🔍 Verificación de Conflictos de Interés</h1>
    <p>Busque posibles conflictos antes de aceptar un nuevo cliente o caso</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# SEARCH FORM
# ============================================================================

st.markdown("""
<div class="search-container">
    <h3 style="color: #e2e8f0; margin-top: 0;">Buscar Cliente Potencial</h3>
    <p style="color: #a0aec0; margin-bottom: 1.5rem;">
        Ingrese los datos del cliente potencial. El sistema buscará coincidencias en su base de datos 
        de clientes existentes y partes relacionadas.
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs for person vs company search
tab_persona, tab_empresa = st.tabs(["👤 Persona Natural", "🏢 Empresa"])

with tab_persona:
    st.markdown("##### Datos de Persona")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nombre = st.text_input(
            "Nombre",
            placeholder="Ej: Juan",
            key="nombre_persona"
        )
    
    with col2:
        apellido = st.text_input(
            "Primer Apellido",
            placeholder="Ej: García",
            key="apellido_persona"
        )
    
    with col3:
        segundo_apellido = st.text_input(
            "Segundo Apellido (opcional)",
            placeholder="Ej: Rivera",
            key="segundo_apellido_persona"
        )
    
    st.markdown("")  # Spacer
    
    if st.button("🔍 Verificar Conflicto", key="btn_persona", width='content'):
        if not nombre and not apellido:
            st.error("⚠️ Debe ingresar al menos el nombre o apellido")
        else:
            with st.spinner("Buscando conflictos..."):
                result = api_client.verificar_conflicto(
                    nombre=nombre if nombre else None,
                    apellido=apellido if apellido else None,
                    segundo_apellido=segundo_apellido if segundo_apellido else None
                )
                
                if result["success"]:
                    st.session_state["conflict_result"] = result["data"]
                else:
                    st.error(f"❌ Error: {result['error']}")

with tab_empresa:
    st.markdown("##### Datos de Empresa")
    nombre_empresa = st.text_input(
        "Nombre de la Empresa",
        placeholder="Ej: Corporación ABC de Puerto Rico",
        key="nombre_empresa_input"
    )
    
    st.markdown("")  # Spacer
    
    if st.button("🔍 Verificar Conflicto", key="btn_empresa", width='content'):
        if not nombre_empresa:
            st.error("⚠️ Debe ingresar el nombre de la empresa")
        else:
            with st.spinner("Buscando conflictos..."):
                result = api_client.verificar_conflicto(
                    nombre_empresa=nombre_empresa
                )
                
                if result["success"]:
                    st.session_state["conflict_result"] = result["data"]
                else:
                    st.error(f"❌ Error: {result['error']}")

# ============================================================================
# RESULTS DISPLAY
# ============================================================================

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

if "conflict_result" in st.session_state:
    result = st.session_state["conflict_result"]
    
    # Header with search term
    st.markdown(f"""
    <h3 style="color: #e2e8f0;">
        Resultados para: <span style="color: #667eea;">"{result['termino_busqueda']}"</span>
    </h3>
    """, unsafe_allow_html=True)
    
    # Summary message
    if result["total_conflictos"] == 0:
        st.markdown("""
        <div class="no-conflict-card">
            <h2 style="color: #48bb78; margin: 0;">✅ Sin Conflictos Detectados</h2>
            <p style="color: #a0aec0; margin-top: 1rem; margin-bottom: 0;">
                No se encontraron coincidencias en la base de datos. 
                Puede proceder con la evaluación del cliente potencial.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Clear button
        if st.button("🔄 Nueva Búsqueda"):
            del st.session_state["conflict_result"]
            st.rerun()
    
    else:
        # Conflict warning
        alta_count = sum(1 for c in result["conflictos"] if c["nivel_confianza"] == "alta")
        media_count = sum(1 for c in result["conflictos"] if c["nivel_confianza"] == "media")
        
        st.markdown(f"""
        <div style="background: rgba(245, 101, 101, 0.1); border: 1px solid rgba(245, 101, 101, 0.3); 
                    border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
            <h3 style="color: #fc8181; margin: 0;">
                ⚠️ {result['total_conflictos']} Posible(s) Conflicto(s) Detectado(s)
            </h3>
            <p style="color: #feb2b2; margin: 0.5rem 0 0 0;">
                {alta_count} de alta confianza • {media_count} de media confianza
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display each conflict
        for i, conflicto in enumerate(result["conflictos"], 1):
            confidence_class = "confidence-alta" if conflicto["nivel_confianza"] == "alta" else "confidence-media"
            result_class = "result-high" if conflicto["nivel_confianza"] == "alta" else "result-medium"
            confidence_text = "ALTA" if conflicto["nivel_confianza"] == "alta" else "MEDIA"
            
            with st.container():
                st.markdown(f"""
                <div class="result-card {result_class}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <div>
                            <h4 style="color: #e2e8f0; margin: 0; font-size: 1.1rem;">
                                Conflicto #{i}: {conflicto['cliente_nombre']}
                            </h4>
                            <p style="color: #a0aec0; margin: 0.25rem 0 0 0; font-size: 0.9rem;">
                                {conflicto['campo_coincidente']}
                            </p>
                        </div>
                        <div>
                            <span class="confidence-badge {confidence_class}">
                                {confidence_text} ({conflicto['similitud_score']:.1f}%)
                            </span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                        <div>
                            <p style="color: #718096; font-size: 0.8rem; margin: 0;">ASUNTO</p>
                            <p style="color: #e2e8f0; margin: 0.25rem 0 0 0; font-size: 0.95rem;">
                                {conflicto['asunto_nombre'][:50]}{'...' if len(conflicto['asunto_nombre']) > 50 else ''}
                            </p>
                        </div>
                        <div>
                            <p style="color: #718096; font-size: 0.8rem; margin: 0;">ESTADO</p>
                            <p style="color: #e2e8f0; margin: 0.25rem 0 0 0; font-size: 0.95rem;">
                                {conflicto['estado_asunto']}
                            </p>
                        </div>
                        <div>
                            <p style="color: #718096; font-size: 0.8rem; margin: 0;">TIPO</p>
                            <p style="color: #e2e8f0; margin: 0.25rem 0 0 0; font-size: 0.95rem;">
                                {conflicto['tipo_coincidencia'].replace('_', ' ').title()}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("")  # Spacer
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🔄 Nueva Búsqueda"):
                del st.session_state["conflict_result"]
                st.rerun()
        
        with col2:
            # Export results
            df = pd.DataFrame(result["conflictos"])
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Exportar CSV",
                csv,
                f"conflictos_{result['termino_busqueda'].replace(' ', '_')}.csv",
                "text/csv"
            )

else:
    # Initial state - show instructions
    st.markdown("""
    <div style="text-align: center; padding: 3rem; color: #718096;">
        <p style="font-size: 3rem; margin-bottom: 1rem;">🔍</p>
        <h3 style="color: #a0aec0;">Ingrese los datos arriba para iniciar la búsqueda</h3>
        <p>El sistema comparará contra toda su base de datos de clientes y partes relacionadas.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR INFO
# ============================================================================

with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 8px;">
        <h4 style="color: #667eea; margin: 0 0 0.75rem 0;">ℹ️ Cómo Funciona</h4>
        <p style="color: #a0aec0; font-size: 0.85rem; margin: 0; line-height: 1.6;">
            El sistema utiliza búsqueda difusa (fuzzy matching) para detectar coincidencias incluso con:
        </p>
        <ul style="color: #a0aec0; font-size: 0.85rem; margin: 0.5rem 0 0 0; padding-left: 1.25rem;">
            <li>Variaciones de acentos (José = Jose)</li>
            <li>Errores tipográficos</li>
            <li>Orden diferente de nombres</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    st.markdown("""
    <div style="padding: 1rem; background: rgba(245, 101, 101, 0.1); border-radius: 8px;">
        <h4 style="color: #fc8181; margin: 0 0 0.75rem 0;">⚠️ Niveles de Confianza</h4>
        <p style="color: #feb2b2; font-size: 0.85rem; margin: 0;">
            <strong>Alta (≥90%):</strong> Coincidencia casi exacta<br>
            <strong>Media (70-89%):</strong> Coincidencia posible
        </p>
    </div>
    """, unsafe_allow_html=True)