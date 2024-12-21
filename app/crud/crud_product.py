import csv
from datetime import datetime, timezone
import io
import json
from sqlalchemy.orm import Session
from app.models.article import Article
from app.models.product import Product, ProductAffiliateURL, ProductSpecification, ProductPro, ProductCon, ProductImage
from app.models.store import Store
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

    stores = db.query(Store).filter(Store.id.in_(product.store_ids)).all()

    new_product = Product(
        name=product.name,
        seo_keyword=product.seo_keyword,
        rating=product.rating,
        in_stock=scraped_data.get('in_stock'),
        description=scraped_data.get('description'),
        full_name=scraped_data.get('full_name'),
        last_checked=datetime.now(timezone.utc),
        stores=stores
    )

    new_product.affiliate_urls = [ProductAffiliateURL(url=str(url)) for url in product.affiliate_urls]

    specifications = scraped_data.get('specifications', {})
    new_product.specifications = [ProductSpecification(spec_key=k, spec_value=v) for k, v in specifications.items()]
    
    
    image_urls = scraped_data.get('image_urls', [])
    new_product.images = [ProductImage(image_url=img_url) for img_url in image_urls]

    if image_service and new_product.images:
        for img_obj in new_product.images:
            wp_id = await image_service.process_image(
                entity_type="product",
                entity=new_product,
                image_url=img_obj.image_url
            )
            img_obj.wp_id = wp_id

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
    Retrieve products that are out of stock and the articles they are part of.
    """
    out_of_stock_products = db.query(Product).filter(Product.in_stock == False).all()
    result = []

    for product in out_of_stock_products:
        articles = product.articles
        result.append({
            "product": ProductResponse.from_orm(product),
            "articles": [ArticleResponse.from_orm(article) for article in articles]
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
    if not product:
        return None

    update_data = product_update.model_dump()

    for attr in ["in_stock", "full_name", "description", "review", "name", "seo_keyword", "rating"]:
        if attr in update_data and update_data[attr] is not None:
            setattr(product, attr, update_data[attr])

        if 'store_ids' in update_data and update_data['store_ids'] is not None:
            stores = db.query(Store).filter(Store.id.in_(update_data['store_ids'])).all()
            product.stores = stores

        if 'affiliate_urls' in update_data and update_data['affiliate_urls'] is not None:
            product.affiliate_urls.clear()
            product.affiliate_urls = [ProductAffiliateURL(url=str(url)) for url in update_data['affiliate_urls']]

        if 'specifications' in update_data and update_data['specifications'] is not None:
            product.specifications.clear()
            product.specifications = [
                ProductSpecification(spec_key=k, spec_value=v) for k, v in update_data['specifications'].items()]
             
        if 'pros' in update_data and update_data['pros'] is not None:
            product.pros.clear()
            product.pros = [ProductPro(text=pro) for pro in update_data['pros']]

        if 'cons' in update_data and update_data['cons'] is not None:
            product.cons.clear()
            product.cons = [ProductCon(text=con) for con in update_data['cons']]

        if 'image_urls' in update_data and update_data['image_urls'] is not None:
            new_image_urls = set(
                str(url) if str(url).startswith(('http://', 'https://')) else f"http://{str(url)}"
                for url in update_data['image_urls']
            )
            existing_images = {img.image_url: img for img in product.images}
            
            for url in new_image_urls:
                if url not in existing_images:
                    product.images.append(ProductImage(image_url=url))

            for existing_url, img_obj in list(existing_images.items()):
                if existing_url not in new_image_urls:
                    db.delete(img_obj)


        if image_service:
            for img_obj in product.images:
                wp_id = await image_service.process_image(
                    entity_type="product",
                    entity=product,
                    image_url=img_obj.image_url
                )
                img_obj.wp_id = wp_id

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