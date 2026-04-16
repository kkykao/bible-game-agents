"""Dialogue history model for Bible Game"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class DialogueHistory(Base):
    """Store conversation history between player and NPCs"""
    __tablename__ = "dialogue_history"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    quest_id = Column(Integer, ForeignKey("quests.id"))
    
    # Dialogue content
    character_id = Column(String(50), nullable=False)  # jesus, david, solomon, etc.
    player_message = Column(Text, nullable=False)
    character_response = Column(Text, nullable=False)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    dialogue_node = Column(Integer)  # Which node in the quest dialogue
    turn_number = Column(Integer)  # Conversation turn number
    
    # Theology tracking
    theology_accuracy = Column(Integer, default=0)  # 0-100 score
    kbible_reference_used = Column(String(255))  # e.g., "John 3:16"
    theology_lesson = Column(Text)  # Key teaching point
    
    # Relationships
    player = relationship("Player", back_populates="dialogue_history")
    
    def __repr__(self):
        return f"<DialogueHistory(id={self.id}, player={self.player_id}, character={self.character_id})>"
