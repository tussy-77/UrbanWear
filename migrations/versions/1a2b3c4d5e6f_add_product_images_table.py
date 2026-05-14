"""add product_images table for multiple product images

Revision ID: 1a2b3c4d5e6f
Revises: f3a8b2c91d47
Create Date: 2026-05-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '1a2b3c4d5e6f'
down_revision = 'f3a8b2c91d47'
branch_labels = None
depends_on = None


def upgrade():
    # Crear la tabla product_images
    op.create_table(
        'product_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.current_timestamp(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índice para búsquedas rápidas
    op.create_index('idx_product_images_product', 'product_images', ['product_id'])


def downgrade():
    # Eliminar índice
    op.drop_index('idx_product_images_product', table_name='product_images')
    
    # Eliminar tabla
    op.drop_table('product_images')
