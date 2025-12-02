"""
Fix volunteers table to match Jian's Access database structure (VOLUNTEERtbl)

Based on Access schema:
- VolunteerID (PK)
- PerfectID
- FirstName
- LastName
- IntLastName
- isActive
- isUnder17
- Address

Relationships:
- VOLUNTEERtbl → tblTraining (one-to-many)
- VOLUNTEERtbl → juncAssignments (one-to-many) - many-to-many with sites
- VOLUNTEERtbl → juncAttendance (one-to-many) - many-to-many with visits
"""

import logging
from sqlalchemy import create_engine, text
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_volunteers_table():
    """
    Update volunteers table structure to match Access VOLUNTEERtbl
    and create related tables (training, assignments, attendance)
    """
    
    # Connect to database
    DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
    engine = create_engine(DATABASE_URL)
    
    logger.info("Starting volunteers table structure update...")
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # Step 1: Check current volunteers table structure
            logger.info("Checking current volunteers table structure...")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'volunteers'
                ORDER BY ordinal_position
            """))
            
            current_columns = {row[0]: row[1] for row in result}
            logger.info(f"Current columns: {list(current_columns.keys())}")
            
            # Step 2: Create backup of existing site_code assignments
            logger.info("Backing up existing volunteer-site assignments...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS volunteer_site_assignments_backup AS
                SELECT volunteer_id, site_code, start_date as assignment_date
                FROM volunteers
                WHERE site_code IS NOT NULL
            """))
            
            # Step 3: Add missing columns to volunteers table
            logger.info("Adding missing columns to volunteers table...")
            
            # Add PerfectID
            try:
                conn.execute(text("ALTER TABLE volunteers ADD COLUMN perfect_id VARCHAR(50)"))
                logger.info("Added perfect_id column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("perfect_id column already exists")
                else:
                    raise
            
            # Add IntLastName
            try:
                conn.execute(text("ALTER TABLE volunteers ADD COLUMN int_last_name VARCHAR(100)"))
                logger.info("Added int_last_name column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("int_last_name column already exists")
                else:
                    raise
            
            # Add isUnder17
            try:
                conn.execute(text("ALTER TABLE volunteers ADD COLUMN is_under_17 BOOLEAN DEFAULT false"))
                logger.info("Added is_under_17 column")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("is_under_17 column already exists")
                else:
                    raise
            
            # Add Address (if not exists - check if address column exists)
            if 'address' not in current_columns:
                try:
                    conn.execute(text("ALTER TABLE volunteers ADD COLUMN address TEXT"))
                    logger.info("Added address column")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info("address column already exists")
                    else:
                        raise
            else:
                logger.info("address column already exists")
            
            # Step 4: Rename columns to match Access naming (if needed)
            # Keep PostgreSQL naming convention (snake_case) but ensure we have all fields
            
            # Ensure is_active exists (matches isActive)
            if 'is_active' not in current_columns:
                try:
                    conn.execute(text("ALTER TABLE volunteers ADD COLUMN is_active BOOLEAN DEFAULT true"))
                    logger.info("Added is_active column")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info("is_active column already exists")
                    else:
                        raise
            
            # Step 5: Create tblTraining table
            logger.info("Creating training table (tblTraining)...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS training (
                    training_id SERIAL PRIMARY KEY,
                    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
                    training_type VARCHAR(100),
                    training_date DATE,
                    expiration_date DATE,
                    test_score DECIMAL(5,2),
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT NOW(),
                    updated_date TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Create index on volunteer_id for performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_training_volunteer_id 
                ON training(volunteer_id)
            """))
            
            logger.info("Created training table")
            
            # Step 6: Create juncAssignments table (many-to-many volunteer-site)
            logger.info("Creating volunteer_assignments table (juncAssignments)...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS volunteer_assignments (
                    assignment_id SERIAL PRIMARY KEY,
                    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
                    site_code VARCHAR(50) NOT NULL REFERENCES sites(site_code) ON DELETE CASCADE,
                    sector VARCHAR(50),
                    assign_start DATE,
                    assign_end DATE,
                    notes TEXT,
                    is_valid BOOLEAN DEFAULT true,
                    created_date TIMESTAMP DEFAULT NOW(),
                    updated_date TIMESTAMP DEFAULT NOW(),
                    UNIQUE(volunteer_id, site_code, assign_start)
                )
            """))
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_assignments_volunteer_id 
                ON volunteer_assignments(volunteer_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_assignments_site_code 
                ON volunteer_assignments(site_code)
            """))
            
            logger.info("Created volunteer_assignments table")
            
            # Step 7: Migrate existing site_code assignments to juncAssignments
            logger.info("Migrating existing volunteer-site assignments...")
            conn.execute(text("""
                INSERT INTO volunteer_assignments (volunteer_id, site_code, assign_start, is_valid)
                SELECT 
                    volunteer_id,
                    site_code,
                    COALESCE(start_date, CURRENT_DATE) as assign_start,
                    is_active as is_valid
                FROM volunteers
                WHERE site_code IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM volunteer_assignments va
                    WHERE va.volunteer_id = volunteers.volunteer_id
                    AND va.site_code = volunteers.site_code
                )
            """))
            
            migrated_count = conn.execute(text("SELECT COUNT(*) FROM volunteer_assignments")).scalar()
            logger.info(f"Migrated {migrated_count} volunteer-site assignments")
            
            # Step 8: Create juncAttendance table (volunteer-visit attendance)
            logger.info("Creating visit_attendance table (juncAttendance)...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS visit_attendance (
                    attendance_id SERIAL PRIMARY KEY,
                    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
                    visit_id INTEGER REFERENCES samples(sample_id) ON DELETE CASCADE,
                    data_code VARCHAR(50),
                    notes TEXT,
                    created_date TIMESTAMP DEFAULT NOW(),
                    updated_date TIMESTAMP DEFAULT NOW(),
                    UNIQUE(volunteer_id, visit_id)
                )
            """))
            
            # Create indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_attendance_volunteer_id 
                ON visit_attendance(volunteer_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_attendance_visit_id 
                ON visit_attendance(visit_id)
            """))
            
            logger.info("Created visit_attendance table")
            
            # Step 9: Migrate existing volunteer_id from samples to visit_attendance
            logger.info("Migrating existing volunteer-sample relationships to visit_attendance...")
            conn.execute(text("""
                INSERT INTO visit_attendance (volunteer_id, visit_id)
                SELECT 
                    volunteer_id,
                    sample_id
                FROM samples
                WHERE volunteer_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT 1 FROM visit_attendance va
                    WHERE va.volunteer_id = samples.volunteer_id
                    AND va.visit_id = samples.sample_id
                )
            """))
            
            attendance_count = conn.execute(text("SELECT COUNT(*) FROM visit_attendance")).scalar()
            logger.info(f"Migrated {attendance_count} volunteer-visit attendance records")
            
            # Step 10: Remove site_code from volunteers table (now in junction table)
            # NOTE: We'll keep it for now to avoid breaking existing queries, but document it as deprecated
            logger.info("Note: Keeping site_code in volunteers table for backward compatibility")
            logger.info("Consider removing after verifying all queries use volunteer_assignments")
            
            trans.commit()
            logger.info("✅ Successfully updated volunteers table structure!")
            
            # Step 11: Print summary
            logger.info("\n=== VOLUNTEERS TABLE STRUCTURE SUMMARY ===")
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'volunteers'
                ORDER BY ordinal_position
            """))
            
            logger.info("\nVolunteers table columns:")
            for row in result:
                logger.info(f"  - {row[0]}: {row[1]} ({'nullable' if row[2] == 'YES' else 'not null'})")
            
            # Count records in new tables
            training_count = conn.execute(text("SELECT COUNT(*) FROM training")).scalar()
            assignments_count = conn.execute(text("SELECT COUNT(*) FROM volunteer_assignments")).scalar()
            attendance_count = conn.execute(text("SELECT COUNT(*) FROM visit_attendance")).scalar()
            
            logger.info(f"\nRelated tables:")
            logger.info(f"  - training: {training_count} records")
            logger.info(f"  - volunteer_assignments: {assignments_count} records")
            logger.info(f"  - visit_attendance: {attendance_count} records")
            
        except Exception as e:
            trans.rollback()
            logger.error(f"❌ Error updating volunteers table: {e}")
            raise

if __name__ == "__main__":
    fix_volunteers_table()



