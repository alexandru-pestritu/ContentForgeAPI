"""Added blog table and foreign keys for blogs

Revision ID: b1a12874ecdf
Revises: f15b5844dc69
Create Date: 2024-12-27 15:58:11.440875

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1a12874ecdf"
down_revision: Union[str, None] = "f15b5844dc69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "blogs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        ...
    )
    op.create_index(op.f("ix_blogs_id"), "blogs", ["id"], unique=False)

    # ARTICLES
    with op.batch_alter_table("articles", schema=None) as batch_op:
        batch_op.add_column(sa.Column("blog_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_articles_blog_id",
            "blogs",
            ["blog_id"],
            ["id"],
            ondelete="CASCADE"
        )

    # PRODUCTS
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("blog_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_products_blog_id",
            "blogs",
            ["blog_id"],
            ["id"],
            ondelete="CASCADE"
        )

    # PROMPTS
    with op.batch_alter_table("prompts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("blog_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_prompts_blog_id",
            "blogs",
            ["blog_id"],
            ["id"],
            ondelete="CASCADE"
        )

    # STOCK_CHECK_LOGS
    with op.batch_alter_table("stock_check_logs", schema=None) as batch_op:
        batch_op.add_column(sa.Column("blog_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_stockcheck_blog_id",
            "blogs",
            ["blog_id"],
            ["id"],
            ondelete="CASCADE"
        )

    # STORES
    with op.batch_alter_table("stores", schema=None) as batch_op:
        batch_op.add_column(sa.Column("blog_id", sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "fk_stores_blog_id",
            "blogs",
            ["blog_id"],
            ["id"],
            ondelete="CASCADE"
        )

def downgrade():
    # ARTICLES
    with op.batch_alter_table("articles", schema=None) as batch_op:
        batch_op.drop_constraint("fk_articles_blog_id", type_="foreignkey")
        batch_op.drop_column("blog_id")

    # PRODUCTS
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_constraint("fk_products_blog_id", type_="foreignkey")
        batch_op.drop_column("blog_id")

    # PROMPTS
    with op.batch_alter_table("prompts", schema=None) as batch_op:
        batch_op.drop_constraint("fk_prompts_blog_id", type_="foreignkey")
        batch_op.drop_column("blog_id")

    # STOCK_CHECK_LOGS
    with op.batch_alter_table("stock_check_logs", schema=None) as batch_op:
        batch_op.drop_constraint("fk_stockcheck_blog_id", type_="foreignkey")
        batch_op.drop_column("blog_id")

    # STORES
    with op.batch_alter_table("stores", schema=None) as batch_op:
        batch_op.drop_constraint("fk_stores_blog_id", type_="foreignkey")
        batch_op.drop_column("blog_id")

    op.drop_index(op.f("ix_blogs_id"), table_name="blogs")
    op.drop_table("blogs")

