from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud.crud_product import (
    create_product, 
    get_product_by_id, 
    get_products, 
    update_product, 
    delete_product
)
from app.database import get_db
from app.models.user import User  
from app.dependencies.auth import get_current_user  

router = APIRouter()

@router.post("/", response_model=ProductResponse)
def create_new_product(
    product: ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  
):
    """
    Create a new product.
    """
    return create_product(db=db, product=product)

@router.get("/", response_model=List[ProductResponse])
async def read_products(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Retrieve a list of products with pagination.
    """
    return get_products(db=db, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Retrieve a product by ID.
    """
    product = get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_existing_product(
    product_id: int, 
    product: ProductUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    """
    Update an existing product.
    """
    updated_product = update_product(db=db, product_id=product_id, product_update=product)
    
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return updated_product

@router.delete("/{product_id}", response_model=ProductResponse)
def delete_existing_product(
    product_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    """
    Delete a product by ID.
    """
    deleted_product = delete_product(db=db, product_id=product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted_product
