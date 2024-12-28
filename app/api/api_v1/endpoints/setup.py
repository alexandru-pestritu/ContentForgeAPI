from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db

from app.crud.crud_setup import (
    get_setup_status,
    complete_setup,
    is_setup_completed,
    update_step
)
from app.schemas.settings import SettingUpdate
from app.schemas.setup_status import SetupStatusResponse
from app.crud import crud_user, crud_blog, crud_settings
from app.schemas.user import UserCreate
from app.schemas.blog import BlogCreate

router = APIRouter()

@router.get("/status", response_model=SetupStatusResponse)
def read_setup_status(db: Session = Depends(get_db)):
    return get_setup_status(db)

@router.post("/step1", status_code=201)
def setup_step1_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    if is_setup_completed(db):
        raise HTTPException(status_code=400, detail="Setup already completed.")
    
    existing = crud_user.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already used.")

    crud_user.create_user(db, user_data)

    update_step(db, 2)

    return {"detail": "User created. Step1 done."}

@router.post("/step2", status_code=201)
def setup_step2_api_keys(
    crawlbase_api_key: str,
    scrapingfish_api_key: str,
    edenai_api_key: str,
    db: Session = Depends(get_db)
):
    if is_setup_completed(db):
        raise HTTPException(status_code=400, detail="Setup already completed.")

    crud_settings.update_setting(
        db, 
        key="scraping.api.crawlbase_api_key", 
        setting_update=SettingUpdate(value=crawlbase_api_key)
    )

    crud_settings.update_setting(
        db, 
        key="scraping.api.scrapingfish_api_key", 
        setting_update=SettingUpdate(value=scrapingfish_api_key)
    )

    crud_settings.update_setting(
        db, 
        key="ai.api.edenai_api_key", 
        setting_update=SettingUpdate(value=edenai_api_key)
    )

    update_step(db, 3)

    return {"detail": "API keys set. Step2 done."}

@router.post("/step3", status_code=201)
def setup_step3_first_blog(
    blog_data: BlogCreate,
    db: Session = Depends(get_db)
):
    if is_setup_completed(db):
        raise HTTPException(status_code=400, detail="Setup already completed.")

    new_blog = crud_blog.create_blog(db, blog_data)

    update_step(db, 4)

    return {"detail": "First blog created.", "blog_id": new_blog.id}

@router.post("/complete", response_model=SetupStatusResponse)
def finalize_setup(db: Session = Depends(get_db)):
    if is_setup_completed(db):
        raise HTTPException(status_code=400, detail="Setup already completed.")

    return complete_setup(db)
