from sqlalchemy import Column, Integer, String, Table, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

article_product_association = Table(
    "article_product_association",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True)
)

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    wp_id = Column(Integer, nullable=True)
    title = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    author_id = Column(Integer, nullable=True)
    status = Column(String, nullable=True, default='draft')
    content = Column(Text, nullable=True)

    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)

    main_image_url = Column(String, nullable=True)
    main_image_wp_id = Column(Integer, nullable=True)

    buyers_guide_image_url = Column(String, nullable=True)
    buyers_guide_image_wp_id = Column(Integer, nullable=True)

    introduction = Column(Text, nullable=True)
    buyers_guide = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)

    products = relationship("Product", secondary="article_product_association", back_populates="articles")
    categories = relationship("Category", back_populates="article", cascade="all, delete-orphan")
    seo_keywords = relationship("ArticleSEOKeyword", back_populates="article", cascade="all, delete-orphan")
    faqs = relationship("ArticleFAQ", back_populates="article", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    wp_id = Column(Integer, nullable=False)

    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    article = relationship("Article", back_populates="categories")

class ArticleFAQ(Base):
    __tablename__ = "article_faqs"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    question = Column(String, nullable=False)
    answer = Column(Text, nullable=False)

    article = relationship("Article", back_populates="faqs")

class ArticleSEOKeyword(Base):
    __tablename__ = "article_seo_keywords"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(String, nullable=False)

    article = relationship("Article", back_populates="seo_keywords")
