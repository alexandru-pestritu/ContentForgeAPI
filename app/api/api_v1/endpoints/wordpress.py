from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List
from app.services.wordpress_service import WordPressService
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user 

router = APIRouter()

@router.get("/users", response_model=List[dict])
async def get_wordpress_users(
    blog_id: int = Path(..., title="The ID of the blog to get users from."),
    db : Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    """
    Get a list of users from WordPress.
    """
    wordpress_service = WordPressService(blog_id=blog_id, db=db)
    try:
        users = await wordpress_service.get_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories", response_model=List[dict])
async def get_wordpress_categories(
    blog_id: int = Path(..., title="The ID of the blog to get categories from."),
    db : Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    """
    Get a list of categories from WordPress.
    """
    wordpress_service = WordPressService(blog_id=blog_id, db=db)
    try:
        categories = await wordpress_service.get_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
