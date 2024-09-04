from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse
from app.crud.crud_prompt import (
    create_prompt, 
    get_prompt_by_id, 
    get_prompts, 
    update_prompt, 
    delete_prompt
)
from app.database import get_db
from app.models.user import User  
from app.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=PromptResponse)
async def create_new_prompt(
    prompt: PromptCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Create a new prompt.
    """
    return create_prompt(db=db, prompt=prompt)

@router.get("/", response_model=Dict[str, Any])
async def read_prompts(
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a list of prompts with pagination, sorting, filtering, and total records.
    """
    result = get_prompts(db=db, skip=skip, limit=limit, sort_field=sort_field, sort_order=sort_order, filter=filter)
    return result

@router.get("/{prompt_id}", response_model=PromptResponse)
async def read_prompt(
    prompt_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a prompt by ID.
    """
    prompt = get_prompt_by_id(db=db, prompt_id=prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_existing_prompt(
    prompt_id: int, 
    prompt: PromptUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing prompt.
    """
    updated_prompt = update_prompt(db=db, prompt_id=prompt_id, prompt_update=prompt)
    if not updated_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated_prompt

@router.delete("/{prompt_id}", response_model=PromptResponse)
async def delete_existing_prompt(
    prompt_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a prompt by ID.
    """
    deleted_prompt = delete_prompt(db=db, prompt_id=prompt_id)
    if not deleted_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return deleted_prompt
