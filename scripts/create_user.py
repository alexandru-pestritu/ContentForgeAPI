from app.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()

def create_user(email: str, password: str, name: str = None):
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        name=name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

email = "admin@example.com"
password = "admin"
name = "Admin User"

new_user = create_user(email, password, name)
print(f"Created user: {new_user.email}")
