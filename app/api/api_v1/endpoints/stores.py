from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user

from app.schemas.stores import StoreCreate, StoreUpdate, StoreResponse
from app.crud.crud_store import (
    create_store,
    get_stores,
    get_store_by_id,
    update_store,
    delete_store
)

from app.services.wordpress_service import WordPressService
from app.services.image_service import ImageService

router = APIRouter()


@router.post("/", response_model=StoreResponse)
async def create_new_store(
    store_data: StoreCreate,
    blog_id: int = Path(..., description="The ID of the blog"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None
) -> StoreResponse:
    """
    Creates a new store for the specified blog.

    :param blog_id: The ID of the blog to which the store belongs.
    :param store_data: The Pydantic model containing store details.
    :param db: The database session.
    :param current_user: The currently authenticated user.
    :param upload_to_wordpress: Whether to upload the store's favicon to WordPress.
    :return: The newly created store as a StoreResponse.
    """
    image_service: Optional[ImageService] = None
    if upload_to_wordpress:
        wordpress_service = WordPressService(blog_id=blog_id, db=db)
        image_service = ImageService(wordpress_service)

    new_store = await create_store(
        db=db,
        blog_id=blog_id,
        store=store_data,
        image_service=image_service
    )
    return new_store


@router.get("/", response_model=Dict[str, Any])
async def read_stores(
    blog_id: int = Path(..., description="The ID of the blog"),
    skip: int = 0,
    limit: int = 10,
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieves a paginated list of stores for the specified blog, with optional sorting and filtering.

    :param blog_id: The ID of the blog whose stores are requested.
    :param skip: Number of records to skip (for pagination).
    :param limit: Maximum number of records to return (for pagination).
    :param sort_field: The field by which results should be sorted.
    :param sort_order: The sort order (use -1 for DESC, otherwise ASC).
    :param filter: An optional filter string that matches store fields like name/base_url.
    :param db: The database session.
    :param current_user: The currently authenticated user.
    :return: A dictionary containing a list of stores and the total record count.
    """
    result = get_stores(
        db=db,
        blog_id=blog_id,
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_order=sort_order,
        filter=filter
    )
    return result


@router.get("/{store_id}", response_model=StoreResponse)
async def read_store(
    blog_id: int = Path(..., description="The ID of the blog"),
    store_id: int = Path(..., description="The ID of the store"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StoreResponse:
    """
    Retrieves details of a specific store by store_id, ensuring it belongs to the specified blog.

    :param blog_id: The ID of the blog.
    :param store_id: The ID of the store.
    :param db: The database session.
    :param current_user: The currently authenticated user.
    :return: A StoreResponse if found; otherwise raises 404.
    """
    store = get_store_by_id(db=db, store_id=store_id, blog_id=blog_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.put("/{store_id}", response_model=StoreResponse)
async def update_existing_store(
    store_data: StoreUpdate,
    blog_id: int = Path(..., description="The ID of the blog"),
    store_id: int = Path(..., description="The ID of the store"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upload_to_wordpress: Optional[bool] = None
) -> StoreResponse:
    """
    Updates an existing store under the specified blog.

    :param blog_id: The ID of the blog.
    :param store_id: The ID of the store to update.
    :param store_data: The Pydantic model containing updated fields for the store.
    :param db: The database session.
    :param current_user: The currently authenticated user.
    :param upload_to_wordpress: Whether to re-upload or update the store's favicon in WordPress.
    :return: The updated store as a StoreResponse if found; otherwise raises 404.
    """
    image_service: Optional[ImageService] = None
    if upload_to_wordpress:
        wordpress_service = WordPressService(blog_id=blog_id, db=db)
        image_service = ImageService(wordpress_service)

    updated_store = await update_store(
        db=db,
        store_id=store_id,
        blog_id=blog_id,
        store_update=store_data,
        image_service=image_service
    )
    if not updated_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return updated_store


@router.delete("/{store_id}", response_model=StoreResponse)
async def delete_existing_store(
    blog_id: int = Path(..., description="The ID of the blog"),
    store_id: int = Path(..., description="The ID of the store"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> StoreResponse:
    """
    Deletes a store by its ID, ensuring it belongs to the specified blog.

    :param blog_id: The ID of the blog.
    :param store_id: The ID of the store to delete.
    :param db: The database session.
    :param current_user: The currently authenticated user.
    :return: The deleted store as a StoreResponse if found; otherwise raises 404.
    """
    deleted_store = delete_store(db=db, store_id=store_id, blog_id=blog_id)
    if not deleted_store:
        raise HTTPException(status_code=404, detail="Store not found")
    return deleted_store
