"""SQLAlchemy models for the Bible Game"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Create Base class for all models
Base = declarative_base()

# Import all models to register them with Base
from src.models.player import Player
from src.models.quest import Quest, PlayerQuestProgress, QuestStatus
from src.models.dialogue import DialogueHistory
from src.models.game_state import GameState, Achievement

__all__ = [
    "Base",
    "Player",
    "Quest",
    "PlayerQuestProgress",
    "QuestStatus",
    "DialogueHistory",
    "GameState",
    "Achievement",
]
