from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict

class ProductBase(BaseModel):
    store_ids: Optional[List[int]]
    affiliate_urls: Optional[List[HttpUrl]]
    seo_keyword: Optional[str]
    rating: Optional[float]

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str]
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
    name: str
    in_stock: bool
    description: str
    specifications: Dict[str, str]
    image_urls: List[HttpUrl]
    image_ids: List[int]
    review: str
    pros: List[str]
    cons: List[str]

    class Config:
        from_attributes = True
