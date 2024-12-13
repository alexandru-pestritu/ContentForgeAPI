import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.schemas.prompt import PromptCreate, PromptUpdate, PromptResponse
from app.schemas.prompt_type_subtype_response import PromptTypeSubtypeResponse
from app.crud.crud_prompt import (
    create_prompt, 
    get_prompt_by_id, 
    get_prompts, 
    update_prompt, 
    delete_prompt,
    get_prompt_types_subtypes,
    get_placeholders_for_type,
    get_prompts_by_type_and_optional_subtype,
    export_prompts
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

@router.get("/export", response_class=StreamingResponse)
async def export_prompt_data(
    skip: int = 0,
    limit: int = 10,
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Export prompts as a CSV file based on the current table view.
    """
    csv_data = export_prompts(
        db=db,
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_order=sort_order,
        filter=filter
    )
    
    response = StreamingResponse(io.StringIO(csv_data), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=prompts_export.csv"
    return response

@router.get("/{prompt_type}", response_model=List[PromptResponse])
async def read_prompts_by_type_and_optional_subtype(
    prompt_type: str, 
    prompt_subtype: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all prompts of a specific type and optionally a subtype.
    
    :param prompt_type: The type of prompts to retrieve.
    :param prompt_subtype: The optional subtype of prompts to retrieve.
    :param db: Database session.
    :param current_user: The current authenticated user.
    :return: List of prompts.
    """
    prompts = get_prompts_by_type_and_optional_subtype(
        db=db, 
        prompt_type=prompt_type, 
        prompt_subtype=prompt_subtype
    )
    return prompts



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

@router.get("/types-subtypes/", response_model=PromptTypeSubtypeResponse)
async def get_types_subtypes(
    current_user: User = Depends(get_current_user)
):
    """
    Get available types and subtypes for prompts.
    """
    types_subtypes = get_prompt_types_subtypes()
    return {"types": types_subtypes}

@router.get("/placeholders/{type}", response_model=List[str])
async def get_placeholders(
    type: str,
    current_user: User = Depends(get_current_user) 
):
    """
    Get available placeholders for a given type (product or article).
    """
    return get_placeholders_for_type(type)