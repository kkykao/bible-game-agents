"""Bible Learning Game - Main Entry Point"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.agents.character_agent import get_character_agent, get_all_characters
from src.models import Base

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./game.db")
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bible Learning Game API",
    description="AI agents for biblical learning",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request/Response Models
class DialogueRequest(BaseModel):
    player_name: str
    character_id: str
    message: str

class DialogueResponse(BaseModel):
    response: str
    character: str
    theology_reference: str = None

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Bible Game API is running"}

@app.get("/api/characters")
async def get_characters():
    """Return list of available biblical characters"""
    characters = get_all_characters()
    return {
        "characters": characters
    }

@app.post("/api/dialogue")
async def send_dialogue(request: DialogueRequest):
    """Handle dialogue between player and character using Claude AI"""
    character_id = request.character_id.lower()
    
    try:
        # Get character agent
        agent = get_character_agent(character_id)
        
        # Get response from Claude through character agent
        response_text = agent.get_dialogue_response(request.player_name, request.message)
        
        return {
            "response": response_text,
            "character": character_id,
            "theology_reference": "KJV 1611"
        }
    
    except Exception as e:
        print(f"Error in dialogue endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting response: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
