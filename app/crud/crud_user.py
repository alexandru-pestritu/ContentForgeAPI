from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserBase
from app.core.security import get_password_hash
from typing import Optional

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_pw = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        name=user_data.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserBase) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    if user_update.email:
        db_user.email = user_update.email
    if user_update.name is not None:
        db_user.name = user_update.name
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
