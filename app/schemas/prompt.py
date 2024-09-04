from pydantic import BaseModel
from typing import Dict, List, Optional

class PromptBase(BaseModel):
    name: str
    type: str
    subtype: str
    text: str

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    text: Optional[str] = None

class PromptResponse(PromptBase):
    id: int

    class Config:
        from_attributes = True
