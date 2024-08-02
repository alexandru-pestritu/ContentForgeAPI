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
from app.services.wordpress_service import WordPressService
from app.services.image_service import ImageService

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_new_product(
    product: ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None,
    wordpress_service: WordPressService = Depends()
):
    """
    Create a new product.
    """
    image_service = None
    if upload_to_wordpress:
        image_service = ImageService(wordpress_service)
    
    return await create_product(db=db, product=product, image_service=image_service)

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
async def read_product(
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
async def update_existing_product(
    product_id: int, 
    product: ProductUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None,
    wordpress_service: WordPressService = Depends()
):
    """
    Update an existing product.
    """
    image_service = None
    if upload_to_wordpress:
        image_service = ImageService(wordpress_service)

    updated_product = await update_product(db=db, product_id=product_id, product_update=product, image_service=image_service)
    
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return updated_product

@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_existing_product(
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
