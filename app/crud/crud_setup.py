from sqlalchemy.orm import Session
from app.models.setup_status import SetupStatus
from app.schemas.setup_status import SetupStatusResponse

def get_setup_status(db: Session) -> SetupStatusResponse:
    status_obj = db.query(SetupStatus).first()
    if not status_obj:
        status_obj = SetupStatus(setup_completed=False, current_step=1)
        db.add(status_obj)
        db.commit()
        db.refresh(status_obj)
    return SetupStatusResponse.model_validate(status_obj)

def is_setup_completed(db: Session) -> bool:
    status_obj = db.query(SetupStatus).first()
    if not status_obj:
        return False
    return status_obj.setup_completed

def update_step(db: Session, step: int) -> SetupStatusResponse:
    """
    Updates the current step of the setup process.
    """
    status_obj = db.query(SetupStatus).first()
    if not status_obj:
        status_obj = SetupStatus(setup_completed=False, current_step=1)
        db.add(status_obj)
    
    status_obj.current_step = step
    db.commit()
    db.refresh(status_obj)
    return SetupStatusResponse.model_validate(status_obj)

def complete_setup(db: Session) -> SetupStatusResponse:
    """
    Marks the setup process as completed.
    """
    status_obj = db.query(SetupStatus).first()
    if not status_obj:
        status_obj = SetupStatus()
        db.add(status_obj)
    
    status_obj.setup_completed = True
    db.commit()
    db.refresh(status_obj)
    return SetupStatusResponse.model_validate(status_obj)
