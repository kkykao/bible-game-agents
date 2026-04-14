"""Quest management system"""
import json
from sqlalchemy.orm import Session
from src.models import Quest, PlayerQuestProgress, QuestStatus
from datetime import datetime

# Sample quests
SAMPLE_QUESTS = [
    {
        "title": "The Way of Grace",
        "character_id": "jesus",
        "description": "Learn about God's grace through dialogue with Jesus",
        "theology_topic": "Soteriology",
        "difficulty_level": 1,
        "reward_xp": 100,
        "reward_points": 50,
        "objectives": ["Ask 3 questions about grace", "Learn about faith", "Understand redemption"],
        "scripture_references": ["John 3:16", "Romans 3:24", "Ephesians 2:8"],
    },
    {
        "title": "The Psalms of David",
        "character_id": "david",
        "description": "Explore the Psalms and their spiritual wisdom",
        "theology_topic": "Worship",
        "difficulty_level": 2,
        "reward_xp": 150,
        "reward_points": 75,
        "objectives": ["Learn about worship", "Understand repentance", "Practice prayer"],
        "scripture_references": ["Psalm 23:1", "Psalm 139:14"],
    },
    {
        "title": "Wisdom's Way",
        "character_id": "solomon",
        "description": "Discover the wisdom of Solomon",
        "theology_topic": "Epistemology",
        "difficulty_level": 2,
        "reward_xp": 150,
        "reward_points": 75,
        "objectives": ["Ask about wisdom", "Learn about fear of God", "Understand vanity"],
        "scripture_references": ["Proverbs 1:7", "Ecclesiastes 1:2"],
    },
    {
        "title": "The Ark and Faith",
        "character_id": "noah",
        "description": "Walk with Noah through faith and obedience",
        "theology_topic": "Faith",
        "difficulty_level": 1,
        "reward_xp": 100,
        "reward_points": 50,
        "objectives": ["Learn about obedience", "Understand God's covenant", "Explore faith"],
        "scripture_references": ["Genesis 6:9", "Hebrews 11:7"],
    },
    {
        "title": "The Law and Freedom",
        "character_id": "moses",
        "description": "Understand God's law through Moses",
        "theology_topic": "Bibliology",
        "difficulty_level": 3,
        "reward_xp": 200,
        "reward_points": 100,
        "objectives": ["Learn about the law", "Understand God's character", "Discover liberty"],
        "scripture_references": ["Exodus 20:1", "Deuteronomy 5:4"],
    },
]


def seed_quests(db: Session):
    """Seed database with sample quests"""
    # Check if quests already exist
    existing = db.query(Quest).first()
    if existing:
        return
    
    for quest_data in SAMPLE_QUESTS:
        quest = Quest(
            title=quest_data["title"],
            character_id=quest_data["character_id"],
            description=quest_data["description"],
            theology_topic=quest_data["theology_topic"],
            difficulty_level=quest_data["difficulty_level"],
            reward_xp=quest_data["reward_xp"],
            reward_points=quest_data["reward_points"],
            objectives=json.dumps(quest_data["objectives"]),
            scripture_references=json.dumps(quest_data["scripture_references"]),
        )
        db.add(quest)
    
    db.commit()


def get_available_quests(db: Session, player_id: int = None):
    """Get all available quests"""
    quests = db.query(Quest).all()
    result = []
    
    for quest in quests:
        quest_dict = {
            "id": quest.id,
            "title": quest.title,
            "character_id": quest.character_id,
            "description": quest.description,
            "difficulty_level": quest.difficulty_level,
            "reward_xp": quest.reward_xp,
            "reward_points": quest.reward_points,
            "theology_topic": quest.theology_topic,
            "objectives": json.loads(quest.objectives) if quest.objectives else [],
            "scripture_references": json.loads(quest.scripture_references) if quest.scripture_references else [],
        }
        
        # Add player progress if player_id provided
        if player_id:
            progress = db.query(PlayerQuestProgress).filter(
                PlayerQuestProgress.player_id == player_id,
                PlayerQuestProgress.quest_id == quest.id
            ).first()
            
            if progress:
                quest_dict["status"] = progress.status.value
                quest_dict["progress"] = progress.progress_percentage
                quest_dict["completed"] = progress.completed
            else:
                quest_dict["status"] = "available"
                quest_dict["progress"] = 0
                quest_dict["completed"] = False
        
        result.append(quest_dict)
    
    return result


def start_quest(db: Session, player_id: int, quest_id: int):
    """Start a quest for a player"""
    # Check if already in progress
    existing = db.query(PlayerQuestProgress).filter(
        PlayerQuestProgress.player_id == player_id,
        PlayerQuestProgress.quest_id == quest_id
    ).first()
    
    if existing:
        return {"status": "error", "message": "Quest already started"}
    
    # Create new progress
    progress = PlayerQuestProgress(
        player_id=player_id,
        quest_id=quest_id,
        status=QuestStatus.IN_PROGRESS,
        started_at=datetime.utcnow()
    )
    
    db.add(progress)
    db.commit()
    
    return {"status": "ok", "message": "Quest started"}


def update_quest_progress(
    db: Session,
    player_id: int,
    quest_id: int,
    progress_percentage: float = None,
    mark_complete: bool = False
):
    """Update quest progress"""
    quest_progress = db.query(PlayerQuestProgress).filter(
        PlayerQuestProgress.player_id == player_id,
        PlayerQuestProgress.quest_id == quest_id
    ).first()
    
    if not quest_progress:
        return {"status": "error", "message": "Quest progress not found"}
    
    if progress_percentage is not None:
        quest_progress.progress_percentage = min(100, max(0, progress_percentage))
    
    if mark_complete:
        quest_progress.status = QuestStatus.COMPLETED
        quest_progress.completed = True
        quest_progress.completed_at = datetime.utcnow()
        # Get quest for rewards
        quest = db.query(Quest).filter(Quest.id == quest_id).first()
        if quest:
            quest_progress.xp_earned = quest.reward_xp
    
    db.commit()
    return {"status": "ok", "message": "Quest progress updated"}
