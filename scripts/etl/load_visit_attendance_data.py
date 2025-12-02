#!/usr/bin/env python3
"""
Load visit attendance data by linking volunteers to samples/visits
Migrates volunteer_id from samples table to visit_attendance junction table
"""

from sqlalchemy import create_engine, text
import sys
import os
import logging

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import DB_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_visit_attendance():
    """Migrate volunteer-sample relationships to visit_attendance table"""
    logger.info("Loading visit attendance data from samples table...")
    
    try:
        # Connect to database
        DATABASE_URL = "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Check if samples table has volunteer_id column
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'samples' AND column_name = 'volunteer_id'
                """))
                
                has_volunteer_id = result.fetchone() is not None
                
                if not has_volunteer_id:
                    logger.warning("samples table does not have volunteer_id column")
                    logger.info("Checking for alternative ways to link volunteers to visits...")
                    
                    # Check if we can link via site_code and date matching
                    # This would require more complex logic
                    logger.info("Visit attendance will need to be populated manually or via forms")
                    trans.commit()
                    return
                
                # Migrate volunteer_id from samples to visit_attendance
                logger.info("Migrating volunteer-sample relationships...")
                
                # First, check what the visit_id column type is in visit_attendance
                result = conn.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'visit_attendance' AND column_name = 'visit_id'
                """))
                visit_id_type = result.scalar()
                
                # Get sample_id type from samples table
                result = conn.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'samples' AND column_name = 'sample_id'
                """))
                sample_id_type = result.scalar()
                
                logger.info(f"visit_attendance.visit_id type: {visit_id_type}, samples.sample_id type: {sample_id_type}")
                
                # Insert attendance records
                if visit_id_type == 'character varying' and sample_id_type == 'character varying':
                    # Both are VARCHAR, direct match
                    result = conn.execute(text("""
                        INSERT INTO visit_attendance (volunteer_id, visit_id)
                        SELECT DISTINCT 
                            CAST(volunteer_id AS VARCHAR(20)),
                            sample_id
                        FROM samples
                        WHERE volunteer_id IS NOT NULL
                        AND volunteer_id != ''
                        AND sample_id IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1 FROM visit_attendance va
                            WHERE va.volunteer_id = CAST(samples.volunteer_id AS VARCHAR(20))
                            AND va.visit_id = samples.sample_id
                        )
                    """))
                elif visit_id_type == 'integer' and sample_id_type == 'integer':
                    # Both are INTEGER
                    result = conn.execute(text("""
                        INSERT INTO visit_attendance (volunteer_id, visit_id)
                        SELECT DISTINCT 
                            CAST(volunteer_id AS VARCHAR(20)),
                            sample_id
                        FROM samples
                        WHERE volunteer_id IS NOT NULL
                        AND volunteer_id != ''
                        AND sample_id IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1 FROM visit_attendance va
                            WHERE va.volunteer_id = CAST(samples.volunteer_id AS VARCHAR(20))
                            AND va.visit_id = samples.sample_id
                        )
                    """))
                else:
                    # Mixed types - need conversion
                    logger.warning(f"Type mismatch: visit_id is {visit_id_type}, sample_id is {sample_id_type}")
                    logger.info("Attempting conversion...")
                    result = conn.execute(text("""
                        INSERT INTO visit_attendance (volunteer_id, visit_id)
                        SELECT DISTINCT 
                            CAST(volunteer_id AS VARCHAR(20)),
                            CAST(sample_id AS VARCHAR(50))
                        FROM samples
                        WHERE volunteer_id IS NOT NULL
                        AND volunteer_id != ''
                        AND sample_id IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1 FROM visit_attendance va
                            WHERE va.volunteer_id = CAST(samples.volunteer_id AS VARCHAR(20))
                            AND va.visit_id = CAST(samples.sample_id AS VARCHAR(50))
                        )
                    """))
                
                inserted = result.rowcount
                trans.commit()
                
                logger.info(f"✅ Successfully inserted {inserted} visit attendance records")
                
                # Verify
                count = conn.execute(text("SELECT COUNT(*) FROM visit_attendance")).scalar()
                logger.info(f"Total visit attendance records in database: {count}")
                
                # Show sample
                sample = conn.execute(text("""
                    SELECT va.volunteer_id, v.first_name, v.last_name, va.visit_id, s.sample_date
                    FROM visit_attendance va
                    JOIN volunteers v ON va.volunteer_id = v.volunteer_id
                    JOIN samples s ON va.visit_id = s.sample_id
                    LIMIT 5
                """)).fetchall()
                
                if sample:
                    logger.info("Sample attendance records:")
                    for row in sample:
                        logger.info(f"  Volunteer {row[0]} ({row[1]} {row[2]}) attended visit {row[3]} on {row[4]}")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error loading visit attendance: {e}")
                raise
        
    except Exception as e:
        logger.error(f"Error loading visit attendance: {e}")
        raise

if __name__ == "__main__":
    load_visit_attendance()

