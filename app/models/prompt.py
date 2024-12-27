from sqlalchemy import Column, ForeignKey, Integer, String, Text
from app.database import Base

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  
    subtype = Column(String, nullable=False)  
    text = Column(Text, nullable=False)