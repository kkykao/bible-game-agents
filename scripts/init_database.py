"""Initialize database with SQLAlchemy models"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models import Base

def init_database():
    """Create database tables from SQLAlchemy models"""
    # Get database URL from environment or use default SQLite
    database_url = os.getenv("DATABASE_URL", "sqlite:///./game.db")
    
    print(f"📊 Initializing database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url, echo=False)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialization complete!")
    print("📋 Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")
    
    engine.dispose()

if __name__ == "__main__":
    init_database()
