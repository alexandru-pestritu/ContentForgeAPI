from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.blog import Blog
from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse

def create_blog(db: Session, blog_data: BlogCreate) -> BlogResponse:
    """
    Creates a new blog in the database.
    
    :param db: The database session.
    :param blog_data: A Pydantic model containing the blog creation data.
    :return: A BlogResponse model containing the newly created blog.
    """
    new_blog = Blog(
        name=blog_data.name,
        base_url=str(blog_data.base_url),
        username=blog_data.username,
        api_key=blog_data.api_key,
        logo_url=str(blog_data.logo_url) if blog_data.logo_url else None
    )
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return BlogResponse.model_validate(new_blog)

def get_blog_by_id(db: Session, blog_id: int) -> Optional[BlogResponse]:
    """
    Retrieves a blog by its ID from the database.
    
    :param db: The database session.
    :param blog_id: The ID of the blog to retrieve.
    :return: A BlogResponse model if found, otherwise None.
    """
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog:
        return BlogResponse.model_validate(blog)
    return None

def get_blogs(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    filter_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves a paginated list of blogs from the database, with optional filtering.
    
    :param db: The database session.
    :param skip: Number of records to skip (for pagination).
    :param limit: Maximum number of records to return (for pagination).
    :param filter_str: Optional filter to search by blog name, base_url, or username.
    :return: A dictionary containing the list of blogs and the total number of records.
    """
    query = db.query(Blog)

    if filter_str:
        filter_pattern = f"%{filter_str}%"
        query = query.filter(
            (Blog.name.ilike(filter_pattern)) |
            (Blog.base_url.ilike(filter_pattern)) |
            (Blog.username.ilike(filter_pattern))
        )

    total_records = query.count()
    blogs = query.offset(skip).limit(limit).all()

    return {
        "blogs": [BlogResponse.model_validate(b) for b in blogs],
        "total_records": total_records
    }

def update_blog(db: Session, blog_id: int, blog_update: BlogUpdate) -> Optional[BlogResponse]:
    """
    Updates an existing blog in the database.
    
    :param db: The database session.
    :param blog_id: The ID of the blog to update.
    :param blog_update: A Pydantic model containing fields to be updated.
    :return: A BlogResponse model if the blog is found and updated, otherwise None.
    """
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        return None

    update_data = blog_update.model_dump(exclude_unset=True)

    if "base_url" in update_data and update_data["base_url"] is not None:
        update_data["base_url"] = str(update_data["base_url"])

    if "logo_url" in update_data and update_data["logo_url"] is not None:
        update_data["logo_url"] = str(update_data["logo_url"])

    for key, value in update_data.items():
        setattr(blog, key, value)

    db.commit()
    db.refresh(blog)
    return BlogResponse.model_validate(blog)

def delete_blog(db: Session, blog_id: int) -> Optional[BlogResponse]:
    """
    Deletes an existing blog from the database.
    
    :param db: The database session.
    :param blog_id: The ID of the blog to delete.
    :return: A BlogResponse model if the blog is found and deleted, otherwise None.
    """
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        return None

    db.delete(blog)
    db.commit()
    return BlogResponse.model_validate(blog)
