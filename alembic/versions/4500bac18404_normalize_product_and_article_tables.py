"""Normalize product and article tables

Revision ID: 4500bac18404
Revises: 950791f621c5
Create Date: 2024-12-17 17:08:50.624358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4500bac18404'
down_revision: Union[str, None] = '950791f621c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('wp_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('wp_id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_table('article_category_association',
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('article_id', 'category_id')
    )
    op.create_table('article_faqs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('question', sa.String(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_faqs_id'), 'article_faqs', ['id'], unique=False)
    op.create_table('article_product_association',
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('article_id', 'product_id')
    )
    op.create_table('article_seo_keywords',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('keyword', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_seo_keywords_id'), 'article_seo_keywords', ['id'], unique=False)
    op.create_table('product_affiliate_urls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_affiliate_urls_id'), 'product_affiliate_urls', ['id'], unique=False)
    op.create_table('product_cons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_cons_id'), 'product_cons', ['id'], unique=False)
    op.create_table('product_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('wp_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_images_id'), 'product_images', ['id'], unique=False)
    op.create_table('product_pros',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_pros_id'), 'product_pros', ['id'], unique=False)
    op.create_table('product_specifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('spec_key', sa.String(), nullable=False),
    sa.Column('spec_value', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_specifications_id'), 'product_specifications', ['id'], unique=False)
    op.create_table('product_store_association',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('product_id', 'store_id')
    )
    op.drop_column('articles', 'faqs')
    op.drop_column('articles', 'categories_id_list')
    op.drop_column('articles', 'seo_keywords')
    op.drop_column('articles', 'products_id_list')
    op.drop_column('products', 'affiliate_urls')
    op.drop_column('products', 'store_ids')
    op.drop_column('products', 'image_urls')
    op.drop_column('products', 'pros')
    op.drop_column('products', 'cons')
    op.drop_column('products', 'image_ids')
    op.drop_column('products', 'specifications')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('specifications', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('image_ids', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('cons', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('pros', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('image_urls', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('store_ids', sa.TEXT(), nullable=False))
    op.add_column('products', sa.Column('affiliate_urls', sa.TEXT(), nullable=False))
    op.add_column('articles', sa.Column('products_id_list', sa.TEXT(), nullable=True))
    op.add_column('articles', sa.Column('seo_keywords', sa.TEXT(), nullable=True))
    op.add_column('articles', sa.Column('categories_id_list', sa.TEXT(), nullable=True))
    op.add_column('articles', sa.Column('faqs', sa.TEXT(), nullable=True))
    op.drop_table('product_store_association')
    op.drop_index(op.f('ix_product_specifications_id'), table_name='product_specifications')
    op.drop_table('product_specifications')
    op.drop_index(op.f('ix_product_pros_id'), table_name='product_pros')
    op.drop_table('product_pros')
    op.drop_index(op.f('ix_product_images_id'), table_name='product_images')
    op.drop_table('product_images')
    op.drop_index(op.f('ix_product_cons_id'), table_name='product_cons')
    op.drop_table('product_cons')
    op.drop_index(op.f('ix_product_affiliate_urls_id'), table_name='product_affiliate_urls')
    op.drop_table('product_affiliate_urls')
    op.drop_index(op.f('ix_article_seo_keywords_id'), table_name='article_seo_keywords')
    op.drop_table('article_seo_keywords')
    op.drop_table('article_product_association')
    op.drop_index(op.f('ix_article_faqs_id'), table_name='article_faqs')
    op.drop_table('article_faqs')
    op.drop_table('article_category_association')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
