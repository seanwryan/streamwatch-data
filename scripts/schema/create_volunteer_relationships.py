#!/usr/bin/env python3
"""
Create relationship tables for volunteers:
- training
- volunteer_assignments
- visit_attendance
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

def create_relationship_tables():
    """Create the relationship tables for volunteers"""
    try:
        # Create connection string
        # Create connection string
        # Using hardcoded credentials from test_team_access.py to ensure it works without env vars
        DATABASE_URL = "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Creating volunteer relationship tables...")
        
        with engine.connect() as conn:
            # 1. Create training table
            logger.info("Creating training table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS training (
                    training_id SERIAL PRIMARY KEY,
                    volunteer_id VARCHAR(20),
                    training_type VARCHAR(100),
                    training_date DATE,
                    expiration_date DATE,
                    test_score DECIMAL(5,2),
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id)
                )
            """))
            
            # 2. Create volunteer_assignments table (Junction: Volunteers <-> Sites)
            logger.info("Creating volunteer_assignments table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS volunteer_assignments (
                    assignment_id SERIAL PRIMARY KEY,
                    volunteer_id VARCHAR(20),
                    site_code VARCHAR(20),
                    sector VARCHAR(50),
                    assign_start DATE,
                    assign_end DATE,
                    notes TEXT,
                    is_valid BOOLEAN DEFAULT true,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id),
                    FOREIGN KEY (site_code) REFERENCES sites(site_code)
                )
            """))
            
            # 3. Create visit_attendance table (Junction: Volunteers <-> Samples/Visits)
            # Note: sample_id in samples table is VARCHAR(50), so visit_id should match
            logger.info("Creating visit_attendance table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS visit_attendance (
                    attendance_id SERIAL PRIMARY KEY,
                    volunteer_id VARCHAR(20),
                    visit_id VARCHAR(50),
                    data_code VARCHAR(50),
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (volunteer_id) REFERENCES volunteers(volunteer_id),
                    FOREIGN KEY (visit_id) REFERENCES samples(sample_id)
                )
            """))
            
            # Create indices
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_training_volunteer ON training(volunteer_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_assignments_volunteer ON volunteer_assignments(volunteer_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_assignments_site ON volunteer_assignments(site_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_attendance_volunteer ON visit_attendance(volunteer_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_attendance_visit ON visit_attendance(visit_id)"))
            
            conn.commit()
            
        logger.info("Relationship tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating relationship tables: {e}")
        return False

if __name__ == "__main__":
    create_relationship_tables()
