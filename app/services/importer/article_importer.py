from typing import Tuple, Dict, Optional
from app.models.importer import ImportStatus
from .base_importer import BaseImporter
from app.schemas.article import ArticleCreate
from app.crud.crud_article import create_article
from sqlalchemy.orm import Session
from app.services.wordpress_service import WordPressService
from app.services.image_service import ImageService

class ArticleImporter(BaseImporter):
    def __init__(self, db: Session, blog_id: int):
        self.db = db
        self.blog_id = blog_id

    async def process_entry(self, data: Dict) -> Tuple[ImportStatus, Optional[str]]:
        if "title" not in data or not data["title"].strip():
            return (ImportStatus.FAILED, "Missing or empty title column")

        if "slug" not in data or not data["slug"].strip():
            return (ImportStatus.FAILED, "Missing or empty slug column")

        seo_keywords = None
        if "seo_keywords" in data and data["seo_keywords"].strip():
            seo_keywords = [kw.strip() for kw in data["seo_keywords"].split(",") if kw.strip()]

        categories_id_list = None
        if "categories_id_list" in data and data["categories_id_list"].strip():
            categories_id_list = [int(x) for x in data["categories_id_list"].split(",") if x.strip().isdigit()]

        products_id_list = None
        if "products_id_list" in data and data["products_id_list"].strip():
            products_id_list = [int(x) for x in data["products_id_list"].split(",") if x.strip().isdigit()]

        article_create = ArticleCreate(
            title=data["title"].strip(),
            slug=data["slug"].strip(),
            categories_id_list=categories_id_list,
            author_id=int(data["author_id"]) if "author_id" in data and data["author_id"].isdigit() else None,
            status=data.get("status", "draft").strip(),
            seo_keywords=seo_keywords,
            meta_title=data.get("meta_title", None),
            meta_description=data.get("meta_description", None),
            main_image_url=data.get("main_image_url", None),
            buyers_guide_image_url=data.get("buyers_guide_image_url", None),
            products_id_list=products_id_list
        )

        upload_wp_str = data.get("upload_to_wordpress", "").strip().lower()
        if upload_wp_str == "true":
            wordpress_service = WordPressService(db=self.db, blog_id=self.blog_id)
            image_service = ImageService(wordpress_service)
        else:
            image_service = None

        try:
            await create_article(db=self.db, blog_id=self.blog_id, article=article_create, image_service=image_service)
            return (ImportStatus.SUCCESS, None)
        except Exception as e:
            return (ImportStatus.FAILED, str(e))
