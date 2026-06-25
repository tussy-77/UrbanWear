"""add magic login sessions table

Revision ID: b3c5d8e1f2a9
Revises: 4b59fd0d695b
Create Date: 2026-06-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b3c5d8e1f2a9'
down_revision = '4b59fd0d695b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'magic_login_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=64), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('user_name', sa.String(length=150), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token'),
    )
    op.create_index(
        op.f('ix_magic_login_sessions_session_token'),
        'magic_login_sessions', ['session_token'], unique=True,
    )


def downgrade():
    op.drop_index(op.f('ix_magic_login_sessions_session_token'), table_name='magic_login_sessions')
    op.drop_table('magic_login_sessions')
