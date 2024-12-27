from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class StoreBase(BaseModel):
    name: str
    base_url: HttpUrl

class StoreCreate(StoreBase):
    pass

class StoreUpdate(BaseModel):  
    name: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    favicon_image_id: Optional[int] = None
    favicon_url: Optional[HttpUrl] = None

class StoreResponse(StoreBase):
    id: int
    blog_id: int
    favicon_image_id: Optional[int] = None
    favicon_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True
