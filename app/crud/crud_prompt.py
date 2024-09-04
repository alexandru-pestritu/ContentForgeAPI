from sqlalchemy.orm import Session
from app.models.prompt import Prompt
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse
from typing import Dict, List, Optional

def create_prompt(db: Session, prompt: PromptCreate) -> PromptResponse:
    new_prompt = Prompt(**prompt.model_dump())
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return PromptResponse.model_validate(new_prompt)

def get_prompt_by_id(db: Session, prompt_id: int) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt:
        return PromptResponse.model_validate(prompt)
    return None

def get_prompts(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> dict:
    query = db.query(Prompt)

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

def update_prompt(db: Session, prompt_id: int, prompt_update: PromptUpdate) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt:
        update_data = prompt_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(prompt, key, value)
        db.commit()
        db.refresh(prompt)
        return PromptResponse.model_validate(prompt)
    return None

def delete_prompt(db: Session, prompt_id: int) -> Optional[PromptResponse]:
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
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
        "product": ["review", "proscons"],
        "article": ["introduction", "buyers_guide", "faqs", "conclusion"]
    }


def get_placeholders_for_type(type: str) -> List[str]:
    """
    Return available placeholders for a given type (product or article).
    """
    placeholders = {
        "product": [
            "{name}", "{full_name}", "{affiliate_urls}", "{description}",
            "{specifications}", "{seo_keyword}", "{pros}", "{cons}", "{review}", "{rating}",
            "{image_urls}"
        ],
        "article": [
            "{title}", "{slug}", "{content}", "{seo_keywords}", "{meta_title}", "{meta_description}", 
            "{main_image_url}", "{buyers_guide_image_url}", "{products_id_list}", 
            "{introduction}", "{buyers_guide}", "{faqs}", "{conclusion}"
        ]
    }
    return placeholders.get(type, [])