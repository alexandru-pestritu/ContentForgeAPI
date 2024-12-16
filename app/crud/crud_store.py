from io import StringIO
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from app.models.store import Store
from app.schemas.stores import StoreCreate, StoreUpdate, StoreResponse
from typing import List, Optional
from app.services.image_service import ImageService
import csv

async def create_store(
    db: Session, 
    store: StoreCreate, 
    image_service: Optional[ImageService] = None
    ) -> StoreResponse:
    """
    Create a new store record in the database.
    """
    store_data = store.model_dump()

    store_data['base_url'] = str(store_data['base_url'])

    domain = urlparse(store_data['base_url']).netloc
    store_data['favicon_url'] = f"https://www.google.com/s2/favicons?domain={domain}"

    if image_service:
        store_data['favicon_image_id'] = await image_service.process_store_image(store_data['name'], store_data['favicon_url'])

    new_store = Store(**store_data)
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return StoreResponse.model_validate(new_store)

def get_store_by_id(
    db: Session, 
    store_id: int
    ) -> Optional[StoreResponse]:
    """
    Retrieve a store by its ID.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        return StoreResponse.model_validate(store)
    return None

def get_stores(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> dict:
    """
    Retrieve a list of stores, with pagination support, sorting, filtering, and total records.
    """
    query = db.query(Store)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Store.name.ilike(filter_pattern) |
            Store.base_url.ilike(filter_pattern) |
            Store.favicon_image_id.ilike(filter_pattern)
        )

    if sort_field:
        if sort_order == -1:
            query = query.order_by(getattr(Store, sort_field).desc())
        else:
            query = query.order_by(getattr(Store, sort_field).asc())

    total_records = query.count()
    stores = query.offset(skip).limit(limit).all()

    return {
        "stores": [StoreResponse.model_validate(store) for store in stores],
        "total_records": total_records
    }


async def update_store(
    db: Session, 
    store_id: int, 
    store_update: StoreUpdate, 
    image_service: Optional[ImageService] = None
    ) -> Optional[StoreResponse]:
    """
    Update an existing store record.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        update_data = store_update.model_dump(exclude_unset=True)

        if 'base_url' in update_data:
            update_data['base_url'] = str(update_data['base_url'])

            domain = urlparse(update_data['base_url']).netloc
            update_data['favicon_url'] = f"https://www.google.com/s2/favicons?domain={domain}"

        if image_service:
            update_data['favicon_image_id'] = await image_service.process_store_image(update_data['name'], update_data['favicon_url'])

        for key, value in update_data.items():
            setattr(store, key, value)
        db.commit()
        db.refresh(store)
        return StoreResponse.model_validate(store)
    return None

def delete_store(
    db: Session, 
    store_id: int
    ) -> Optional[StoreResponse]:
    """
    Delete a store by its ID.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        db.delete(store)
        db.commit()
        return StoreResponse.model_validate(store)
    return None