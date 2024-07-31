from app.database import Base, engine
from app.models.store import Store

Base.metadata.create_all(bind=engine)
