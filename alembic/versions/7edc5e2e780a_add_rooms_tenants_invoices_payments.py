"""add_rooms_tenants_invoices_payments

Revision ID: 7edc5e2e780a
Revises: 8ac67e0e9d38
Create Date: 2026-02-27 08:58:33.492943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7edc5e2e780a'
down_revision: Union[str, Sequence[str], None] = '8ac67e0e9d38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Create rooms table first (it's referenced by other tables)
    op.create_table('rooms',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Step 2: Create tenants table (references rooms)
    op.create_table('tenants',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('id_card', sa.String(length=100), nullable=True),
    sa.Column('photo', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('check_in_date', sa.DateTime(), nullable=True),
    sa.Column('check_out_date', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('room_id')
    )
    
    # Step 3: Create invoices table (references rooms and tenants)
    op.create_table('invoices',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('room_id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.Integer(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('amount_paid', sa.Float(), nullable=True),
    sa.Column('due_date', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'paid', 'late', name='invoicestatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    
    # Step 4: Create payments table (references invoices)
    op.create_table('payments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('invoice_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'completed', 'failed', name='paymentstatus'), nullable=True),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Drop in reverse order (child tables first)
    op.drop_table('payments')
    op.drop_table('invoices')
    op.drop_table('tenants')
    op.drop_table('rooms')
    # ### end Alembic commands ###
