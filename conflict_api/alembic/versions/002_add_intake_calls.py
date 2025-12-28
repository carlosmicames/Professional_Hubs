# conflict_api/alembic/versions/003_add_simple_intake.py
"""add simple intake calls

Revision ID: 003
Revises: 002
Create Date: 2025-12-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add simplified intake_calls_simple table."""
    
    # Create enums
    op.execute("""
        CREATE TYPE tipo_caso_simple AS ENUM ('familia', 'lesiones', 'laboral', 'inmobiliario', 'criminal', 'comercial', 'otro');
        CREATE TYPE estado_consulta AS ENUM ('pendiente', 'formulario_completado', 'confirmada', 'rechazada', 'cancelada');
    """)
    
    # Create table
    op.create_table(
        'intake_calls_simple',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('firma_id', sa.Integer(), nullable=False),
        sa.Column('twilio_call_sid', sa.String(length=100), nullable=True),
        sa.Column('numero_llamante', sa.String(length=20), nullable=False),
        sa.Column('idioma_detectado', sa.Enum('es', 'en', name='idioma_llamada'), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=True),
        sa.Column('tipo_caso', sa.Enum('familia', 'lesiones', 'laboral', 'inmobiliario', 'criminal', 'comercial', 'otro', name='tipo_caso_simple'), nullable=True),
        sa.Column('telefono_contacto', sa.String(length=20), nullable=True),
        sa.Column('nombre_completo', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('descripcion_caso', sa.Text(), nullable=True),
        sa.Column('fecha_cita', sa.DateTime(), nullable=True),
        sa.Column('abogado_asignado', sa.String(length=255), nullable=True),
        sa.Column('google_calendar_event_id', sa.String(length=255), nullable=True),
        sa.Column('estado', sa.Enum('pendiente', 'formulario_completado', 'confirmada', 'rechazada', 'cancelada', name='estado_consulta'), nullable=True),
        sa.Column('whatsapp_form_sent', sa.Boolean(), nullable=True),
        sa.Column('whatsapp_form_completed', sa.Boolean(), nullable=True),
        sa.Column('form_submission_id', sa.String(length=255), nullable=True),
        sa.Column('esta_activo', sa.Boolean(), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['firma_id'], ['firmas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indexes
    op.create_index('ix_intake_simple_firma', 'intake_calls_simple', ['firma_id'])
    op.create_index('ix_intake_simple_call_sid', 'intake_calls_simple', ['twilio_call_sid'], unique=True)
    op.create_index('ix_intake_simple_estado', 'intake_calls_simple', ['estado'])
    op.create_index('ix_intake_simple_fecha_cita', 'intake_calls_simple', ['fecha_cita'])


def downgrade() -> None:
    """Remove simplified intake_calls_simple table."""
    op.drop_index('ix_intake_simple_fecha_cita', table_name='intake_calls_simple')
    op.drop_index('ix_intake_simple_estado', table_name='intake_calls_simple')
    op.drop_index('ix_intake_simple_call_sid', table_name='intake_calls_simple')
    op.drop_index('ix_intake_simple_firma', table_name='intake_calls_simple')
    op.drop_table('intake_calls_simple')
    op.execute("DROP TYPE estado_consulta;")
    op.execute("DROP TYPE tipo_caso_simple;")