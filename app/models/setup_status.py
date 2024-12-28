from sqlalchemy import Column, Integer, Boolean
from app.database import Base

class SetupStatus(Base):
    __tablename__ = "setup_status"

    id = Column(Integer, primary_key=True, index=True)
    setup_completed = Column(Boolean, default=False, nullable=False)
    current_step = Column(Integer, default=1, nullable=False)
