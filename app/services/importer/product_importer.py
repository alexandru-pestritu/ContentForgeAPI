from typing import Tuple, Dict, Optional
from app.models.importer import ImportStatus
from .base_importer import BaseImporter
from app.schemas.product import ProductCreate
from app.crud.crud_product import create_product
from sqlalchemy.orm import Session
from app.services.wordpress_service import WordPressService
from app.services.image_service import ImageService

class ProductImporter(BaseImporter):
    def __init__(self, db: Session):
        self.db = db

    async def process_entry(self, data: Dict) -> Tuple[ImportStatus, Optional[str]]:
        if "name" not in data or not data["name"].strip():
            return (ImportStatus.FAILED, "Missing or empty name column")
        
        if "store_ids" not in data:
            return (ImportStatus.FAILED, "Missing store_ids column")
        if not data["store_ids"]:
            return (ImportStatus.FAILED, "No store_ids provided")

        if "affiliate_urls" not in data or not data["affiliate_urls"]:
            return (ImportStatus.FAILED, "Missing or empty affiliate_urls column")

        store_ids_str = data["store_ids"].strip()
        affiliate_urls_str = data["affiliate_urls"].strip()

        store_ids = [int(s) for s in store_ids_str.split(",") if s.strip().isdigit()]
        affiliate_urls = [url.strip() for url in affiliate_urls_str.split(",") if url.strip()]

        if not store_ids:
            return (ImportStatus.FAILED, "Invalid store_ids format or empty list")
        if not affiliate_urls:
            return (ImportStatus.FAILED, "Invalid affiliate_urls format or empty list")

        product_create = ProductCreate(
            name=data["name"].strip(),
            store_ids=store_ids,
            affiliate_urls=affiliate_urls,
            seo_keyword=data.get("seo_keyword", None),
            rating=float(data.get("rating", 0.0)) if data.get("rating") else None
        )

        upload_wp_str = data.get("upload_to_wordpress", "").strip().lower()
        if upload_wp_str == "true":
            wordpress_service = WordPressService()
            image_service = ImageService(wordpress_service)
        else:
            image_service = None

        try:
            await create_product(self.db, product_create, image_service=image_service)
            return (ImportStatus.SUCCESS, None)
        except Exception as e:
            return (ImportStatus.FAILED, str(e))
