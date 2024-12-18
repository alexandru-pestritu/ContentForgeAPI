from sqlalchemy import Column, DateTime, Integer, String, Text, Float, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

product_store_association = Table(
    "product_store_association",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
    Column("store_id", Integer, ForeignKey("stores.id", ondelete="CASCADE"), primary_key=True)
)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    in_stock = Column(Boolean, nullable=True)
    description = Column(Text, nullable=True)
    seo_keyword = Column(String, nullable=False)
    review = Column(Text, nullable=True)
    rating = Column(Float, nullable=False)
    last_checked = Column(DateTime, nullable=True)

    articles = relationship("Article", secondary="article_product_association", back_populates="products")
    stores = relationship("Store", secondary=product_store_association, back_populates="products")
    affiliate_urls = relationship("ProductAffiliateURL", back_populates="product", cascade="all, delete-orphan")
    specifications = relationship("ProductSpecification", back_populates="product", cascade="all, delete-orphan")
    pros = relationship("ProductPro", back_populates="product", cascade="all, delete-orphan")
    cons = relationship("ProductCon", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class ProductAffiliateURL(Base):
    __tablename__ = "product_affiliate_urls"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)

    product = relationship("Product", back_populates="affiliate_urls")

class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    spec_key = Column(String, nullable=False)
    spec_value = Column(String, nullable=False)

    product = relationship("Product", back_populates="specifications")

class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String, nullable=False)
    wp_id = Column(Integer, nullable=True)

    product = relationship("Product", back_populates="images")

class ProductPro(Base):
    __tablename__ = "product_pros"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)

    product = relationship("Product", back_populates="pros")

class ProductCon(Base):
    __tablename__ = "product_cons"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)

    product = relationship("Product", back_populates="cons")