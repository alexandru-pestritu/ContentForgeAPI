from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.models.stock_check_log import StockCheckLog
from app.schemas.stock_check_log import StockCheckLogResponse

def get_stock_check_logs(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[StockCheckLogResponse]:
    """
    Retrieve stock check logs with optional date filtering.
    Returns a list of Pydantic models.
    """
    query = db.query(StockCheckLog)

    if start_date:
        query = query.filter(StockCheckLog.check_time >= start_date)
    if end_date:
        query = query.filter(StockCheckLog.check_time <= end_date)

    logs = query.all()
    return [StockCheckLogResponse.from_orm(log) for log in logs]
