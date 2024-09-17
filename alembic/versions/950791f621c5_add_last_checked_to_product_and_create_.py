"""add last_checked to Product and create StockCheckLog

Revision ID: 950791f621c5
Revises: e3b73592a6d4
Create Date: 2024-09-17 19:54:31.123934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '950791f621c5'
down_revision: Union[str, None] = 'e3b73592a6d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stock_check_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('check_time', sa.DateTime(), nullable=True),
    sa.Column('duration', sa.Float(), nullable=False),
    sa.Column('in_stock_count', sa.Integer(), nullable=False),
    sa.Column('out_of_stock_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stock_check_logs_id'), 'stock_check_logs', ['id'], unique=False)
    op.add_column('products', sa.Column('last_checked', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'last_checked')
    op.drop_index(op.f('ix_stock_check_logs_id'), table_name='stock_check_logs')
    op.drop_table('stock_check_logs')
    # ### end Alembic commands ###
