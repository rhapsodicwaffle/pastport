"""Initial migration

Revision ID: 821381f444b5
Revises: 
Create Date: 2025-05-07 00:26:12.828553

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '821381f444b5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog_post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('author', sa.String(length=150), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookmark',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('item_type', sa.String(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('collaborative_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room_id', sa.String(length=8), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('username'),
    sa.UniqueConstraint('email')
    )
    op.create_table('capsule',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner_username', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('expiry_date', sa.Date(), nullable=True),
    sa.Column('delivery_date', sa.Date(), nullable=True),
    sa.Column('sent', sa.Boolean(), nullable=True),
    sa.Column('encryption', sa.String(length=50), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('accessibility', sa.String(length=20), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('tags', sa.String(length=255), nullable=True),
    sa.Column('recipient_email', sa.String(length=120), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('is_memorial', sa.Boolean(), nullable=True),
    sa.Column('verifier_emails', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('verifier_confirmations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('recipient_emails', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.ForeignKeyConstraint(['owner_username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=True),
    sa.Column('capsule_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['capsule_id'], ['capsule.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('capsule_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['capsule_id'], ['capsule.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('capsule_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(length=255), nullable=False),
    sa.Column('read', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['capsule_id'], ['capsule.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    op.drop_table('like')
    op.drop_table('file')
    op.drop_table('capsule')
    op.drop_table('user')
    op.drop_table('collaborative_message')
    op.drop_table('bookmark')
    op.drop_table('blog_post')
    # ### end Alembic commands ###
