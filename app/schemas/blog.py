from pydantic import BaseModel, HttpUrl
from typing import Optional

class BlogBase(BaseModel):
    name: str
    base_url: HttpUrl
    username: str
    api_key: str
    logo_url: Optional[HttpUrl] = None

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    username: Optional[str] = None
    api_key: Optional[str] = None
    logo_url: Optional[HttpUrl] = None

class BlogResponse(BlogBase):
    id: int

    class Config:
        from_attributes = True
