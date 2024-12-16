import asyncio
import csv
from io import StringIO
from uuid import uuid4
from app.schemas.importer import ImportEntryResponse, ImportTaskResponse
from .task_manager import task_manager
from app.models.importer import ImportStatus
from .websocket_manager import websocket_manager
from .store_importer import StoreImporter
from .product_importer import ProductImporter
from .article_importer import ArticleImporter
from .prompt_importer import PromptImporter
from sqlalchemy.orm import Session

IMPORTERS = {
    "store": StoreImporter,
    "product": ProductImporter,
    "article": ArticleImporter,
    "prompt": PromptImporter
}


class ImporterService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, entity_type: str, csv_file_content: str):
        task_id = str(uuid4())
        task = task_manager.create_task(task_id, entity_type)

        f = StringIO(csv_file_content)
        reader = csv.DictReader(f)
        data = list(reader)

        task_manager.add_entries_to_task(task_id, data)
        return task_id, data

    async def process_task(self, task_id: str):
        await asyncio.sleep(1) 
        task = task_manager.get_task(task_id)
        if not task:
            return

        importer_cls = IMPORTERS.get(task.entity_type)
        if not importer_cls:
            return

        importer = importer_cls(self.db)

        for i, entry in enumerate(task.entries):
            if entry.status == ImportStatus.PENDING:
                status, error = await importer.process_entry(entry.data)
                task_manager.update_entry_status(task_id, i, status, error)
                await websocket_manager.broadcast_task_update(task_id, {
                    "type": "entry_update",
                    "entry_index": i,
                    "status": status.value,
                    "error_message": error
                })

        final_status = [e.status.value for e in task.entries]
        await websocket_manager.broadcast_task_update(task_id, {
            "type": "task_complete",
            "final_status": final_status
        })

    def get_task_response(self, task_id: str):
        task = task_manager.get_task(task_id)
        if not task:
            return None

        return ImportTaskResponse(
            task_id=task_id,
            entity_type=task.entity_type,
            entries=[
                ImportEntryResponse(
                    data=e.data,
                    status=e.status.value,
                    error_message=e.error_message
                ) for e in task.entries
            ]
        )

    async def retry_failed_entries(self, task_id: str):
        task = task_manager.get_task(task_id)
        if not task:
            return
        for entry in task.entries:
            if entry.status == ImportStatus.FAILED:
                entry.status = ImportStatus.PENDING
                entry.error_message = None
        await self.process_task(task_id)