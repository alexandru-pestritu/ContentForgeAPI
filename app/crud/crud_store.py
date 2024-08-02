from urllib.parse import urlparse
from sqlalchemy.orm import Session
from app.models.store import Store
from app.schemas.stores import StoreCreate, StoreUpdate, StoreResponse
from typing import List, Optional
from app.services.image_service import ImageService

async def create_store(db: Session, store: StoreCreate, image_service: Optional[ImageService] = None) -> StoreResponse:
    """
    Create a new store record in the database.
    """
    store_data = store.model_dump()

    # Convert base_url from Url type to string
    store_data['base_url'] = str(store_data['base_url'])

    # Set the favicon URL automatically
    domain = urlparse(store_data['base_url']).netloc
    store_data['favicon_url'] = f"https://www.google.com/s2/favicons?domain={domain}"

    # If image upload is requested, handle the image upload
    if image_service:
        store_data['favicon_image_id'] = await image_service.process_store_image(store_data['name'], store_data['favicon_url'])

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

async def update_store(db: Session, store_id: int, store_update: StoreUpdate, image_service: Optional[ImageService] = None) -> Optional[StoreResponse]:
    """
    Update an existing store record.
    """
    store = db.query(Store).filter(Store.id == store_id).first()
    if store:
        update_data = store_update.model_dump(exclude_unset=True)

        # Convert base_url from Url type to string
        if 'base_url' in update_data:
            update_data['base_url'] = str(update_data['base_url'])

            # Update the favicon URL automatically
            domain = urlparse(update_data['base_url']).netloc
            update_data['favicon_url'] = f"https://www.google.com/s2/favicons?domain={domain}"

        # Handle image upload if requested
        if image_service:
            update_data['favicon_image_id'] = await image_service.process_store_image(update_data['name'], update_data['favicon_url'])

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
