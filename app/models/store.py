from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    base_url = Column(String)
    favicon_url = Column(String)
    favicon_wp_image_id = Column(Integer, nullable=True)
