"""create invoices table

Revision ID: 003
Revises: 002
Create Date: 2025-01-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create invoices table for billing automation."""
    
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False, comment='ID del cliente'),
        sa.Column('invoice_number', sa.String(length=50), nullable=False, comment='Número de factura'),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='Monto de la factura'),
        sa.Column('due_date', sa.Date(), nullable=False, comment='Fecha de vencimiento'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending', comment='Estado: pending, paid, cancelled'),
        sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Soft delete flag'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['client_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_invoices_id', 'invoices', ['id'], unique=False)
    op.create_index('ix_invoices_client_id', 'invoices', ['client_id'], unique=False)
    op.create_index('ix_invoices_invoice_number', 'invoices', ['invoice_number'], unique=True)
    op.create_index('ix_invoices_due_date', 'invoices', ['due_date'], unique=False)
    op.create_index('ix_invoices_status', 'invoices', ['status'], unique=False)


def downgrade() -> None:
    """Drop invoices table."""
    op.drop_index('ix_invoices_status', table_name='invoices')
    op.drop_index('ix_invoices_due_date', table_name='invoices')
    op.drop_index('ix_invoices_invoice_number', table_name='invoices')
    op.drop_index('ix_invoices_client_id', table_name='invoices')
    op.drop_index('ix_invoices_id', table_name='invoices')
    op.drop_table('invoices')