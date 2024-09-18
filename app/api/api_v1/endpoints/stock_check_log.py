from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.stock_check_log import StockCheckLogResponse
from app.crud.crud_stock_check_log import get_stock_check_logs
from app.database import get_db

router = APIRouter()

@router.get("/", response_model=List[StockCheckLogResponse])
async def read_stock_check_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all stock check logs with optional date filtering.
    """
    logs = get_stock_check_logs(db=db, start_date=start_date, end_date=end_date)
    if not logs:
        raise HTTPException(status_code=404, detail="No stock check logs found")
    return logs
