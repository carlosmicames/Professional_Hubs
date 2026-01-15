"""add billing communication logs

Revision ID: 004
Revises: 003
Create Date: 2025-01-06

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add billing_communication_logs table."""
    
    # Create enum types
    communication_type_enum = postgresql.ENUM(
        'EMAIL', 'SMS', 'PHONE_CALL', 'LETTER',
        name='communication_type',
        create_type=False
    )
    communication_type_enum.create(op.get_bind(), checkfirst=True)
    
    communication_status_enum = postgresql.ENUM(
        'SENT', 'DELIVERED', 'FAILED', 'BOUNCED', 'READ',
        name='communication_status',
        create_type=False
    )
    communication_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create billing_communication_logs table
    op.create_table(
        'billing_communication_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False, comment='ID de la factura'),
        sa.Column('type', sa.Enum('EMAIL', 'SMS', 'PHONE_CALL', 'LETTER', name='communication_type'), nullable=False, comment='Tipo de comunicación (email/sms)'),
        sa.Column('message_body', sa.Text(), nullable=False, comment='Contenido del mensaje enviado'),
        sa.Column('subject', sa.String(length=500), nullable=True, comment='Asunto (para emails)'),
        sa.Column('status', sa.Enum('SENT', 'DELIVERED', 'FAILED', 'BOUNCED', 'READ', name='communication_status'), nullable=False, comment='Estado de la comunicación'),
        sa.Column('sent_at', sa.DateTime(), nullable=False, comment='Fecha/hora de envío'),
        sa.Column('delivered_at', sa.DateTime(), nullable=True, comment='Fecha/hora de entrega'),
        sa.Column('read_at', sa.DateTime(), nullable=True, comment='Fecha/hora de lectura (si disponible)'),
        sa.Column('external_id', sa.String(length=255), nullable=True, comment='ID de Twilio/Postmark'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='Mensaje de error si falló'),
        sa.Column('days_overdue_when_sent', sa.Integer(), nullable=False, comment='Días de atraso al enviar'),
        sa.Column('reminder_sequence', sa.Integer(), nullable=False, comment='Número en secuencia (1=primer recordatorio)'),
        sa.Column('esta_activo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Soft delete flag'),
        sa.Column('creado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_billing_comms_invoice_date', 'billing_communication_logs', ['invoice_id', 'sent_at'], unique=False)
    op.create_index('ix_billing_comms_status', 'billing_communication_logs', ['status'], unique=False)
    op.create_index('ix_billing_comms_type_date', 'billing_communication_logs', ['type', 'sent_at'], unique=False)
    op.create_index('ix_billing_communication_logs_id', 'billing_communication_logs', ['id'], unique=False)


def downgrade() -> None:
    """Remove billing_communication_logs table."""
    op.drop_index('ix_billing_communication_logs_id', table_name='billing_communication_logs')
    op.drop_index('ix_billing_comms_type_date', table_name='billing_communication_logs')
    op.drop_index('ix_billing_comms_status', table_name='billing_communication_logs')
    op.drop_index('ix_billing_comms_invoice_date', table_name='billing_communication_logs')
    op.drop_table('billing_communication_logs')
    
    # Drop enum types
    sa.Enum(name='communication_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='communication_type').drop(op.get_bind(), checkfirst=True)