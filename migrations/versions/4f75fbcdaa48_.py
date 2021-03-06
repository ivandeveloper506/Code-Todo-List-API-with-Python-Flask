"""empty message

Revision ID: 4f75fbcdaa48
Revises: ed4be5643176
Create Date: 2021-03-30 04:30:40.299430

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4f75fbcdaa48'
down_revision = 'ed4be5643176'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todo', sa.Column('label1', sa.String(length=250), nullable=False))
    op.drop_column('todo', 'label')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('todo', sa.Column('label', mysql.VARCHAR(length=250), nullable=False))
    op.drop_column('todo', 'label1')
    # ### end Alembic commands ###
