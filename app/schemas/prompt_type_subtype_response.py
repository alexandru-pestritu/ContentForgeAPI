from typing import Dict, List
from pydantic import BaseModel


class PromptTypeSubtypeResponse(BaseModel):
    types: Dict[str, List[str]]