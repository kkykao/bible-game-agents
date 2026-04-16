"""Conversation model for saving and loading character dialogues"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from datetime import datetime
import json
from . import Base


class SavedConversation(Base):
    """Store saved conversations between player and characters"""
    __tablename__ = "saved_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metadata
    player_name = Column(String(100), nullable=False, index=True)
    character_id = Column(String(50), nullable=False, index=True)
    conversation_title = Column(String(255), nullable=True)  # Custom name if provided
    
    # Content (stored as JSON)
    messages_json = Column(Text, nullable=False)  # JSON array of message objects
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Index for common queries
    __table_args__ = (
        Index('idx_player_character', 'player_name', 'character_id'),
        Index('idx_player_name', 'player_name'),
    )
    
    def set_messages(self, messages: list):
        """Serialize messages to JSON"""
        self.messages_json = json.dumps(messages)
    
    def get_messages(self) -> list:
        """Deserialize messages from JSON"""
        if not self.messages_json:
            return []
        try:
            return json.loads(self.messages_json)
        except json.JSONDecodeError:
            return []
    
    def __repr__(self):
        return f"<SavedConversation(id={self.id}, player={self.player_name}, character={self.character_id})>"
