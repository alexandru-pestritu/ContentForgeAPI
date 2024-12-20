from typing import Optional
from sqlalchemy.orm import Session
from app.models.settings import Setting
from app.schemas.settings import SettingBase, SettingCreate, SettingUpdate, SettingResponse

def get_setting_by_key(db: Session, key: str) -> Optional[SettingResponse]:
    """
    Returns a setting by its key.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        return SettingResponse.model_validate(setting)
    return None

def get_all_settings(db: Session) -> list[SettingResponse]:
    """
    Returns all settings.
    """
    settings = db.query(Setting).all()
    return [SettingResponse.model_validate(s) for s in settings]

def create_setting(db: Session, setting: SettingCreate) -> SettingResponse:
    """
    Creates a new setting.
    """
    SettingBase.validate_value(setting.type, setting.value)
    
    new_setting = Setting(
        key=setting.key,
        value=str(setting.value),
        type=setting.type,
        description=setting.description,
    )
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return SettingResponse.model_validate(new_setting)

def update_setting(db: Session, key: str, setting_update: SettingUpdate) -> Optional[SettingResponse]:
    """
    Updates a setting by its key.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        SettingBase.validate_value(setting.type, setting_update.value)
        
        setting.value = str(setting_update.value)
        db.commit()
        db.refresh(setting)
        return SettingResponse.model_validate(setting)
    return None

def delete_setting(db: Session, key: str) -> Optional[SettingResponse]:
    """
    Deletes a setting by its key.
    """
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        db.delete(setting)
        db.commit()
        return SettingResponse.model_validate(setting)
    return None
