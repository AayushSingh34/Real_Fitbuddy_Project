import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List
from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# --- 1. SETUP & CONFIGURATION ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FitnessApp")

app = FastAPI()

# VERY IMPORTANT: Allow your frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your frontend's actual URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DATABASE SETUP ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./fitness.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    weight = Column(Float)
    gender = Column(String)
    diet = Column(String)
    goal = Column(String)
    intensity = Column(String)

class DBWorkoutPlan(Base):
    __tablename__ = "workout_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer) # Simplified for this example
    plan_data = Column(JSON)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- 3. AI SETUP ---
try:
    client = genai.Client()
except Exception as e:
    logger.error(f"Gemini client error: {e}")
    client = None

# --- 4. PYDANTIC SCHEMAS ---
class UserProfile(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    age: int = Field(..., ge=12, lt=100)
    weight: float = Field(..., gt=20.0, lt=300.0)
    gender: Literal["male", "female"]
    diet: Literal["vegetarian", "non-vegetarian"]
    goal: Literal["weight_loss", "muscle_gain", "endurance"]
    intensity: Literal["low", "medium", "high"]

class DailyWorkout(BaseModel):
    day: str
    focus: str
    exercises: List[str]
    duration_minutes: int
    calories_burned: int
    diet_plan: str
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    total_calories: int

class NutritionAndRecovery(BaseModel):
    daily_calories_target: int
    macro_split: str
    nutrition_tips: List[str]
    recovery_tips: List[str]

class CompleteFitnessPlan(BaseModel):
    workout_schedule: List[DailyWorkout]
    lifestyle_guide: NutritionAndRecovery

# --- 5. ENDPOINTS ---
@app.post("/users/")
def create_user_and_plan(profile: UserProfile, db: Session = Depends(get_db)):
    logger.info(f"Generating plan for {profile.name}...")
    
    # Save User
    db_user = DBUser(**profile.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Call AI
    prompt = f"""
    Create a detailed 7-day fitness and lifestyle plan for: {profile.model_dump()}.
    Goal: {profile.goal}. Intensity: {profile.intensity}.
    Gender: {profile.gender}. Diet Preference: {profile.diet}.
    
    IMPORTANT: Create diet plans that are STRICTLY {profile.diet}:
    - If vegetarian: Use only vegetarian foods (no meat, fish, poultry)
    - If non-vegetarian: Include meat, fish, poultry options
    
    For each day, provide:
    - Day number (Day 1, Day 2, etc.)
    - Focus area (e.g., Upper Body, Cardio, etc.)
    - List of specific exercises (e.g., Push-ups, Running, Squats)
    - Duration in minutes
    - Estimated calories burned during workout
    - Diet plan for that day (brief meal overview) - MUST match {profile.diet} preference
    - Protein intake in grams
    - Carbohydrates intake in grams  
    - Fat intake in grams
    - Total calories for the day
    
    Do not include any medical, legal, or generic disclaimers; just deliver the actionable plan.
    Return the data in a structured JSON format.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=CompleteFitnessPlan,
                temperature=0.3
            ),
        )
        logger.debug(f"AI raw response text: {response.text}")
        try:
            ai_plan = json.loads(response.text)
            logger.info(f"Plan parsed successfully. Number of days: {len(ai_plan.get('workout_schedule', []))}")
        except Exception as e:
            logger.error(f"JSON parsing error: {e}\nResponse text: {response.text}")
            # if the model returns plain text instead of JSON, just wrap it
            ai_plan = {"text": response.text}
    except Exception as e:
        logger.error(f"AI Error: {e}")
        raise HTTPException(status_code=502, detail=f"AI generation failed: {str(e)}")

    # Save Plan
    db_plan = DBWorkoutPlan(user_id=db_user.id, plan_data=ai_plan)
    db.add(db_plan)
    db.commit()

    logger.info("Plan successfully created and saved.")
    return {"message": "Success!", "plan": ai_plan}

# --- Feedback Endpoint ---
class FeedbackModel(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    realism: str
    comment: str
    timestamp: str

@app.post("/feedback/")
def submit_feedback(feedback: FeedbackModel):
    logger.info(f"Feedback received - Rating: {feedback.rating}/5, Realism: {feedback.realism}, Comment: {feedback.comment[:50]}...")
    return {"message": "Feedback saved successfully!"}

# --- 6. ERROR HANDLERS ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(status_code=500, content={"message": "Internal Server Error"})