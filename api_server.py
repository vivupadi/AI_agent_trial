from fastapi import FastAPI, HTTPException
import requests
import colorsys
import pydantic
from typing import Optional, List

import sqlite3

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


from pydantic import BaseModel
from datetime import datetime
import uvicorn
import schedule

from weather_agent import WeatherEmailAgent

import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY= os.getenv('weather_api_key')

app = FastAPI(title= 'Weather app',
              version= '1.0.0')


#Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

# Database setup
DATABASE = "tasks.db"

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize the database with a tasks table"""
    with get_db() as conn:
        conn.execute("""
          
        """)

#Data models
class Reminder(BaseModel):
    email:str
    city:str
    country_code: str

class ReminderResponse(BaseModel):
    id: int
    email: str
    city: str
    country_code: str
    time: str
    enabled: bool
    created_at: str

# In-memory database (for learning - use real DB in production)
reminders_db: List[dict] = []
reminder_id_counter = 1


#classes to validate the data


@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "reminders_count": len(reminders_db)
    }

@app.post("/save", response_model = Reminder)

@app.post("/reminders", response_model = Reminder)
async def create_reminder(request: Reminder):

    agent = WeatherEmailAgent(OPENWEATHER_API_KEY, request.email, request.city, request.country_code)

    agent.run_check()

    schedule.every().day.at("08:30").do(agent.run_check)

    return {
        "success": True,
        "message": "Reminder created and email sent!",
        "email": request.email,
        "city": request.city,
        "country_code": request.country_code
    }


# ========== RUN LOCALLY ==========

if __name__ == "__main__":
    print("🌤️ Starting Weather Agent API...")
    print("📍 http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )