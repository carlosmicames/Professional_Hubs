"""create core tables

Revision ID: 002
Revises: 001
Create Date: 2025-01-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create core tables for Professional Hubs."""
    
    # Create enum types
    estado_asunto_enum = postgresql.ENUM(
        'ACTIVO', 'CERRADO', 'PENDIENTE', 'ARCHIVADO',
        name='estadoasunto',
        create_type=False
    )
    estado_asunto_enum.create(op.get_bind(), checkfirst=True)
    
    tipo_relacion_enum = postgresql.ENUM(
        'DEMANDANTE', 'DEMANDADO', 'PARTE_CONTRARIA', 'CO_DEMANDADO', 
        'CONYUGE', 'SUBSIDIARIA', 'EMPRESA_MATRIZ',
        name='tiporelacion',
        create_type=False
    )
    tipo_relacion_enum.create(op.get_bind(), checkfirst=True)
    
    # Create firmas table
    op.create_table(
        'firmas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False, comment='Nombre del bufete'),
        sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Soft delete flag'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_firmas_id', 'firmas', ['id'], unique=False)
    
    # Create clientes table
    op.create_table(
        'clientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('firma_id', sa.Integer(), nullable=False, comment='ID del bufete (multi-tenant)'),
        sa.Column('nombre', sa.String(length=100), nullable=True, comment='Nombre del cliente individual'),
        sa.Column('apellido', sa.String(length=100), nullable=True, comment='Primer apellido del cliente individual'),
        sa.Column('segundo_apellido', sa.String(length=100), nullable=True, comment='Segundo apellido (común en Puerto Rico)'),
        sa.Column('nombre_empresa', sa.String(length=255), nullable=True, comment='Nombre de empresa/corporación'),
        sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Soft delete flag'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['firma_id'], ['firmas.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_clientes_id', 'clientes', ['id'], unique=False)
    op.create_index('ix_clientes_firma_id', 'clientes', ['firma_id'], unique=False)
    op.create_index('ix_clientes_nombre_apellido', 'clientes', ['nombre', 'apellido'], unique=False)
    op.create_index('ix_clientes_nombre_apellido_completo', 'clientes', ['nombre', 'apellido', 'segundo_apellido'], unique=False)
    op.create_index('ix_clientes_nombre_empresa', 'clientes', ['nombre_empresa'], unique=False)
    op.create_index('ix_clientes_firma_activo', 'clientes', ['firma_id', 'esta_activo'], unique=False)
    
    # Create asuntos table
    op.create_table(
        'asuntos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False, comment='ID del cliente principal'),
        sa.Column('nombre_asunto', sa.String(length=500), nullable=False, comment='Nombre o descripción del asunto'),
        sa.Column('fecha_apertura', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE'), comment='Fecha de apertura'),
        sa.Column('estado', sa.Enum('ACTIVO', 'CERRADO', 'PENDIENTE', 'ARCHIVADO', name='estadoasunto'), nullable=False, server_default='ACTIVO', comment='Estado actual del asunto'),
        sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Soft delete flag'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_asuntos_id', 'asuntos', ['id'], unique=False)
    op.create_index('ix_asuntos_cliente_id', 'asuntos', ['cliente_id'], unique=False)
    op.create_index('ix_asuntos_cliente_estado', 'asuntos', ['cliente_id', 'estado'], unique=False)
    op.create_index('ix_asuntos_fecha_apertura', 'asuntos', ['fecha_apertura'], unique=False)
    
    # Create partes_relacionadas table
    op.create_table(
        'partes_relacionadas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asunto_id', sa.Integer(), nullable=False, comment='ID del asunto relacionado'),
        sa.Column('nombre', sa.String(length=255), nullable=False, comment='Nombre de la parte relacionada'),
        sa.Column('tipo_relacion', sa.Enum('DEMANDANTE', 'DEMANDADO', 'PARTE_CONTRARIA', 'CO_DEMANDADO', 'CONYUGE', 'SUBSIDIARIA', 'EMPRESA_MATRIZ', name='tiporelacion'), nullable=False, comment='Tipo de relación con el asunto'),
        sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Soft delete flag'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['asunto_id'], ['asuntos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_partes_relacionadas_id', 'partes_relacionadas', ['id'], unique=False)
    op.create_index('ix_partes_relacionadas_asunto_id', 'partes_relacionadas', ['asunto_id'], unique=False)
    op.create_index('ix_partes_nombre', 'partes_relacionadas', ['nombre'], unique=False)
    op.create_index('ix_partes_asunto_activo', 'partes_relacionadas', ['asunto_id', 'esta_activo'], unique=False)


def downgrade() -> None:
    """Drop all core tables."""
    op.drop_index('ix_partes_asunto_activo', table_name='partes_relacionadas')
    op.drop_index('ix_partes_nombre', table_name='partes_relacionadas')
    op.drop_index('ix_partes_relacionadas_asunto_id', table_name='partes_relacionadas')
    op.drop_index('ix_partes_relacionadas_id', table_name='partes_relacionadas')
    op.drop_table('partes_relacionadas')
    
    op.drop_index('ix_asuntos_fecha_apertura', table_name='asuntos')
    op.drop_index('ix_asuntos_cliente_estado', table_name='asuntos')
    op.drop_index('ix_asuntos_cliente_id', table_name='asuntos')
    op.drop_index('ix_asuntos_id', table_name='asuntos')
    op.drop_table('asuntos')
    
    op.drop_index('ix_clientes_firma_activo', table_name='clientes')
    op.drop_index('ix_clientes_nombre_empresa', table_name='clientes')
    op.drop_index('ix_clientes_nombre_apellido_completo', table_name='clientes')
    op.drop_index('ix_clientes_nombre_apellido', table_name='clientes')
    op.drop_index('ix_clientes_firma_id', table_name='clientes')
    op.drop_index('ix_clientes_id', table_name='clientes')
    op.drop_table('clientes')
    
    op.drop_index('ix_firmas_id', table_name='firmas')
    op.drop_table('firmas')
    
    sa.Enum(name='tiporelacion').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='estadoasunto').drop(op.get_bind(), checkfirst=True)