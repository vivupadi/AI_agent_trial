from fastapi import FastAPI, HTTPException
import requests
import colorsys
import pydantic


from pydantic import BaseModel
from datetime import datetime
import uvicorn


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

#Data models
class Reminder(BaseModel):
    email:str
    city:str
    time:str
    enabled: bool =True

class ReminderResponse(BaseModel):
    id: int
    email: str
    city: str
    time: str
    enabled: bool
    created_at: str

# In-memory database (for learning - use real DB in production)
reminders_db: List[dict] = []
reminder_id_counter = 1

class ReminderResponse(BaseModel):

classes to validate the data


@app.get("/")
async def root():
    return {
        "message": "Welcome to Weather Reminder API!",
        "docs": "/docs",
        "endpoints": {
            "GET /": "This welcome message",
            "GET /health": "Health check",
            "GET /reminders": "List all reminders",
            "POST /reminders": "Create new reminder",
            "GET /reminders/{id}": "Get specific reminder",
            "PUT /reminders/{id}": "Update reminder",
            "DELETE /reminders/{id}": "Delete reminder"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "reminders_count": len(reminders_db)
    }


    agent = WeatherEmailAgent(OPENWEATHER_API_KEY, CITY, COUNTRY_CODE)
    agent.run_check()

    schedule.every().day.at("16:49").do(agent.run_check)


