from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.placeholder_service import PlaceholderService

router = APIRouter()

@router.get("/{type}", response_model=List[str])
async def get_placeholders(
    type: str,
    current_user: User = Depends(get_current_user) 
):
    """
    Get available placeholders for a given type (product or article).
    """
    return PlaceholderService.get_placeholders_for_type(type)