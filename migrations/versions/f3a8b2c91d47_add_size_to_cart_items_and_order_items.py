"""add size to cart_items and order_items

Revision ID: f3a8b2c91d47
Revises: 955f2f809ce7
Create Date: 2026-05-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f3a8b2c91d47'
down_revision = '955f2f809ce7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cart_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('size', sa.String(length=20), nullable=True))

    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('size', sa.String(length=20), nullable=True))


def downgrade():
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.drop_column('size')

    with op.batch_alter_table('cart_items', schema=None) as batch_op:
        batch_op.drop_column('size')
