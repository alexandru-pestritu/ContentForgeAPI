from sqlalchemy import Column, Integer, DateTime, Float
from app.database import Base
from datetime import datetime, timezone

class StockCheckLog(Base):
    __tablename__ = "stock_check_logs"

    id = Column(Integer, primary_key=True, index=True)
    check_time = Column(DateTime, default=datetime.now(timezone.utc)) 
    duration = Column(Float, nullable=False)  
    in_stock_count = Column(Integer, nullable=False) 
    out_of_stock_count = Column(Integer, nullable=False) 
