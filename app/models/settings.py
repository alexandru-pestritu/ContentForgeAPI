from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=True)
    type = Column(String, nullable=False)
    description = Column(String, nullable=True)
