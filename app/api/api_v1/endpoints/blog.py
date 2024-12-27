from typing import Any, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.blog import (
    BlogCreate,
    BlogUpdate,
    BlogResponse
)
from app.crud.crud_blog import (
    create_blog,
    get_blog_by_id,
    get_blogs,
    update_blog,
    delete_blog
)

router = APIRouter()

@router.post("/", response_model=BlogResponse)
def create_new_blog(
    blog_data: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new blog.
    
    :param blog_data: The Pydantic model containing the new blog data.
    :param db: The database session.
    :return: The created BlogResponse model.
    """
    return create_blog(db=db, blog_data=blog_data)

@router.get("/", response_model=Dict[str, Any])
def read_blogs(
    skip: int = 0,
    limit: int = 10,
    filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of blogs with pagination and optional filtering.
    
    :param skip: Number of records to skip.
    :param limit: Maximum number of records to return.
    :param filter: Optional string to filter by blog name, base_url, or username.
    :param db: The database session.
    :return: A dictionary containing the 'blogs' list and 'total_records'.
    """
    return get_blogs(db=db, skip=skip, limit=limit, filter_str=filter)

@router.get("/{blog_id}", response_model=BlogResponse)
def read_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a specific blog by its ID.
    
    :param blog_id: The ID of the blog to retrieve.
    :param db: The database session.
    :return: The BlogResponse model, if found.
    """
    blog = get_blog_by_id(db=db, blog_id=blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog

@router.put("/{blog_id}", response_model=BlogResponse)
def update_existing_blog(
    blog_id: int,
    blog_update: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing blog.
    
    :param blog_id: The ID of the blog to update.
    :param blog_update: A Pydantic model containing fields to be updated.
    :param db: The database session.
    :return: The updated BlogResponse model, if the blog is found.
    """
    updated_blog = update_blog(db=db, blog_id=blog_id, blog_update=blog_update)
    if not updated_blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return updated_blog

@router.delete("/{blog_id}", response_model=BlogResponse)
def delete_existing_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a blog by its ID.
    
    :param blog_id: The ID of the blog to delete.
    :param db: The database session.
    :return: The BlogResponse model of the deleted blog, if found.
    """
    deleted_blog = delete_blog(db=db, blog_id=blog_id)
    if not deleted_blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return deleted_blog
