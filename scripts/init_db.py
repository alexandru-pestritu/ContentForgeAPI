from app.database import Base, engine
from app.models.store import Store
from app.models.user import User
from app.models.product import Product
from app.models.article import Article
from app.models.prompt import Prompt

Base.metadata.create_all(bind=engine)
