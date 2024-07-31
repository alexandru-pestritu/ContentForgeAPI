from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.stores import StoreCreate, StoreUpdate, StoreResponse
from app.crud.crud_store import (
    create_store, 
    get_store_by_id, 
    get_stores, 
    update_store, 
    delete_store
)
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=StoreResponse)
def create_new_store(store: StoreCreate, db: Session = Depends(get_db)):
    """
    Create a new store.
    """
    return create_store(db=db, store=store)

@router.get("/", response_model=List[StoreResponse])
def read_stores(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Retrieve a list of stores with pagination.
    """
    return get_stores(db=db, skip=skip, limit=limit)

@router.get("/{store_id}", response_model=StoreResponse)
def read_store(store_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a store by ID.
    """
    store = get_store_by_id(db=db, store_id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@router.put("/{store_id}", response_model=StoreResponse)
def update_existing_store(store_id: int, store: StoreUpdate, db: Session = Depends(get_db)):
    """
    Update an existing store.
    """
    updated_store = update_store(db=db, store_id=store_id, store_update=store)
    if not updated_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return updated_store

@router.delete("/{store_id}", response_model=StoreResponse)
def delete_existing_store(store_id: int, db: Session = Depends(get_db)):
    """
    Delete a store by ID.
    """
    deleted_store = delete_store(db=db, store_id=store_id)
    if not deleted_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return deleted_store
