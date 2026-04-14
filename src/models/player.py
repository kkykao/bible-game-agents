"""Player model for Bible Game"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models import Base


class Player(Base):
    """Player profile and progress tracking"""
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    language = Column(String(10), default="en")  # en, zh-TW
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    
    # Game progress
    level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    health = Column(Integer, default=100)
    
    # Learning stats
    theology_score = Column(Float, default=0.0)
    bible_knowledge = Column(Float, default=0.0)
    dialogue_count = Column(Integer, default=0)
    
    # Profile customization
    character_name = Column(String(255))
    avatar_url = Column(String(500))
    preferences = Column(JSON, default={})
    
    # Relationships
    quests = relationship("PlayerQuestProgress", back_populates="player", cascade="all, delete-orphan")
    dialogue_history = relationship("DialogueHistory", back_populates="player", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="player", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Player(id={self.id}, username={self.username}, level={self.level})>"
