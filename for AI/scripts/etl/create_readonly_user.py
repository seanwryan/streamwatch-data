#!/usr/bin/env python3
"""
Create read-only user for StreamWatch database
"""

import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_readonly_user():
    """Create a read-only user for the StreamWatch database"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Creating read-only user for StreamWatch database...")
        
        with engine.connect() as conn:
            # Create read-only user (drop first if exists)
            try:
                conn.execute(text("DROP ROLE streamwatch_readonly;"))
                conn.commit()
            except:
                conn.rollback()  # Role doesn't exist, that's fine
            
            conn.execute(text("""
                CREATE ROLE streamwatch_readonly LOGIN PASSWORD 'streamwatch_readonly_2024';
            """))
            conn.commit()
            
            # Grant connection privileges
            conn.execute(text("""
                GRANT CONNECT ON DATABASE neondb TO streamwatch_readonly;
            """))
            conn.commit()
            
            # Grant usage on schema
            conn.execute(text("""
                GRANT USAGE ON SCHEMA public TO streamwatch_readonly;
            """))
            conn.commit()
            
            # Grant select on all existing tables
            conn.execute(text("""
                GRANT SELECT ON ALL TABLES IN SCHEMA public TO streamwatch_readonly;
            """))
            conn.commit()
            
            # Grant select on future tables
            conn.execute(text("""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO streamwatch_readonly;
            """))
            conn.commit()
            
        logger.info("Read-only user created successfully!")
        logger.info("Username: streamwatch_readonly")
        logger.info("Password: streamwatch_readonly_2024")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating read-only user: {e}")
        return False

if __name__ == "__main__":
    create_readonly_user()
