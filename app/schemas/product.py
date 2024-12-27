from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict
from app.models.product import Product

class ProductBase(BaseModel):
    name: str
    store_ids: List[int]
    affiliate_urls: List[HttpUrl]
    seo_keyword: Optional[str]
    rating: Optional[float]

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    in_stock: Optional[bool] 
    full_name : Optional[str]
    description: Optional[str]
    specifications: Optional[Dict[str, str]]
    image_urls: Optional[List[HttpUrl]]
    image_ids: Optional[List[int]]
    review: Optional[str]
    pros: Optional[List[str]]
    cons: Optional[List[str]]

class ProductResponse(ProductBase):
    id: int
    in_stock: Optional[bool] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    specifications: Optional[Dict[str, str]] = None
    image_urls: Optional[List[HttpUrl]] = None
    image_ids: Optional[List[int]] = None
    review: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None

    @classmethod
    def from_orm(cls, product: Product):
        return cls(
            id=product.id,
            blog_id=product.blog_id,
            name=product.name,
            store_ids=[store.id for store in product.stores],
            affiliate_urls=[HttpUrl(aff.url) for aff in product.affiliate_urls],
            seo_keyword=product.seo_keyword,
            rating=product.rating,
            in_stock=product.in_stock,
            full_name=product.full_name,
            description=product.description,
            specifications={spec.spec_key: spec.spec_value for spec in product.specifications},
            image_urls=[HttpUrl(img.image_url) for img in product.images],
            image_ids=[img.wp_id for img in product.images if img.wp_id is not None],
            review=product.review,
            pros=[pro.text for pro in product.pros],
            cons=[con.text for con in product.cons],
        )

    class Config:
        from_attributes = True
