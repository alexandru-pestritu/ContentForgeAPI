from urllib.parse import urlparse
from sqlalchemy.orm import Session
from app.models.store import Store
from app.schemas.stores import StoreCreate, StoreUpdate, StoreResponse
from typing import List, Optional

def create_store(db: Session, store: StoreCreate) -> StoreResponse:
    """
    Create a new store record in the database.
    """
    # Convert HttpUrl objects to strings
    base_url_str = str(store.base_url)
    domain = urlparse(base_url_str).netloc
    favicon_url_str = f"https://www.google.com/s2/favicons?domain={domain}"

    store_data = store.model_dump()
    store_data['base_url'] = base_url_str
    store_data['favicon_url'] = favicon_url_str
    store_data['favicon_image_id'] = None  

    new_store = Store(**store_data)
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return StoreResponse.model_validate(new_store)

def get_store_by_id(db: Session, store_id: int) -> Optional[StoreResponse]:
    """
    Retrieve a store by its ID.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        return StoreResponse.model_validate(store)
    return None

def get_stores(db: Session, skip: int = 0, limit: int = 10) -> List[StoreResponse]:
    """
    Retrieve a list of stores, with pagination support.
    """
    stores = db.query(Store).offset(skip).limit(limit).all()
    return [StoreResponse.model_validate(store) for store in stores]

def update_store(db: Session, store_id: int, store_update: StoreUpdate) -> Optional[StoreResponse]:
    """
    Update an existing store record.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        update_data = store_update.model_dump(exclude_unset=True)
        
        # Convert HttpUrl objects to strings if they are provided
        if 'base_url' in update_data and update_data['base_url'] is not None:
            update_data['base_url'] = str(update_data['base_url'])
        if 'favicon_url' in update_data and update_data['favicon_url'] is not None:
            update_data['favicon_url'] = str(update_data['favicon_url'])

        for key, value in update_data.items():
            setattr(store, key, value)
        db.commit()
        db.refresh(store)
        return StoreResponse.model_validate(store)
    return None


def delete_store(db: Session, store_id: int) -> Optional[StoreResponse]:
    """
    Delete a store by its ID.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        db.delete(store)
        db.commit()
        return StoreResponse.model_validate(store)
    return None
