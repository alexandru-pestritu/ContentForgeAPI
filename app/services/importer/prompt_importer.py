from typing import Tuple, Dict, Optional
from app.models.importer import ImportStatus
from .base_importer import BaseImporter
from app.schemas.prompt import PromptCreate
from app.crud.crud_prompt import create_prompt
from sqlalchemy.orm import Session

class PromptImporter(BaseImporter):
    def __init__(self, db: Session):
        self.db = db

    async def process_entry(self, data: Dict) -> Tuple[ImportStatus, Optional[str]]:
        if "name" not in data or not data["name"].strip():
            return (ImportStatus.FAILED, "Missing or empty name column")
        
        if "type" not in data or not data["type"].strip():
            return (ImportStatus.FAILED, "Missing or empty type column")
        
        if "subtype" not in data or not data["subtype"].strip():
            return (ImportStatus.FAILED, "Missing or empty subtype column")
        
        if "text" not in data or not data["text"].strip():
            return (ImportStatus.FAILED, "Missing or empty text column")

        prompt_create = PromptCreate(
            name=data["name"].strip(),
            type=data["type"].strip(),
            subtype=data["subtype"].strip(),
            text=data["text"].strip()
        )

        try:
            new_prompt = create_prompt(self.db, prompt_create)
            return (ImportStatus.SUCCESS, None)
        except Exception as e:
            return (ImportStatus.FAILED, str(e))
