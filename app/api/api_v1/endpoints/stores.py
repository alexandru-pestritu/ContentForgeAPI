from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.schemas.stores import StoreCreate, StoreUpdate, StoreResponse
from app.crud.crud_store import (
    create_store, 
    get_store_by_id, 
    get_stores, 
    update_store, 
    delete_store
)
from app.database import get_db
from app.models.user import User  
from app.dependencies.auth import get_current_user  
from app.services.wordpress_service import WordPressService
from app.services.image_service import ImageService

router = APIRouter()

@router.post("/", response_model=StoreResponse)
async def create_new_store(
    store: StoreCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),  
    upload_to_wordpress: Optional[bool] = None,
    wordpress_service: WordPressService = Depends()
):
    """
    Create a new store.
    """
    image_service = ImageService(wordpress_service) if upload_to_wordpress else None
    return await create_store(db=db, store=store, image_service=image_service)

@router.get("/", response_model=Dict[str, Any])
async def read_stores(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Retrieve a list of stores with pagination and total records.
    """
    result = get_stores(db=db, skip=skip, limit=limit)
    return result

@router.get("/{store_id}", response_model=StoreResponse)
async def read_store(
    store_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Retrieve a store by ID.
    """
    store = get_store_by_id(db=db, store_id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@router.put("/{store_id}", response_model=StoreResponse)
async def update_existing_store(
    store_id: int, 
    store: StoreUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  
    upload_to_wordpress: Optional[bool] = None,
    wordpress_service: WordPressService = Depends()
):
    """
    Update an existing store.
    """
    image_service = ImageService(wordpress_service) if upload_to_wordpress else None
    
    updated_store = await update_store(db=db, store_id=store_id, store_update=store, image_service=image_service)
    
    if not updated_store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    return updated_store

@router.delete("/{store_id}", response_model=StoreResponse)
async def delete_existing_store(
    store_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    """
    Delete a store by ID.
    """
    deleted_store = delete_store(db=db, store_id=store_id)
    if not deleted_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return deleted_store
