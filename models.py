from sqlalchemy import create_engine, Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey,DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://chatuser:admin123@localhost/chatdb")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

# Παράδειγμα μοντέλου
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    is_online = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False) 