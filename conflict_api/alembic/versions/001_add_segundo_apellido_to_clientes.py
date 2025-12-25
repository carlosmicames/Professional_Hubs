"""add segundo_apellido to clientes

Revision ID: 001
Revises:
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add segundo_apellido column to clientes table."""
    # Add segundo_apellido column
    op.add_column(
        'clientes',
        sa.Column('segundo_apellido', sa.String(length=100), nullable=True, comment='Segundo apellido (común en Puerto Rico)')
    )

    # Create composite index for full name search
    op.create_index(
        'ix_clientes_nombre_apellido_completo',
        'clientes',
        ['nombre', 'apellido', 'segundo_apellido'],
        unique=False
    )


def downgrade() -> None:
    """Remove segundo_apellido column from clientes table."""
    # Drop the composite index first
    op.drop_index('ix_clientes_nombre_apellido_completo', table_name='clientes')

    # Drop the column
    op.drop_column('clientes', 'segundo_apellido')
