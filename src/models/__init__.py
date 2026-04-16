"""SQLAlchemy models for the Bible Game"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Create Base class for all models
Base = declarative_base()

# Import all models to register them with Base
from .player import Player
from .quest import Quest, PlayerQuestProgress, QuestStatus
from .dialogue import DialogueHistory
from .game_state import GameState, Achievement
from .conversation import SavedConversation

__all__ = [
    "Base",
    "Player",
    "Quest",
    "PlayerQuestProgress",
    "QuestStatus",
    "DialogueHistory",
    "GameState",
    "Achievement",
    "SavedConversation",
]
