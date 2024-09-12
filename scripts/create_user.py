import os
from dotenv import load_dotenv
from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

load_dotenv()

db = SessionLocal()

def create_user(email: str, password: str, name: str = None):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"User with email {email} already exists.")
        return existing_user
    
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

email = os.getenv("APP_EMAIL")
password = os.getenv("APP_PASSWORD")
name = os.getenv("APP_NAME")

if not email or not password:
    raise ValueError("APP_EMAIL and APP_PASSWORD must be set in .env")

new_user = create_user(email, password, name)
print(f"User: {new_user.email}")
