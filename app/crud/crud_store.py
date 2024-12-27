import csv
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.store import Store
from app.schemas.stores import StoreCreate, StoreUpdate, StoreResponse
from app.services.image_service import ImageService


async def create_store(
    db: Session,
    blog_id: int,
    store: StoreCreate,
    image_service: Optional[ImageService] = None
) -> StoreResponse:
    """
    Creates a new store record in the database, associated with a specific blog.

    :param db: The database session.
    :param blog_id: The ID of the blog that owns this store.
    :param store: A Pydantic model containing store creation data.
    :param image_service: Optional service for uploading the store's favicon to WordPress.
    :return: A StoreResponse containing the newly created store.
    """
    store_data = store.model_dump()

    store_data['base_url'] = str(store_data['base_url'])

    store_data['blog_id'] = blog_id

    domain = urlparse(store_data['base_url']).netloc
    store_data['favicon_url'] = f"https://www.google.com/s2/favicons?domain={domain}"

    if image_service:
        temp_store_obj = Store(
            name=store_data['name'],
            base_url=store_data['base_url'],
            blog_id=blog_id
        )
        store_data['favicon_image_id'] = await image_service.process_image(
            entity_type="store",
            entity=temp_store_obj,
            image_url=store_data['favicon_url']
        )

    new_store = Store(**store_data)
    db.add(new_store)
    db.commit()
    db.refresh(new_store)

    return StoreResponse.model_validate(new_store)


def get_stores(
    db: Session,
    blog_id: int,
    skip: int = 0,
    limit: int = 10,
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves a list of stores for the given blog_id, with pagination, 
    optional filtering, and sorting.

    :param db: The database session.
    :param blog_id: The ID of the blog to which these stores belong.
    :param skip: Number of records to skip.
    :param limit: Maximum number of records to return.
    :param sort_field: The field by which to sort results.
    :param sort_order: -1 for DESC, otherwise ASC.
    :param filter: A string to filter the stores (by name or base_url).
    :return: A dictionary containing 'stores' (list) and 'total_records'.
    """
    query = db.query(Store).filter(Store.blog_id == blog_id)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            (Store.name.ilike(filter_pattern)) |
            (Store.base_url.ilike(filter_pattern))
        )

    if sort_field:
        field_attr = getattr(Store, sort_field, None)
        if field_attr:
            if sort_order == -1:
                query = query.order_by(field_attr.desc())
            else:
                query = query.order_by(field_attr.asc())

    total_records = query.count()
    stores = query.offset(skip).limit(limit).all()

    return {
        "stores": [StoreResponse.model_validate(s) for s in stores],
        "total_records": total_records
    }


def get_store_by_id(
    db: Session,
    store_id: int,
    blog_id: int
) -> Optional[StoreResponse]:
    """
    Retrieves a single store by its store_id, ensuring it belongs to the specified blog.

    :param db: The database session.
    :param store_id: The ID of the store to retrieve.
    :param blog_id: The ID of the blog that owns the store.
    :return: A StoreResponse if found, otherwise None.
    """
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.blog_id == blog_id
    ).first()
    if store:
        return StoreResponse.model_validate(store)
    return None


async def update_store(
    db: Session,
    store_id: int,
    blog_id: int,
    store_update: StoreUpdate,
    image_service: Optional[ImageService] = None
) -> Optional[StoreResponse]:
    """
    Updates an existing store for a specific blog, 
    optionally updating the favicon in WordPress.

    :param db: The database session.
    :param store_id: The ID of the store to update.
    :param blog_id: The ID of the blog that owns this store.
    :param store_update: A Pydantic model with updated store fields.
    :param image_service: Optional service for uploading/updating the store's favicon.
    :return: An updated StoreResponse if found, otherwise None.
    """
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.blog_id == blog_id
    ).first()
    if not store:
        return None

    update_data = store_update.model_dump(exclude_unset=True)

    if 'base_url' in update_data:
        update_data['base_url'] = str(update_data['base_url'])
        domain = urlparse(update_data['base_url']).netloc
        update_data['favicon_url'] = f"https://www.google.com/s2/favicons?domain={domain}"

        if image_service:
            update_data['favicon_image_id'] = await image_service.process_image(
                entity_type="store",
                entity=store,
                image_url=update_data['favicon_url']
            )

    for key, value in update_data.items():
        setattr(store, key, value)

    db.commit()
    db.refresh(store)
    return StoreResponse.model_validate(store)


def delete_store(
    db: Session,
    store_id: int,
    blog_id: int
) -> Optional[StoreResponse]:
    """
    Deletes a store by its ID, ensuring it belongs to the specified blog.

    :param db: The database session.
    :param store_id: The ID of the store to delete.
    :param blog_id: The ID of the blog that owns the store.
    :return: The deleted Store as a StoreResponse if found, otherwise None.
    """
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.blog_id == blog_id
    ).first()
    if not store:
        return None

    db.delete(store)
    db.commit()
    return StoreResponse.model_validate(store)
