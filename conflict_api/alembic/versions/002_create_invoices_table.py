"""create invoices table

Revision ID: 002
Revises: 001
Create Date: 2025-01-15

BULLETPROOF VERSION: Handles existing tables.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    conn = op.get_bind()
    result = conn.execute(text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :name)"
    ), {"name": table_name})
    return result.scalar()


def upgrade() -> None:
    """Create invoices table for billing automation."""
    
    print("\n=== Professional Hubs Migration 002 ===\n")
    
    if not table_exists('invoices'):
        op.create_table(
            'invoices',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('client_id', sa.Integer(), nullable=False),
            sa.Column('invoice_number', sa.String(length=50), nullable=False),
            sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column('due_date', sa.Date(), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
            sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.ForeignKeyConstraint(['client_id'], ['clientes.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_invoices_id', 'invoices', ['id'], unique=False)
        op.create_index('ix_invoices_client_id', 'invoices', ['client_id'], unique=False)
        op.create_index('ix_invoices_invoice_number', 'invoices', ['invoice_number'], unique=True)
        op.create_index('ix_invoices_due_date', 'invoices', ['due_date'], unique=False)
        op.create_index('ix_invoices_status', 'invoices', ['status'], unique=False)
        print("  ✓ Created table: invoices")
    else:
        print("  → Table already exists: invoices (skipping)")
    
    print("\n=== Migration 002 Complete ===\n")


def downgrade() -> None:
    """Drop invoices table."""
    if table_exists('invoices'):
        op.drop_index('ix_invoices_status', table_name='invoices')
        op.drop_index('ix_invoices_due_date', table_name='invoices')
        op.drop_index('ix_invoices_invoice_number', table_name='invoices')
        op.drop_index('ix_invoices_client_id', table_name='invoices')
        op.drop_index('ix_invoices_id', table_name='invoices')
        op.drop_table('invoices')