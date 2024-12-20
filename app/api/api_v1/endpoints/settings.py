from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.settings import SettingCreate, SettingUpdate, SettingResponse
from app.crud.crud_settings import (
    get_setting_by_key,
    get_all_settings,
    create_setting,
    update_setting,
    delete_setting,
)
from app.models.user import User  
from app.dependencies.auth import get_current_user  

router = APIRouter()

@router.get("/", response_model=list[SettingResponse])
def read_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    """
    Returns all settings.
    """
    return get_all_settings(db)

@router.get("/{key}", response_model=SettingResponse)
def read_setting(
    key: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    """
    Returns a setting by its key.
    """
    setting = get_setting_by_key(db, key)
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.post("/", response_model=SettingResponse)
def create_new_setting(
    setting: SettingCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    """
    Creates a new setting.
    """
    existing_setting = get_setting_by_key(db, setting.key)
    if existing_setting:
        raise HTTPException(status_code=400, detail="Setting with this key already exists")
    return create_setting(db, setting)

@router.put("/{key}", response_model=SettingResponse)
def update_existing_setting(
    key: str, 
    setting_update: SettingUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    """
    Updates a setting by its key.
    """
    updated_setting = update_setting(db, key, setting_update)
    if not updated_setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return updated_setting

@router.delete("/{key}", response_model=SettingResponse)
def delete_existing_setting(
    key: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    """
    Deletes a setting by its key.
    """
    deleted_setting = delete_setting(db, key)
    if not deleted_setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return deleted_setting
