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
            name=product.name,
            store_ids=product.get_store_ids(),
            affiliate_urls=product.get_affiliate_urls(),
            seo_keyword=product.seo_keyword,
            rating=product.rating,
            in_stock=product.in_stock,
            description=product.description,
            specifications=product.get_specifications(),
            image_urls=product.get_image_urls(),
            image_ids=product.get_image_ids(),
            review=product.review,
            pros=product.get_pros(),
            cons=product.get_cons(),
        )

    class Config:
        from_attributes = True
