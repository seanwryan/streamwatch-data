#!/usr/bin/env python3
"""
Run a SQL migration file against the database
Usage: python3 run_migration.py path/to/file.sql
"""

import psycopg2
from sqlalchemy import create_engine, text
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration(file_path):
    """Run SQL file"""
    logger.info(f"Running migration from {file_path}...")
    
    try:
        # Read SQL file
        with open(file_path, 'r') as f:
            sql_content = f.read()
            
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Execute as one block? Or split?
            # sqlalchemy text() might handle multiple statements if driver allows.
            # psycopg2 usually requires execute() per statement or special handling.
            # But simple scripts often work.
            conn.execute(text(sql_content))
            conn.commit()
            
        logger.info("Migration executed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error running migration: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 run_migration.py path/to/file.sql")
        sys.exit(1)
    
    run_migration(sys.argv[1])
