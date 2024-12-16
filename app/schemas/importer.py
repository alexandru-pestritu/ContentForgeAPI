from pydantic import BaseModel
from typing import List, Optional, Dict

class ImportEntryResponse(BaseModel):
    data: Dict
    status: str
    error_message: Optional[str]

class ImportTaskResponse(BaseModel):
    task_id: str
    entity_type: str
    entries: List[ImportEntryResponse]
