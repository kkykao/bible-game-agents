"""Achievement system for tracking player accomplishments"""
from sqlalchemy.orm import Session
from models import Achievement, Player
from datetime import datetime

# Sample achievements
SAMPLE_ACHIEVEMENTS = [
    {
        "achievement_id": "first_steps",
        "title": "First Steps",
        "description": "Have your first dialogue with a biblical character",
        "requirement_type": "dialogues_completed",
        "requirement_value": 1,
        "bonus_xp": 10,
        "bonus_points": 5,
    },
    {
        "achievement_id": "grace_seeker",
        "title": "Grace Seeker",
        "description": "Complete 'The Way of Grace' quest",
        "requirement_type": "quests_completed",
        "requirement_value": 1,
        "bonus_xp": 50,
        "bonus_points": 25,
    },
    {
        "achievement_id": "scripture_scholar",
        "title": "Scripture Scholar",
        "description": "Achieve 500+ points in Bible Knowledge",
        "requirement_type": "bible_knowledge",
        "requirement_value": 500,
        "bonus_xp": 100,
        "bonus_points": 50,
    },
    {
        "achievement_id": "theology_master",
        "title": "Theology Master",
        "description": "Achieve 1000+ theology score",
        "requirement_type": "theology_score",
        "requirement_value": 1000,
        "bonus_xp": 200,
        "bonus_points": 100,
    },
    {
        "achievement_id": "level_5",
        "title": "Rising Scholar",
        "description": "Reach level 5",
        "requirement_type": "level_reached",
        "requirement_value": 5,
        "bonus_xp": 75,
        "bonus_points": 40,
    },
    {
        "achievement_id": "devoted_student",
        "title": "Devoted Student",
        "description": "Have 50 dialogues with characters",
        "requirement_type": "dialogues_completed",
        "requirement_value": 50,
        "bonus_xp": 150,
        "bonus_points": 75,
    },
]


def seed_achievements(db: Session, player_id: int):
    """Create achievements for a player"""
    # Check if already created
    existing = db.query(Achievement).filter(
        Achievement.player_id == player_id
    ).first()
    
    if existing:
        return
    
    for ach_data in SAMPLE_ACHIEVEMENTS:
        achievement = Achievement(
            player_id=player_id,
            achievement_id=ach_data["achievement_id"],
            title=ach_data["title"],
            description=ach_data["description"],
            requirement_type=ach_data["requirement_type"],
            requirement_value=ach_data["requirement_value"],
            bonus_xp=ach_data["bonus_xp"],
            bonus_points=ach_data["bonus_points"],
        )
        db.add(achievement)
    
    db.commit()


def check_achievements(db: Session, player_id: int):
    """Check and unlock achievements for a player"""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        return
    
    achievements = db.query(Achievement).filter(
        Achievement.player_id == player_id,
        Achievement.unlocked == False
    ).all()
    
    for ach in achievements:
        unlocked = False
        progress = 0
        
        # Check achievement criteria
        if ach.requirement_type == "dialogues_completed":
            progress = player.dialogue_count / ach.requirement_value * 100
            unlocked = player.dialogue_count >= ach.requirement_value
        
        elif ach.requirement_type == "quests_completed":
            progress = 0  # Would need to count from PlayerQuestProgress
            # unlocked = count_completed_quests(db, player_id) >= ach.requirement_value
        
        elif ach.requirement_type == "level_reached":
            progress = (player.level / ach.requirement_value) * 100
            unlocked = player.level >= ach.requirement_value
        
        elif ach.requirement_type == "theology_score":
            progress = (player.theology_score / ach.requirement_value) * 100
            unlocked = player.theology_score >= ach.requirement_value
        
        elif ach.requirement_type == "bible_knowledge":
            progress = (player.bible_knowledge / ach.requirement_value) * 100
            unlocked = player.bible_knowledge >= ach.requirement_value
        
        # Update achievement
        ach.progress = min(100, progress)
        
        if unlocked and not ach.unlocked:
            ach.unlocked = True
            ach.unlocked_at = datetime.utcnow()
            # Award bonus XP and points
            player.experience_points += ach.bonus_xp
    
    db.commit()


def get_player_achievements(db: Session, player_id: int):
    """Get all achievements for a player"""
    achievements = db.query(Achievement).filter(
        Achievement.player_id == player_id
    ).all()
    
    return [
        {
            "id": ach.id,
            "achievement_id": ach.achievement_id,
            "title": ach.title,
            "description": ach.description,
            "unlocked": ach.unlocked,
            "unlocked_at": ach.unlocked_at.isoformat() if ach.unlocked_at else None,
            "progress": ach.progress,
            "bonus_xp": ach.bonus_xp,
            "bonus_points": ach.bonus_points,
        }
        for ach in achievements
    ]
