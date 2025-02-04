from sqlalchemy import Column, ForeignKey, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True, nullable=False)
    base_url = Column(String, nullable=False)
    favicon_image_id = Column(Integer, nullable=True)
    favicon_url = Column(String, nullable=True)

    products = relationship("Product", secondary="product_store_association", back_populates="stores")
