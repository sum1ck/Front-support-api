from sqlalchemy import create_engine, BigInteger, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


