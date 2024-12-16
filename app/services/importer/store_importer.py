from typing import Tuple, Dict, Optional
from app.models.importer import ImportStatus
from .base_importer import BaseImporter
from app.schemas.stores import StoreCreate
from app.crud.crud_store import create_store
from sqlalchemy.orm import Session
from app.services.wordpress_service import WordPressService
from app.services.image_service import ImageService

class StoreImporter(BaseImporter):
    def __init__(self, db: Session):
        self.db = db

    async def process_entry(self, data: Dict) -> Tuple[ImportStatus, Optional[str]]:
        if "name" not in data:
            return (ImportStatus.FAILED, "Missing name column")
        
        if "base_url" not in data:
            return (ImportStatus.FAILED, "Missing base_url column")
        
        if not data["name"].strip():
            return (ImportStatus.FAILED, "Empty name value")
        
        if not data["base_url"].strip():
            return (ImportStatus.FAILED, "Empty base_url value")
        
        store_create = StoreCreate(name=data["name"], base_url=data["base_url"])

        upload_wp_str = data.get("upload_to_wordpress", "").strip().lower()
        if upload_wp_str == "true":
            wordpress_service = WordPressService()
            image_service = ImageService(wordpress_service)
        else:
            image_service = None

        try:
            await create_store(self.db, store_create, image_service=image_service)
            return (ImportStatus.SUCCESS, None)
        except Exception as e:
            return (ImportStatus.FAILED, str(e))
