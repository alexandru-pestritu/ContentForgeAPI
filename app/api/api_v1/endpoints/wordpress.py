from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.wordpress_service import WordPressService
from app.models.user import User
from app.dependencies.auth import get_current_user 

router = APIRouter()

@router.get("/users", response_model=List[dict])
async def get_wordpress_users(
    wordpress_service: WordPressService = Depends(),
    current_user: User = Depends(get_current_user)  
):
    """
    Get a list of users from WordPress.
    """
    try:
        users = await wordpress_service.get_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[dict])
async def get_wordpress_categories(
    wordpress_service: WordPressService = Depends(),
    current_user: User = Depends(get_current_user)  
):
    """
    Get a list of categories from WordPress.
    """
    try:
        categories = await wordpress_service.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
