from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud.crud_dashboard import get_dashboard_stats
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardStatsResponse

router = APIRouter()

@router.get("/stats", response_model=DashboardStatsResponse)
async def read_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve statistics for the dashboard:
    - number of published articles
    - number of draft articles
    - total number of products
    - number of out of stock products
    """
    stats = get_dashboard_stats(db=db)
    return stats