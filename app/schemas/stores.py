from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class StoreBase(BaseModel):
    name: str
    base_url: HttpUrl
    favicon_image_id: Optional[int] = None
    favicon_url: Optional[HttpUrl] = None

class StoreCreate(StoreBase):
    pass

class StoreUpdate(StoreBase):
    name: Optional[str] = None
    base_url: Optional[HttpUrl] = None

class StoreResponse(StoreBase):
    id: int

    class Config:
        from_attributes = True
