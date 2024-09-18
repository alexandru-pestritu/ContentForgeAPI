from pydantic import BaseModel
from datetime import datetime

class StockCheckLogResponse(BaseModel):
    id: int
    check_time: datetime
    duration: float
    in_stock_count: int
    out_of_stock_count: int

    class Config:
        from_attributes = True
