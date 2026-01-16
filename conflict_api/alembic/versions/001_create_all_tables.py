"""create all tables - NO ENUMS VERSION

Revision ID: 001
Revises: None
Create Date: 2025-01-15

This migration creates ALL tables using String columns instead of PostgreSQL ENUMs.
This eliminates deployment issues with enum types.

Tables created:
- firmas (law firms)
- clientes (clients with email/telefono for billing)
- asuntos (legal matters)
- partes_relacionadas (related parties)
- invoices (for billing automation)
- billing_communication_logs (for billing automation)
- intake_calls_simple (for AI call agent - Phase 2)
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    conn = op.get_bind()
    result = conn.execute(text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def upgrade() -> None:
    """Create all tables for Professional Hubs."""
    
    print("\n" + "="*60)
    print("Professional Hubs - Complete Database Setup")
    print("NO PostgreSQL ENUMs - Using String columns")
    print("="*60 + "\n")
    
    # =========================================================================
    # CORE TABLES (Conflict Checker)
    # =========================================================================
    
    # FIRMAS table
    if not table_exists('firmas'):
        op.execute(text("""
            CREATE TABLE firmas (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_firmas_id ON firmas(id)"))
        print("  ✓ Created: firmas")
    else:
        print("  → Exists: firmas")
    
    # CLIENTES table (with email/telefono for billing)
    if not table_exists('clientes'):
        op.execute(text("""
            CREATE TABLE clientes (
                id SERIAL PRIMARY KEY,
                firma_id INTEGER NOT NULL REFERENCES firmas(id) ON DELETE CASCADE,
                nombre VARCHAR(100),
                apellido VARCHAR(100),
                segundo_apellido VARCHAR(100),
                nombre_empresa VARCHAR(255),
                email VARCHAR(255),
                telefono VARCHAR(50),
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_clientes_id ON clientes(id)"))
        op.execute(text("CREATE INDEX ix_clientes_firma_id ON clientes(firma_id)"))
        op.execute(text("CREATE INDEX ix_clientes_nombre_apellido ON clientes(nombre, apellido)"))
        op.execute(text("CREATE INDEX ix_clientes_nombre_empresa ON clientes(nombre_empresa)"))
        op.execute(text("CREATE INDEX ix_clientes_firma_activo ON clientes(firma_id, esta_activo)"))
        print("  ✓ Created: clientes")
    else:
        print("  → Exists: clientes")
    
    # ASUNTOS table (String for estado instead of ENUM)
    if not table_exists('asuntos'):
        op.execute(text("""
            CREATE TABLE asuntos (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
                nombre_asunto VARCHAR(500) NOT NULL,
                fecha_apertura DATE NOT NULL DEFAULT CURRENT_DATE,
                estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_asuntos_id ON asuntos(id)"))
        op.execute(text("CREATE INDEX ix_asuntos_cliente_id ON asuntos(cliente_id)"))
        op.execute(text("CREATE INDEX ix_asuntos_cliente_estado ON asuntos(cliente_id, estado)"))
        op.execute(text("CREATE INDEX ix_asuntos_fecha_apertura ON asuntos(fecha_apertura)"))
        print("  ✓ Created: asuntos")
    else:
        print("  → Exists: asuntos")
    
    # PARTES_RELACIONADAS table (String for tipo_relacion instead of ENUM)
    if not table_exists('partes_relacionadas'):
        op.execute(text("""
            CREATE TABLE partes_relacionadas (
                id SERIAL PRIMARY KEY,
                asunto_id INTEGER NOT NULL REFERENCES asuntos(id) ON DELETE CASCADE,
                nombre VARCHAR(255) NOT NULL,
                tipo_relacion VARCHAR(30) NOT NULL,
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_partes_relacionadas_id ON partes_relacionadas(id)"))
        op.execute(text("CREATE INDEX ix_partes_relacionadas_asunto_id ON partes_relacionadas(asunto_id)"))
        op.execute(text("CREATE INDEX ix_partes_nombre ON partes_relacionadas(nombre)"))
        op.execute(text("CREATE INDEX ix_partes_asunto_activo ON partes_relacionadas(asunto_id, esta_activo)"))
        print("  ✓ Created: partes_relacionadas")
    else:
        print("  → Exists: partes_relacionadas")
    
    # =========================================================================
    # BILLING AUTOMATION TABLES
    # =========================================================================
    
    # INVOICES table
    if not table_exists('invoices'):
        op.execute(text("""
            CREATE TABLE invoices (
                id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
                invoice_number VARCHAR(50) NOT NULL UNIQUE,
                amount NUMERIC(10, 2) NOT NULL,
                due_date DATE NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_invoices_id ON invoices(id)"))
        op.execute(text("CREATE INDEX ix_invoices_client_id ON invoices(client_id)"))
        op.execute(text("CREATE INDEX ix_invoices_due_date ON invoices(due_date)"))
        op.execute(text("CREATE INDEX ix_invoices_status ON invoices(status)"))
        print("  ✓ Created: invoices")
    else:
        print("  → Exists: invoices")
    
    # BILLING_COMMUNICATION_LOGS table (String for type/status instead of ENUM)
    if not table_exists('billing_communication_logs'):
        op.execute(text("""
            CREATE TABLE billing_communication_logs (
                id SERIAL PRIMARY KEY,
                invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                type VARCHAR(20) NOT NULL,
                message_body TEXT NOT NULL,
                subject VARCHAR(500),
                status VARCHAR(20) NOT NULL DEFAULT 'SENT',
                sent_at TIMESTAMP NOT NULL,
                delivered_at TIMESTAMP,
                read_at TIMESTAMP,
                external_id VARCHAR(255),
                error_message TEXT,
                days_overdue_when_sent INTEGER NOT NULL,
                reminder_sequence INTEGER NOT NULL,
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_billing_communication_logs_id ON billing_communication_logs(id)"))
        op.execute(text("CREATE INDEX ix_billing_comms_invoice_date ON billing_communication_logs(invoice_id, sent_at)"))
        op.execute(text("CREATE INDEX ix_billing_comms_status ON billing_communication_logs(status)"))
        op.execute(text("CREATE INDEX ix_billing_comms_type_date ON billing_communication_logs(type, sent_at)"))
        print("  ✓ Created: billing_communication_logs")
    else:
        print("  → Exists: billing_communication_logs")
    
    # =========================================================================
    # AI CALL AGENT TABLES (Phase 2 - ready but not active)
    # =========================================================================
    
    # INTAKE_CALLS_SIMPLE table (String for enums instead of ENUM)
    if not table_exists('intake_calls_simple'):
        op.execute(text("""
            CREATE TABLE intake_calls_simple (
                id SERIAL PRIMARY KEY,
                firma_id INTEGER NOT NULL REFERENCES firmas(id) ON DELETE CASCADE,
                twilio_call_sid VARCHAR(100) UNIQUE,
                numero_llamante VARCHAR(20) NOT NULL,
                idioma_detectado VARCHAR(5) DEFAULT 'ES',
                nombre VARCHAR(255),
                tipo_caso VARCHAR(20),
                telefono_contacto VARCHAR(20),
                nombre_completo VARCHAR(255),
                email VARCHAR(255),
                descripcion_caso TEXT,
                fecha_cita TIMESTAMP,
                abogado_asignado VARCHAR(255),
                google_calendar_event_id VARCHAR(255),
                estado VARCHAR(30) DEFAULT 'PENDIENTE',
                whatsapp_form_sent BOOLEAN DEFAULT false,
                whatsapp_form_completed BOOLEAN DEFAULT false,
                form_submission_id VARCHAR(255),
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_intake_calls_simple_id ON intake_calls_simple(id)"))
        op.execute(text("CREATE INDEX ix_intake_calls_firma_id ON intake_calls_simple(firma_id)"))
        op.execute(text("CREATE INDEX ix_intake_calls_call_sid ON intake_calls_simple(twilio_call_sid)"))
        print("  ✓ Created: intake_calls_simple")
    else:
        print("  → Exists: intake_calls_simple")
    
    print("\n" + "="*60)
    print("Database Setup Complete!")
    print("")
    print("Tables ready:")
    print("  • firmas, clientes, asuntos, partes_relacionadas")
    print("  • invoices, billing_communication_logs")
    print("  • intake_calls_simple (Phase 2)")
    print("="*60 + "\n")


def downgrade() -> None:
    """Drop all tables in reverse order."""
    conn = op.get_bind()
    
    tables = [
        'intake_calls_simple',
        'billing_communication_logs',
        'invoices',
        'partes_relacionadas',
        'asuntos',
        'clientes',
        'firmas'
    ]
    
    for table in tables:
        if table_exists(table):
            conn.execute(text(f"DROP TABLE {table} CASCADE"))
            print(f"  ✓ Dropped: {table}")