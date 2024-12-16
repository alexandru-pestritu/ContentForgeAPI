import enum
from typing import List, Optional, Dict

class ImportStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class ImportEntry:
    def __init__(self, data: Dict):
        self.data = data
        self.status = ImportStatus.PENDING
        self.error_message: Optional[str] = None

class ImportTask:
    def __init__(self, task_id: str, entity_type: str):
        self.task_id = task_id
        self.entity_type = entity_type
        self.entries: List[ImportEntry] = []
