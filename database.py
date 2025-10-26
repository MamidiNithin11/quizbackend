import os
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True, nullable=False)
    title = Column(String, nullable=True)
    date_generated = Column(DateTime, default=datetime.utcnow)
    scraped_content = Column(Text, nullable=True)  
    full_quiz_data = Column(Text, nullable=True)   
def init_db():
    """Create tables in the database."""
    Base.metadata.create_all(bind=engine)

def save_quiz(session, url, title, scraped_content, quiz_dict):
    """Helper function to save a quiz into the database."""
    q = Quiz(
        url=url,
        title=title,
        scraped_content=scraped_content,
        full_quiz_data=json.dumps(quiz_dict, ensure_ascii=False),
    )
    session.add(q)
    session.commit()
    session.refresh(q)
    return q
