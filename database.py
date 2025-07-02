from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from models import SessionLocal

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # .env: postgresql://chatuser:admin123@localhost:5432/chatdb

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
