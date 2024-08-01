from app.database import Base, engine
from app.models.store import Store
from app.models.user import User
from app.models.product import Product

Base.metadata.create_all(bind=engine)
