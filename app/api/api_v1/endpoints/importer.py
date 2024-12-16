from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.services.importer.importer_service import ImporterService
from app.schemas.importer import ImportTaskResponse

router = APIRouter()

@router.post("/")
async def import_entities(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    entity_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Import entities of the given type from a CSV file.
    """
    importer = ImporterService(db)
    content = (await file.read()).decode("utf-8")
    task_id, entries_data = importer.create_task(entity_type, content)
    background_tasks.add_task(importer.process_task, task_id)
    return {"task_id": task_id, "entries": entries_data}

@router.post("/{task_id}/retry", response_model=ImportTaskResponse)
async def retry_import_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    entity_type: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retry the failed entries for a given import task and entity type.
    """
    importer = ImporterService(db)
    background_tasks.add_task(importer.retry_failed_entries, task_id)
    return importer.get_task_response(task_id)
