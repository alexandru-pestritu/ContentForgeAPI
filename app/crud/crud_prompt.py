import csv
from io import StringIO
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.product import Product
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse
from typing import Dict, List, Optional
from app.services.markdown_service import MarkdownService

def create_prompt(db: Session, blog_id: int, prompt: PromptCreate) -> PromptResponse:
    prompt_data = prompt.model_dump()
    prompt_data["blog_id"] = blog_id
    new_prompt = Prompt(**prompt_data)
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return PromptResponse.model_validate(new_prompt)

def get_prompt_by_id(db: Session, blog_id: int, prompt_id: int) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.blog_id == blog_id).first()
    if prompt:
        return PromptResponse.model_validate(prompt)
    return None

def get_prompts(
    db: Session, 
    blog_id: int,
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> dict:
    query = db.query(Prompt).filter(Prompt.blog_id == blog_id)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Prompt.name.ilike(filter_pattern) |
            Prompt.type.ilike(filter_pattern) |
            Prompt.subtype.ilike(filter_pattern) |
            Prompt.text.ilike(filter_pattern)
        )

    if sort_field:
        if sort_order == -1:
            query = query.order_by(getattr(Prompt, sort_field).desc())
        else:
            query = query.order_by(getattr(Prompt, sort_field).asc())

    total_records = query.count()
    prompts = query.offset(skip).limit(limit).all()

    return {
        "prompts": [PromptResponse.model_validate(prompt) for prompt in prompts],
        "total_records": total_records
    }

def update_prompt(db: Session, blog_id: int, prompt_id: int, prompt_update: PromptUpdate) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.blog_id == blog_id).first()
    if prompt:
        update_data = prompt_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(prompt, key, value)
        db.commit()
        db.refresh(prompt)
        return PromptResponse.model_validate(prompt)
    return None

def delete_prompt(db: Session, blog_id: int, prompt_id: int) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id, Prompt.blog_id == blog_id).first()
    if prompt:
        db.delete(prompt)
        db.commit()
        return PromptResponse.model_validate(prompt)
    return None

def get_prompt_types_subtypes() -> Dict[str, List[str]]:
    """
    Return the available types and subtypes for prompts.
    """
    return {
        "Product": ["Review", "Pros & Cons"],
        "Article": ["Introduction", "Buyer's Guide", "FAQs", "Conclusion"]
    }

def get_prompts_by_type_and_optional_subtype(
    db: Session, 
    blog_id: int,
    prompt_type: Optional[str] = None, 
    prompt_subtype: Optional[str] = None
) -> List[PromptResponse]:
    """
    Retrieve all prompts of a specific type and optionally a subtype.

    :param db: Database session.
    :param prompt_type: The optional type of prompts to retrieve.
    :param prompt_subtype: The optional subtype of prompts to retrieve.
    :return: List of prompts with the specified type and optional subtype.
    """
    query = db.query(Prompt).filter(Prompt.blog_id == blog_id)
    
    if prompt_type:
        query = query.filter(Prompt.type == prompt_type)
    
    if prompt_subtype:
        query = query.filter(Prompt.subtype == prompt_subtype)
    
    prompts = query.all()
    return [PromptResponse.model_validate(prompt) for prompt in prompts]