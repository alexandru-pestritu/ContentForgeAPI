import io
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud.crud_product import (
    create_product,
    get_out_of_stock_products_with_articles, 
    get_product_by_id, 
    get_products, 
    update_product, 
    delete_product,
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
    blog_id: int = Path(..., description="The ID of the blog"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None,
):
    """
    Create a new product.
    """
    wordpress_service = WordPressService(blog_id=blog_id, db=db)
    image_service = ImageService(wordpress_service) if upload_to_wordpress else None
    
    return await create_product(db=db, blog_id=blog_id, product=product, image_service=image_service)

@router.get("/", response_model=Dict[str, Any])
async def read_products(
    blog_id: int = Path(..., description="The ID of the blog"),
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a list of products with pagination, sorting, filtering, and total records.
    """
    result = get_products(db=db, blog_id=blog_id, skip=skip, limit=limit, sort_field=sort_field, sort_order=sort_order, filter=filter)
    return result


@router.get("/out-of-stock", response_model=List[Dict[str, Any]])
async def read_out_of_stock_products_with_articles(
    blog_id: int = Path(..., description="The ID of the blog"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve products that are out of stock and the articles they are part of.
    """
    result = get_out_of_stock_products_with_articles(db=db, blog_id=blog_id)
    return result

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    blog_id: int = Path(..., description="The ID of the blog"),
    product_id: int = Path(..., description="The ID of the product"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) 
):
    """
    Retrieve a product by ID.
    """
    product = get_product_by_id(db=db, blog_id=blog_id, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product: ProductUpdate,
    blog_id: int = Path(..., description="The ID of the blog"),
    product_id: int = Path(..., description="The ID of the product"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None,
):
    """
    Update an existing product.
    """
    image_service: Optional[ImageService] = None
    if upload_to_wordpress:
        wordpress_service = WordPressService(blog_id=blog_id, db=db)
        image_service = ImageService(wordpress_service)

    updated_product = await update_product(db=db, blog_id=blog_id, product_id=product_id, product_update=product, image_service=image_service)
    
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return updated_product

@router.delete("/{product_id}", response_model=ProductResponse)
async def delete_existing_product(
    blog_id: int = Path(..., description="The ID of the blog"),
    product_id: int = Path(..., description="The ID of the product"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
    """
    Delete a product by ID.
    """
    deleted_product = delete_product(db=db, blog_id=blog_id, product_id=product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted_product
