from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app.crud.crud_widgets import generate_product_widget, generate_article_widget
from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/generate/product", response_model=Dict[str, Any])
async def generate_product_content(
    product_id: int, 
    blog_id: int = Path(..., description="ID of the blog."),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Generate content for a product using ProductTemplate.
    
    :param product_id: ID of the product.
    :param db: Database session.
    :param current_user: The current authenticated user.
    :return: The generated content for the product.
    """
    try:
        result = await generate_product_widget(db=db, blog_id=blog_id, product_id=product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate/article", response_model=Dict[str, Any])
async def generate_article_content(
    article_id: int, 
    publish_to_wp: bool = False, 
    blog_id: int = Path(..., description="ID of the blog."),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Generate content for an article using ArticleTemplate, optionally publish or update it in WordPress.
    
    :param article_id: ID of the article.
    :param publish_to_wp: Boolean to decide whether to publish/update the article in WordPress.
    :param db: Database session.
    :param current_user: The current authenticated user.
    :return: The generated content for the article and WordPress ID (if applicable).
    """
    try:
        result = await generate_article_widget(db=db, blog_id=blog_id, article_id=article_id, publish_to_wp=publish_to_wp)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
