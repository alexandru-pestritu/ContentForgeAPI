from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    This function will yield a database session and ensure it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@event.listens_for(Session, "after_flush")
def delete_orphan_categories(session, flush_context):
    
    from app.models.article import Category 

    orphan_categories = session.query(Category).filter(
        ~Category.articles.any()
    ).all()

    for category in orphan_categories:
        session.delete(category)