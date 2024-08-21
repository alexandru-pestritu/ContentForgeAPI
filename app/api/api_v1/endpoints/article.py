from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from app.crud.crud_article import (
    create_article, 
    get_article_by_id, 
    get_articles, 
    update_article, 
    delete_article
)
from app.database import get_db
from app.models.user import User  
from app.dependencies.auth import get_current_user  
from app.services.wordpress_service import WordPressService
from app.services.image_service import ImageService

router = APIRouter()

@router.post("/", response_model=ArticleResponse)
async def create_new_article(
    article: ArticleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None,
    wordpress_service: WordPressService = Depends()
):
    """
    Create a new article.
    """
    image_service = None
    if upload_to_wordpress:
        image_service = ImageService(wordpress_service)
    
    return await create_article(db=db, article=article, image_service=image_service)

@router.get("/", response_model=Dict[str, Any])
async def read_articles(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Retrieve a list of articles with pagination.
    """
    result = get_articles(db=db, skip=skip, limit=limit)
    return result

@router.get("/{article_id}", response_model=ArticleResponse)
async def read_article(
    article_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Retrieve an article by ID.
    """
    article = get_article_by_id(db=db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_existing_article(
    article_id: int, 
    article: ArticleUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None,
    wordpress_service: WordPressService = Depends()
):
    """
    Update an existing article.
    """
    image_service = None
    if upload_to_wordpress:
        image_service = ImageService(wordpress_service)

    updated_article = await update_article(db=db, article_id=article_id, article_update=article, image_service=image_service)
    
    if not updated_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return updated_article

@router.delete("/{article_id}", response_model=ArticleResponse)
async def delete_existing_article(
    article_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    """
    Delete an article by ID.
    """
    deleted_article = delete_article(db=db, article_id=article_id)
    if not deleted_article:
        raise HTTPException(status_code=404, detail="Article not found")
    return deleted_article
