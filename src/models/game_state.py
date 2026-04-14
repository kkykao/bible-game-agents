"""Game state and achievements models for Bible Game"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models import Base


class GameState(Base):
    """Track game session and global state"""
    __tablename__ = "game_states"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # game difficulty and parameters
    difficulty_level = Column(Integer, default=1)
    adaptive_difficulty_enabled = Column(Boolean, default=True)
    language = Column(String(10), default="en")  # en, zh-TW
    
    # Game rules and parameters
    game_parameters = Column(JSON, default={})
    theology_framework = Column(String(100), default="literalist")
    
    # Session metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Statistics
    total_playtime_minutes = Column(Integer, default=0)
    dialogues_completed = Column(Integer, default=0)
    quests_completed = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<GameState(id={self.id}, session={self.session_id}, difficulty={self.difficulty_level})>"


class Achievement(Base):
    """Player achievements and badges"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    
    # Achievement info
    achievement_id = Column(String(100), nullable=False)  # unique id like "theology_master"
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon_url = Column(String(500))
    
    # Requirements and conditions
    requirement_type = Column(String(100))  # quests_completed, level_reached, theology_score, etc.
    requirement_value = Column(Float)
    
    # Player progress
    unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime)
    progress = Column(Float, default=0.0)  # 0-100 completion percentage
    
    # Rewards
    bonus_xp = Column(Integer, default=0)
    bonus_points = Column(Integer, default=0)
    
    # Relationships
    player = relationship("Player", back_populates="achievements")
    
    def __repr__(self):
        return f"<Achievement(id={self.achievement_id}, title={self.title}, unlocked={self.unlocked})>"
