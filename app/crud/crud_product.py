import csv
from datetime import datetime, timezone
import io
import json
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.product import Product
from app.schemas.article import ArticleResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from typing import Any, Dict, List, Optional
from app.scrapers.scraper_factory import scraper_factory
from app.services.image_metadata_service import ImageMetadataService
from app.services.image_service import ImageService


async def create_product(
    db: Session, 
    product: ProductCreate, 
    image_service: Optional[ImageService] = None
    ) -> ProductResponse:
    """
    Create a new product record in the database.
    """
    scraper = scraper_factory(str(product.affiliate_urls[0]))
    scraped_data = scraper.scrape_product_data()

    new_product = Product(
        name=product.name,
        seo_keyword=product.seo_keyword,
        rating=product.rating,
        in_stock=scraped_data.get('in_stock'),
        description=scraped_data.get('description'),
        full_name=scraped_data.get('full_name'),
        last_checked=datetime.now(timezone.utc)
    )

    new_product.set_specifications(scraped_data.get('specifications', {}))
    new_product.set_image_urls(scraped_data.get('image_urls', []))
    new_product.set_store_ids(product.store_ids)
    new_product.set_affiliate_urls(product.affiliate_urls)

    if image_service:
        image_metadata_service = ImageMetadataService()
        image_ids = []
        for index, image_url in enumerate(new_product.get_image_urls()):
            image_filename, alt_text = image_metadata_service.generate_product_metadata(new_product.name, new_product.seo_keyword, new_product.full_name, index + 1)
            image_path = await image_service.download_image(image_url)
            processed_image_path = image_service.set_image_metadata(image_path, new_file_name=image_filename)
            image_id = await image_service.upload_image_to_wordpress(processed_image_path, image_filename, alt_text)
            image_ids.append(image_id)

        new_product.set_image_ids(image_ids)

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return ProductResponse.from_orm(new_product)

def get_product_by_id(
    db: Session, 
    product_id: int
    ) -> Optional[ProductResponse]:
    """
    Retrieve a product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        return ProductResponse.from_orm(product)
    return None

def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    sort_field: Optional[str] = None,
    sort_order: Optional[int] = None,
    filter: Optional[str] = None
) -> dict:
    """
    Retrieve a list of products, with pagination support, sorting, filtering, and total records.
    """
    query = db.query(Product)

    if filter:
        filter_pattern = f"%{filter}%"
        query = query.filter(
            Product.name.ilike(filter_pattern) |
            Product.seo_keyword.ilike(filter_pattern)
        )

    if sort_field:
        if sort_order == -1:
            query = query.order_by(getattr(Product, sort_field).desc())
        else:
            query = query.order_by(getattr(Product, sort_field).asc())

    total_records = query.count()
    products = query.offset(skip).limit(limit).all()

    return {
        "products": [ProductResponse.from_orm(product) for product in products],
        "total_records": total_records
    }


def get_out_of_stock_products_with_articles(db: Session) -> List[Dict[str, Any]]:
    """
    Retrieve products that are out of stock and the articles they are part of, using a single query for articles.
    """
    out_of_stock_products = db.query(Product).filter(Product.in_stock == False).all()

    articles = db.query(Article).all()

    article_product_map = {}

    for article in articles:
        product_ids = article.get_products_id_list()  

        for product_id in product_ids:
            if product_id not in article_product_map:
                article_product_map[product_id] = []
            article_product_map[product_id].append(article)

    result = []

    for product in out_of_stock_products:
        related_articles = article_product_map.get(product.id, [])

        result.append({
            "product": ProductResponse.from_orm(product),
            "articles": [ArticleResponse.from_orm(article) for article in related_articles]
        })

    return result


async def update_product(
    db: Session, 
    product_id: int, 
    product_update: ProductUpdate, 
    image_service: Optional[ImageService] = None
    ) -> Optional[ProductResponse]:
    """
    Update an existing product record.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        update_data = product_update.model_dump()

        if 'store_ids' in update_data:
            product.set_store_ids(update_data['store_ids'])
        if 'affiliate_urls' in update_data:
            product.set_affiliate_urls(update_data['affiliate_urls'])
        if 'specifications' in update_data:
            product.set_specifications(update_data['specifications'])
        if 'pros' in update_data:
            product.set_pros(update_data['pros'])
        if 'cons' in update_data:
            product.set_cons(update_data['cons'])
        if 'image_urls' in update_data:
            product.set_image_urls(update_data['image_urls'])
        if 'image_ids' in update_data:
            product.set_image_ids(update_data['image_ids'])

        if image_service:
            image_metadata_service = ImageMetadataService()
            image_ids = []
            for index, image_url in enumerate(product.get_image_urls()):
                image_filename, alt_text = image_metadata_service.generate_product_metadata(product.name, product.seo_keyword, product.full_name, index + 1)
                image_path = await image_service.download_image(image_url)
                processed_image_path = image_service.set_image_metadata(image_path, new_file_name=image_filename)
                image_id = await image_service.upload_image_to_wordpress(processed_image_path, image_filename, alt_text)
                image_ids.append(image_id)

            product.set_image_ids(image_ids)

        for key, value in update_data.items():
            if key not in ('store_ids', 'affiliate_urls', 'specifications', 'pros', 'cons', 'image_urls', 'image_ids'):
                setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return ProductResponse.from_orm(product)
    return None

def delete_product(
    db: Session, 
    product_id: int
    ) -> Optional[ProductResponse]:
    """
    Delete a product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return ProductResponse.from_orm(product)
    return None