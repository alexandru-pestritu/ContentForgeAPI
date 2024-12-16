from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.exporter.exporter_service import EXPORTERS
import io

router = APIRouter()

@router.get("/", response_class=StreamingResponse)
async def export_entities(
    entity_type: str = Query(...),
    skip: int = 0,
    limit: int = 10,
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export entities of the given type as a CSV file.
    """
    exporter = EXPORTERS.get(entity_type)
    if not exporter:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {entity_type}")

    csv_data = exporter(db=db, skip=skip, limit=limit, sort_field=sort_field, sort_order=sort_order, filter=filter)
    
    filename = f"{entity_type}_export.csv"

    response = StreamingResponse(io.StringIO(csv_data), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
