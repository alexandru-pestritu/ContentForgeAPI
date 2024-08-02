from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from typing import List, Optional
from app.scrapers.scraper_factory import scraper_factory


def create_product(db: Session, product: ProductCreate) -> ProductResponse:
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
    )

    new_product.set_specifications(scraped_data.get('specifications', {}))
    new_product.set_image_urls(scraped_data.get('image_urls', []))

    new_product.set_store_ids(product.store_ids)
    new_product.set_affiliate_urls(product.affiliate_urls)

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return ProductResponse.from_orm(new_product)

def get_product_by_id(db: Session, product_id: int) -> Optional[ProductResponse]:
    """
    Retrieve a product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        return ProductResponse.from_orm(product)
    return None

def get_products(db: Session, skip: int = 0, limit: int = 10) -> List[ProductResponse]:
    """
    Retrieve a list of products, with pagination support.
    """
    products = db.query(Product).offset(skip).limit(limit).all()
    return [ProductResponse.from_orm(product) for product in products]

def update_product(
    db: Session, 
    product_id: int, 
    product_update: ProductUpdate
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

        for key, value in update_data.items():
            if key not in ('store_ids', 'affiliate_urls', 'specifications', 'pros', 'cons', 'image_urls', 'image_ids'):
                setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return ProductResponse.from_orm(product)
    return None

def delete_product(db: Session, product_id: int) -> Optional[ProductResponse]:
    """
    Delete a product by its ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return ProductResponse.from_orm(product)
    return None
