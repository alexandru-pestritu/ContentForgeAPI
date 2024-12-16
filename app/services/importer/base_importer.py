from typing import Optional, Tuple, Dict
from app.models.importer import ImportStatus

class BaseImporter:
    async def process_entry(self, data: Dict) -> Tuple[ImportStatus, Optional[str]]:
        raise NotImplementedError
