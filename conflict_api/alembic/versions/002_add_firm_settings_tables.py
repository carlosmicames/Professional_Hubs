"""add firm settings tables

Revision ID: 002
Revises: 001
Create Date: 2025-01-16

This migration adds:
- New columns to firmas table (direccion, direccion_postal, telefono)
- New columns to clientes table (direccion, direccion_postal, has_late_invoices, has_potential_conflict)
- perfiles table (profile settings)
- estudios table (educational background)
- areas_practica table (practice areas)
- ubicaciones table (geographic location)
- planes table (subscription plans)
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    conn = op.get_bind()
    result = conn.execute(text(
        """SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = :table AND column_name = :column
        )"""
    ), {"table": table_name, "column": column_name})
    return result.scalar()


def table_exists(table_name: str) -> bool:
    """Check if a table exists."""
    conn = op.get_bind()
    result = conn.execute(text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def upgrade() -> None:
    """Add firm settings tables and columns."""

    print("\n" + "=" * 60)
    print("Professional Hubs - Firm Settings Migration")
    print("=" * 60 + "\n")

    # ==========================================================================
    # UPDATE FIRMAS TABLE - Add new columns
    # ==========================================================================
    if not column_exists('firmas', 'direccion'):
        op.execute(text("ALTER TABLE firmas ADD COLUMN direccion VARCHAR(500)"))
        print("  + Added: firmas.direccion")

    if not column_exists('firmas', 'direccion_postal'):
        op.execute(text("ALTER TABLE firmas ADD COLUMN direccion_postal VARCHAR(500)"))
        print("  + Added: firmas.direccion_postal")

    if not column_exists('firmas', 'telefono'):
        op.execute(text("ALTER TABLE firmas ADD COLUMN telefono VARCHAR(50)"))
        print("  + Added: firmas.telefono")

    # Make firmas.nombre nullable for MVP (was NOT NULL)
    op.execute(text("ALTER TABLE firmas ALTER COLUMN nombre DROP NOT NULL"))
    print("  + Modified: firmas.nombre is now nullable")

    # ==========================================================================
    # UPDATE CLIENTES TABLE - Add new columns
    # ==========================================================================
    if not column_exists('clientes', 'direccion'):
        op.execute(text("ALTER TABLE clientes ADD COLUMN direccion VARCHAR(500) NOT NULL DEFAULT ''"))
        print("  + Added: clientes.direccion")

    if not column_exists('clientes', 'direccion_postal'):
        op.execute(text("ALTER TABLE clientes ADD COLUMN direccion_postal VARCHAR(500)"))
        print("  + Added: clientes.direccion_postal")

    if not column_exists('clientes', 'has_late_invoices'):
        op.execute(text("ALTER TABLE clientes ADD COLUMN has_late_invoices BOOLEAN NOT NULL DEFAULT false"))
        print("  + Added: clientes.has_late_invoices")

    if not column_exists('clientes', 'has_potential_conflict'):
        op.execute(text("ALTER TABLE clientes ADD COLUMN has_potential_conflict BOOLEAN NOT NULL DEFAULT false"))
        print("  + Added: clientes.has_potential_conflict")

    # Make existing nullable columns required for new records
    # Note: We set defaults to empty string so existing records are valid
    if column_exists('clientes', 'nombre'):
        op.execute(text("ALTER TABLE clientes ALTER COLUMN nombre SET NOT NULL"))
        op.execute(text("UPDATE clientes SET nombre = '' WHERE nombre IS NULL"))

    if column_exists('clientes', 'apellido'):
        op.execute(text("UPDATE clientes SET apellido = '' WHERE apellido IS NULL"))
        op.execute(text("ALTER TABLE clientes ALTER COLUMN apellido SET NOT NULL"))

    if column_exists('clientes', 'email'):
        op.execute(text("UPDATE clientes SET email = '' WHERE email IS NULL"))
        op.execute(text("ALTER TABLE clientes ALTER COLUMN email SET NOT NULL"))

    if column_exists('clientes', 'telefono'):
        op.execute(text("UPDATE clientes SET telefono = '' WHERE telefono IS NULL"))
        op.execute(text("ALTER TABLE clientes ALTER COLUMN telefono SET NOT NULL"))

    # Add email index if not exists
    op.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_clientes_email ON clientes(email)
    """))
    print("  + Index: ix_clientes_email")

    # ==========================================================================
    # CREATE PERFILES TABLE
    # ==========================================================================
    if not table_exists('perfiles'):
        op.execute(text("""
            CREATE TABLE perfiles (
                id SERIAL PRIMARY KEY,
                firma_id INTEGER NOT NULL UNIQUE REFERENCES firmas(id) ON DELETE CASCADE,
                numero_rua INTEGER,
                direccion VARCHAR(500),
                direccion_postal VARCHAR(500),
                telefono_celular VARCHAR(50),
                telefono VARCHAR(50),
                numero_colegiado VARCHAR(100),
                instagram VARCHAR(255),
                facebook VARCHAR(255),
                linkedin VARCHAR(255),
                twitter VARCHAR(255),
                tarifa_entrevista_inicial_usd NUMERIC(10, 2),
                formulario_contacto VARCHAR(500),
                descripcion_perfil_profesional TEXT,
                logo_empresa_url VARCHAR(500),
                firma_abogado_url VARCHAR(500),
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_perfiles_id ON perfiles(id)"))
        op.execute(text("CREATE INDEX ix_perfiles_firma_id ON perfiles(firma_id)"))
        print("  + Created: perfiles")
    else:
        print("  - Exists: perfiles")

    # ==========================================================================
    # CREATE ESTUDIOS TABLE
    # ==========================================================================
    if not table_exists('estudios'):
        op.execute(text("""
            CREATE TABLE estudios (
                id SERIAL PRIMARY KEY,
                firma_id INTEGER NOT NULL UNIQUE REFERENCES firmas(id) ON DELETE CASCADE,
                universidad VARCHAR(255),
                ano_graduacion VARCHAR(50),
                escuela_derecho VARCHAR(255),
                ano_graduacion_derecho VARCHAR(50),
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_estudios_id ON estudios(id)"))
        op.execute(text("CREATE INDEX ix_estudios_firma_id ON estudios(firma_id)"))
        print("  + Created: estudios")
    else:
        print("  - Exists: estudios")

    # ==========================================================================
    # CREATE AREAS_PRACTICA TABLE
    # ==========================================================================
    if not table_exists('areas_practica'):
        op.execute(text("""
            CREATE TABLE areas_practica (
                id SERIAL PRIMARY KEY,
                firma_id INTEGER NOT NULL UNIQUE REFERENCES firmas(id) ON DELETE CASCADE,
                areas JSONB DEFAULT '[]'::jsonb,
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_areas_practica_id ON areas_practica(id)"))
        op.execute(text("CREATE INDEX ix_areas_practica_firma_id ON areas_practica(firma_id)"))
        print("  + Created: areas_practica")
    else:
        print("  - Exists: areas_practica")

    # ==========================================================================
    # CREATE UBICACIONES TABLE
    # ==========================================================================
    if not table_exists('ubicaciones'):
        op.execute(text("""
            CREATE TABLE ubicaciones (
                id SERIAL PRIMARY KEY,
                firma_id INTEGER NOT NULL UNIQUE REFERENCES firmas(id) ON DELETE CASCADE,
                pais VARCHAR(100) DEFAULT 'Puerto Rico',
                municipio VARCHAR(100),
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_ubicaciones_id ON ubicaciones(id)"))
        op.execute(text("CREATE INDEX ix_ubicaciones_firma_id ON ubicaciones(firma_id)"))
        print("  + Created: ubicaciones")
    else:
        print("  - Exists: ubicaciones")

    # ==========================================================================
    # CREATE PLANES TABLE
    # ==========================================================================
    if not table_exists('planes'):
        op.execute(text("""
            CREATE TABLE planes (
                id SERIAL PRIMARY KEY,
                firma_id INTEGER NOT NULL UNIQUE REFERENCES firmas(id) ON DELETE CASCADE,
                selected_plan VARCHAR(50) DEFAULT 'Basico',
                trial_days INTEGER DEFAULT 14,
                plan_status VARCHAR(50) DEFAULT 'trial',
                stripe_placeholder VARCHAR(255),
                esta_activo BOOLEAN NOT NULL DEFAULT true,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        op.execute(text("CREATE INDEX ix_planes_id ON planes(id)"))
        op.execute(text("CREATE INDEX ix_planes_firma_id ON planes(firma_id)"))
        print("  + Created: planes")
    else:
        print("  - Exists: planes")

    print("\n" + "=" * 60)
    print("Migration Complete!")
    print("=" * 60 + "\n")


def downgrade() -> None:
    """Remove firm settings tables and columns."""
    conn = op.get_bind()

    # Drop new tables
    tables = ['planes', 'ubicaciones', 'areas_practica', 'estudios', 'perfiles']
    for table in tables:
        if table_exists(table):
            conn.execute(text(f"DROP TABLE {table} CASCADE"))
            print(f"  - Dropped: {table}")

    # Remove columns from clientes
    columns_to_remove = ['direccion', 'direccion_postal', 'has_late_invoices', 'has_potential_conflict']
    for col in columns_to_remove:
        if column_exists('clientes', col):
            conn.execute(text(f"ALTER TABLE clientes DROP COLUMN {col}"))
            print(f"  - Dropped: clientes.{col}")

    # Remove columns from firmas
    firmas_cols = ['direccion', 'direccion_postal', 'telefono']
    for col in firmas_cols:
        if column_exists('firmas', col):
            conn.execute(text(f"ALTER TABLE firmas DROP COLUMN {col}"))
            print(f"  - Dropped: firmas.{col}")
