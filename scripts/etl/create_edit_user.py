#!/usr/bin/env python3
"""
Create edit user for StreamWatch database
"""

import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_edit_user():
    """Create an edit user for the StreamWatch database"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Creating edit user for StreamWatch database...")
        
        with engine.connect() as conn:
            # Create edit user (drop first if exists)
            try:
                conn.execute(text("DROP ROLE streamwatch_edit;"))
                conn.commit()
            except:
                conn.rollback()  # Role doesn't exist, that's fine
            
            conn.execute(text("""
                CREATE ROLE streamwatch_edit LOGIN PASSWORD 'streamwatch_edit_2024';
            """))
            conn.commit()
            
            # Grant connection privileges
            conn.execute(text("""
                GRANT CONNECT ON DATABASE neondb TO streamwatch_edit;
            """))
            conn.commit()
            
            # Grant usage on schema
            conn.execute(text("""
                GRANT USAGE ON SCHEMA public TO streamwatch_edit;
            """))
            conn.commit()
            
            # Grant all privileges on all existing tables
            conn.execute(text("""
                GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO streamwatch_edit;
            """))
            conn.commit()
            
            # Grant all privileges on all existing sequences
            conn.execute(text("""
                GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO streamwatch_edit;
            """))
            conn.commit()
            
            # Grant all privileges on future tables and sequences
            conn.execute(text("""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO streamwatch_edit;
            """))
            conn.commit()
            
            conn.execute(text("""
                ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO streamwatch_edit;
            """))
            conn.commit()
            
            # Grant create privileges (so they can create new tables if needed)
            conn.execute(text("""
                GRANT CREATE ON SCHEMA public TO streamwatch_edit;
            """))
            conn.commit()
            
        logger.info("Edit user created successfully!")
        logger.info("Username: streamwatch_edit")
        logger.info("Password: streamwatch_edit_2024")
        logger.info("Permissions: Full read/write access to all tables and data")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating edit user: {e}")
        return False

if __name__ == "__main__":
    create_edit_user()
