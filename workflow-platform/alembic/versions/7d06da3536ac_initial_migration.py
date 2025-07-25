"""Initial migration

Revision ID: 7d06da3536ac
Revises: 
Create Date: 2025-07-26 18:26:58.476880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d06da3536ac'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_index('idx_users_created_at', 'users', ['created_at'], unique=False)
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_status', 'users', ['status'], unique=False)
    op.create_index('idx_users_username', 'users', ['username'], unique=False)
    op.create_table('email_verification_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index('idx_email_verification_expires', 'email_verification_tokens', ['expires_at'], unique=False)
    op.create_index('idx_email_verification_token', 'email_verification_tokens', ['token'], unique=False)
    op.create_index('idx_email_verification_verified', 'email_verification_tokens', ['is_verified'], unique=False)
    op.create_table('password_reset_tokens',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=255), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_used', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('token')
    )
    op.create_index('idx_password_reset_expires', 'password_reset_tokens', ['expires_at'], unique=False)
    op.create_index('idx_password_reset_token', 'password_reset_tokens', ['token'], unique=False)
    op.create_index('idx_password_reset_used', 'password_reset_tokens', ['is_used'], unique=False)
    op.create_table('user_login_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('login_status', sa.String(length=20), nullable=False),
    sa.Column('failure_reason', sa.String(length=100), nullable=True),
    sa.Column('location_info', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_login_history_created_at', 'user_login_history', ['created_at'], unique=False)
    op.create_index('idx_login_history_ip', 'user_login_history', ['ip_address'], unique=False)
    op.create_index('idx_login_history_user_id', 'user_login_history', ['user_id'], unique=False)
    op.create_table('user_profiles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('display_name', sa.String(length=100), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('timezone', sa.String(length=50), nullable=False),
    sa.Column('language', sa.String(length=10), nullable=False),
    sa.Column('notification_preferences', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_table('user_sessions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('session_token', sa.String(length=255), nullable=False),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('refresh_expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('device_info', sa.JSON(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('refresh_token'),
    sa.UniqueConstraint('session_token')
    )
    op.create_index('idx_user_sessions_active', 'user_sessions', ['is_active'], unique=False)
    op.create_index('idx_user_sessions_expires', 'user_sessions', ['expires_at'], unique=False)
    op.create_index('idx_user_sessions_token', 'user_sessions', ['session_token'], unique=False)
    op.create_index('idx_user_sessions_user_id', 'user_sessions', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_user_sessions_user_id', table_name='user_sessions')
    op.drop_index('idx_user_sessions_token', table_name='user_sessions')
    op.drop_index('idx_user_sessions_expires', table_name='user_sessions')
    op.drop_index('idx_user_sessions_active', table_name='user_sessions')
    op.drop_table('user_sessions')
    op.drop_table('user_profiles')
    op.drop_index('idx_login_history_user_id', table_name='user_login_history')
    op.drop_index('idx_login_history_ip', table_name='user_login_history')
    op.drop_index('idx_login_history_created_at', table_name='user_login_history')
    op.drop_table('user_login_history')
    op.drop_index('idx_password_reset_used', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_token', table_name='password_reset_tokens')
    op.drop_index('idx_password_reset_expires', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
    op.drop_index('idx_email_verification_verified', table_name='email_verification_tokens')
    op.drop_index('idx_email_verification_token', table_name='email_verification_tokens')
    op.drop_index('idx_email_verification_expires', table_name='email_verification_tokens')
    op.drop_table('email_verification_tokens')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_status', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
