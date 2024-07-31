from app.database import Base, engine
from app.models.store import Store
from app.models.user import User

Base.metadata.create_all(bind=engine)
