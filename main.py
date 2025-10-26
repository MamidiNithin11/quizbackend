from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from scraper import scrape_wikipedia
from database import init_db, SessionLocal, Quiz, save_quiz, engine
from llm_quiz_generator import generate_quiz_from_content
from models import QuizResponse

app = FastAPI(title="AI Wiki Quiz Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    print("Starting FastAPI server...")
    try:
        init_db()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT CURRENT_TIMESTAMP")).scalar()
            print(f"Database connected successfully at {result}")
            if engine.url.host:
                print(f"Connected host: {engine.url.host}")
    except Exception as e:
        print(f"Database connection failed: {e}")


'session'
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": " AI Quiz Generator Backend is Running!"}

@app.post("/generate_quiz", response_model=QuizResponse)
def generate_quiz(url: str, db: Session = Depends(get_db)):
    
    try:
        title, text = scrape_wikipedia(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scraping failed: {e}")
    try:
        quiz_dict = generate_quiz_from_content(title, text, url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {e}")
    try:
        new_quiz = save_quiz(db, url, title, text, quiz_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database save failed: {e}")
    if "id" in quiz_dict:
        del quiz_dict["id"]

    try:
        quiz_response = QuizResponse(
            id=new_quiz.id,  
            **quiz_dict      
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response validation failed: {e}")

    return quiz_response
@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    return [
        {
            "id": q.id,
            "title": q.title,
            "url": q.url,
            "date_generated": q.date_generated,
        }
        for q in quizzes
    ]
@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return {
        "id": q.id,
        "title": q.title,
        "url": q.url,
        "quiz_data": q.full_quiz_data,
    }
