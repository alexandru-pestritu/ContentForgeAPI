from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.crud_ai import get_providers_by_feature_and_subfeature, generate_product_text, generate_article_text
from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.get("/providers", response_model=Dict[str, Any])
async def get_providers(
    feature: str, 
    subfeature: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Get the list of providers based on feature and subfeature.
    """
    try:
        providers = await get_providers_by_feature_and_subfeature(feature_name=feature, subfeature_name=subfeature)
        return providers
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-product-text", response_model=Dict[str, Any])
async def generate_product_ai_text(
    product_id: int, 
    prompt_id: int, 
    provider: str, 
    model: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Generate text for a product using AI and return the updated product along with the cost.
    
    :param product_id: ID of the product to update.
    :param prompt_id: ID of the prompt to use for AI generation.
    :param provider: Name of the AI provider (e.g., 'openai').
    :param model: Name of the AI model (e.g., 'gpt-4o').
    :param db: Database session.
    :param current_user: The current authenticated user.
    :return: The updated product and the cost of the AI operation.
    """
    try:
        result = await generate_product_text(db=db, product_id=product_id, prompt_id=prompt_id, provider=provider, model=model)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-article-text", response_model=Dict[str, Any])
async def generate_article_ai_text(
    article_id: int, 
    prompt_id: int, 
    provider: str, 
    model: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Generate text for an article using AI and return the updated article along with the cost.
    
    :param article_id: ID of the article to update.
    :param prompt_id: ID of the prompt to use for AI generation.
    :param provider: Name of the AI provider (e.g., 'openai').
    :param model: Name of the AI model (e.g., 'gpt-4o').
    :param db: Database session.
    :param current_user: The current authenticated user.
    :return: The updated article and the cost of the AI operation.
    """
    try:
        result = await generate_article_text(db=db, article_id=article_id, prompt_id=prompt_id, provider=provider, model=model)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
