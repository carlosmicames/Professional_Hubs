"""create core tables

Revision ID: 001
Revises: None
Create Date: 2025-01-15

BULLETPROOF VERSION: Handles existing enums, existing tables, partial migrations.
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
    """Check if a table exists in the database."""
    conn = op.get_bind()
    result = conn.execute(text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def enum_exists(enum_name: str) -> bool:
    """Check if an enum type exists in the database."""
    conn = op.get_bind()
    result = conn.execute(text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :name)"
    ), {"name": enum_name})
    return result.scalar()


def create_enum_safe(enum_name: str, values: list):
    """Create enum only if it doesn't exist."""
    if not enum_exists(enum_name):
        conn = op.get_bind()
        values_str = ", ".join([f"'{v}'" for v in values])
        conn.execute(text(f"CREATE TYPE {enum_name} AS ENUM ({values_str})"))
        print(f"  ✓ Created enum: {enum_name}")
    else:
        print(f"  → Enum already exists: {enum_name} (skipping)")


def upgrade() -> None:
    """Create core tables for Professional Hubs."""
    
    print("\n=== Professional Hubs Migration 001 ===\n")
    
    # Step 1: Create enums safely
    print("Creating enum types...")
    create_enum_safe('estadoasunto', ['ACTIVO', 'CERRADO', 'PENDIENTE', 'ARCHIVADO'])
    create_enum_safe('tiporelacion', ['DEMANDANTE', 'DEMANDADO', 'PARTE_CONTRARIA', 'CO_DEMANDADO', 'CONYUGE', 'SUBSIDIARIA', 'EMPRESA_MATRIZ'])
    
    # Step 2: Create tables (skip if exists)
    print("\nCreating tables...")
    
    # FIRMAS
    if not table_exists('firmas'):
        op.create_table(
            'firmas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nombre', sa.String(length=255), nullable=False),
            sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_firmas_id', 'firmas', ['id'], unique=False)
        print("  ✓ Created table: firmas")
    else:
        print("  → Table already exists: firmas (skipping)")
    
    # CLIENTES
    if not table_exists('clientes'):
        op.create_table(
            'clientes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('firma_id', sa.Integer(), nullable=False),
            sa.Column('nombre', sa.String(length=100), nullable=True),
            sa.Column('apellido', sa.String(length=100), nullable=True),
            sa.Column('segundo_apellido', sa.String(length=100), nullable=True),
            sa.Column('nombre_empresa', sa.String(length=255), nullable=True),
            sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['firma_id'], ['firmas.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_clientes_id', 'clientes', ['id'], unique=False)
        op.create_index('ix_clientes_firma_id', 'clientes', ['firma_id'], unique=False)
        op.create_index('ix_clientes_nombre_apellido', 'clientes', ['nombre', 'apellido'], unique=False)
        op.create_index('ix_clientes_nombre_empresa', 'clientes', ['nombre_empresa'], unique=False)
        op.create_index('ix_clientes_firma_activo', 'clientes', ['firma_id', 'esta_activo'], unique=False)
        print("  ✓ Created table: clientes")
    else:
        print("  → Table already exists: clientes (skipping)")
    
    # ASUNTOS
    if not table_exists('asuntos'):
        op.execute(text("""
            CREATE TABLE asuntos (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
                nombre_asunto VARCHAR(500) NOT NULL,
                fecha_apertura DATE NOT NULL DEFAULT CURRENT_DATE,
                estado estadoasunto NOT NULL DEFAULT 'ACTIVO',
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_asuntos_id ON asuntos(id)"))
        op.execute(text("CREATE INDEX ix_asuntos_cliente_id ON asuntos(cliente_id)"))
        op.execute(text("CREATE INDEX ix_asuntos_cliente_estado ON asuntos(cliente_id, estado)"))
        print("  ✓ Created table: asuntos")
    else:
        print("  → Table already exists: asuntos (skipping)")
    
    # PARTES_RELACIONADAS
    if not table_exists('partes_relacionadas'):
        op.execute(text("""
            CREATE TABLE partes_relacionadas (
                id SERIAL PRIMARY KEY,
                asunto_id INTEGER NOT NULL REFERENCES asuntos(id) ON DELETE CASCADE,
                nombre VARCHAR(255) NOT NULL,
                tipo_relacion tiporelacion NOT NULL,
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_partes_relacionadas_id ON partes_relacionadas(id)"))
        op.execute(text("CREATE INDEX ix_partes_relacionadas_asunto_id ON partes_relacionadas(asunto_id)"))
        op.execute(text("CREATE INDEX ix_partes_nombre ON partes_relacionadas(nombre)"))
        print("  ✓ Created table: partes_relacionadas")
    else:
        print("  → Table already exists: partes_relacionadas (skipping)")
    
    print("\n=== Migration 001 Complete ===\n")


def downgrade() -> None:
    """Drop all core tables."""
    conn = op.get_bind()
    
    # Drop tables in reverse order (respecting foreign keys)
    for table in ['partes_relacionadas', 'asuntos', 'clientes', 'firmas']:
        if table_exists(table):
            conn.execute(text(f"DROP TABLE {table} CASCADE"))
            print(f"  Dropped table: {table}")
    
    # Drop enums
    for enum in ['tiporelacion', 'estadoasunto']:
        if enum_exists(enum):
            conn.execute(text(f"DROP TYPE {enum}"))
            print(f"  Dropped enum: {enum}")