from sqlalchemy import Column, Integer, String
from app.database import Base

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    username = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    logo_url = Column(String, nullable=True)
