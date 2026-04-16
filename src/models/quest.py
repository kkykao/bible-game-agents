"""Quest and progress models for Bible Game"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from . import Base


class QuestStatus(str, Enum):
    """Quest status enumeration"""
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


class Quest(Base):
    """Available quests in the game"""
    __tablename__ = "quests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    character_id = Column(String(50), nullable=False)  # jesus, david, solomon, etc.
    theology_topic = Column(String(255))
    difficulty_level = Column(Integer, default=1)
    reward_xp = Column(Integer, default=100)
    reward_points = Column(Integer, default=50)
    
    # Quest content
    objectives = Column(Text)  # JSON string with quest objectives
    dialogue_flow = Column(Text)  # JSON with dialogue nodes
    scripture_references = Column(Text)  # JSON array of verses
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player_progress = relationship("PlayerQuestProgress", back_populates="quest", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quest(id={self.id}, title={self.title}, character={self.character_id})>"


class PlayerQuestProgress(Base):
    """Track player progress on quests"""
    __tablename__ = "player_quest_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    quest_id = Column(Integer, ForeignKey("quests.id"), nullable=False, index=True)
    
    status = Column(SQLEnum(QuestStatus), default=QuestStatus.AVAILABLE)
    progress_percentage = Column(Float, default=0.0)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Dialogue choices and progress
    current_node = Column(Integer, default=0)
    dialogue_choices = Column(Text)  # JSON with player choices
    
    xp_earned = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    
    # Relationships
    player = relationship("Player", back_populates="quests")
    quest = relationship("Quest", back_populates="player_progress")
    
    def __repr__(self):
        return f"<PlayerQuestProgress(player={self.player_id}, quest={self.quest_id}, status={self.status})>"
