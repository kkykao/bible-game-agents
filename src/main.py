"""Bible Learning Game - Main Entry Point"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from agents.character_agent import get_character_agent, get_all_characters, get_character_groups, get_characters_in_group, get_reference_sources
from models import Base, SavedConversation

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

class SaveConversationRequest(BaseModel):
    player_name: str
    character_id: str
    messages: list  # Array of message objects
    conversation_title: str = None  # Optional custom title

class ConversationSummary(BaseModel):
    id: int
    player_name: str
    character_id: str
    conversation_title: str = None
    created_at: str
    updated_at: str
    message_count: int

class LoadedConversation(BaseModel):
    id: int
    player_name: str
    character_id: str
    conversation_title: str = None
    messages: list
    created_at: str
    updated_at: str

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

@app.get("/api/groups")
async def get_groups():
    """Return character groups with descriptions"""
    groups = get_character_groups()
    return {
        "groups": groups
    }

@app.get("/api/groups/{group_id}")
async def get_group_characters(group_id: str):
    """Return all characters in a specific group"""
    group_data = get_characters_in_group(group_id)
    if not group_data:
        raise HTTPException(status_code=404, detail=f"Group '{group_id}' not found")
    return group_data

@app.get("/api/sources")
async def get_sources():
    """Return primary reference sources for character wisdom"""
    sources = get_reference_sources()
    return {
        "sources": sources
    }

@app.post("/api/dialogue")
async def send_dialogue(request: DialogueRequest):
    """Handle dialogue between player and character using Claude AI"""
    character_id = request.character_id.lower()
    
    try:
        # Get character agent
        agent = get_character_agent(character_id)
        
        # Get response from Claude through character agent
        # Returns dict with 'text' and 'illustrations' keys
        response_data = agent.get_dialogue_response(request.player_name, request.message)
        
        return {
            "response": response_data.get("text", ""),
            "illustrations": response_data.get("illustrations", []),
            "character": character_id,
            "theology_reference": "KJV 1611"
        }
    
    except Exception as e:
        print(f"Error in dialogue endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting response: {str(e)}")

@app.post("/api/conversations/save")
async def save_conversation(request: SaveConversationRequest, db: Session = Depends(get_db)):
    """Save a conversation to database"""
    try:
        # Create new conversation record
        conversation = SavedConversation(
            player_name=request.player_name,
            character_id=request.character_id.lower(),
            conversation_title=request.conversation_title or f"Chat with {request.character_id.capitalize()}"
        )
        
        # Serialize and save messages
        conversation.set_messages(request.messages)
        
        # Save to database
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return {
            "success": True,
            "conversation_id": conversation.id,
            "message": f"Conversation saved successfully"
        }
    
    except Exception as e:
        db.rollback()
        print(f"Error saving conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving conversation: {str(e)}")

@app.get("/api/conversations")
async def get_conversations(player_name: str, db: Session = Depends(get_db)):
    """Get all saved conversations for a player"""
    try:
        conversations = db.query(SavedConversation).filter(
            SavedConversation.player_name == player_name
        ).order_by(SavedConversation.updated_at.desc()).all()
        
        result = []
        for conv in conversations:
            messages = conv.get_messages()
            result.append({
                "id": conv.id,
                "player_name": conv.player_name,
                "character_id": conv.character_id,
                "conversation_title": conv.conversation_title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": len(messages)
            })
        
        return {"conversations": result}
    
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching conversations: {str(e)}")

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Load a specific saved conversation"""
    try:
        conversation = db.query(SavedConversation).filter(
            SavedConversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "id": conversation.id,
            "player_name": conversation.player_name,
            "character_id": conversation.character_id,
            "conversation_title": conversation.conversation_title,
            "messages": conversation.get_messages(),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading conversation: {str(e)}")

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Delete a saved conversation"""
    try:
        conversation = db.query(SavedConversation).filter(
            SavedConversation.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        db.delete(conversation)
        db.commit()
        
        return {"success": True, "message": "Conversation deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
