#!/usr/bin/env python3
"""
Align database structure with schema documentation
This script modifies the database to match our documented schema exactly
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def align_database_with_schema():
    """Align database structure with schema documentation"""
    logger.info("Starting database schema alignment...")
    
    try:
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Step 1: Add missing columns to sites table
            logger.info("Step 1: Adding missing columns to sites table...")
            
            # Add site_name column if it doesn't exist
            try:
                conn.execute(text("""
                    ALTER TABLE sites ADD COLUMN IF NOT EXISTS site_name VARCHAR(100)
                """))
                logger.info("Added site_name column to sites table")
            except Exception as e:
                logger.warning(f"Could not add site_name: {e}")
            
            # Add elevation column
            try:
                conn.execute(text("""
                    ALTER TABLE sites ADD COLUMN IF NOT EXISTS elevation DECIMAL(8,2)
                """))
                logger.info("Added elevation column to sites table")
            except Exception as e:
                logger.warning(f"Could not add elevation: {e}")
            
            # Add watershed column
            try:
                conn.execute(text("""
                    ALTER TABLE sites ADD COLUMN IF NOT EXISTS watershed VARCHAR(100)
                """))
                logger.info("Added watershed column to sites table")
            except Exception as e:
                logger.warning(f"Could not add watershed: {e}")
            
            # Add created_date and updated_date columns
            try:
                conn.execute(text("""
                    ALTER TABLE sites ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT NOW()
                """))
                conn.execute(text("""
                    ALTER TABLE sites ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP DEFAULT NOW()
                """))
                logger.info("Added created_date and updated_date columns to sites table")
            except Exception as e:
                logger.warning(f"Could not add date columns: {e}")
            
            # Step 2: Add missing columns to samples table
            logger.info("Step 2: Adding missing columns to samples table...")
            
            # Add notes column
            try:
                conn.execute(text("""
                    ALTER TABLE samples ADD COLUMN IF NOT EXISTS notes TEXT
                """))
                logger.info("Added notes column to samples table")
            except Exception as e:
                logger.warning(f"Could not add notes: {e}")
            
            # Add created_date and updated_date columns
            try:
                conn.execute(text("""
                    ALTER TABLE samples ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT NOW()
                """))
                conn.execute(text("""
                    ALTER TABLE samples ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP DEFAULT NOW()
                """))
                logger.info("Added created_date and updated_date columns to samples table")
            except Exception as e:
                logger.warning(f"Could not add date columns: {e}")
            
            # Step 3: Add missing columns to bugs table
            logger.info("Step 3: Adding missing columns to bugs table...")
            
            # Add genus_species column
            try:
                conn.execute(text("""
                    ALTER TABLE bugs ADD COLUMN IF NOT EXISTS genus_species VARCHAR(100)
                """))
                logger.info("Added genus_species column to bugs table")
            except Exception as e:
                logger.warning(f"Could not add genus_species: {e}")
            
            # Add notes column
            try:
                conn.execute(text("""
                    ALTER TABLE bugs ADD COLUMN IF NOT EXISTS notes TEXT
                """))
                logger.info("Added notes column to bugs table")
            except Exception as e:
                logger.warning(f"Could not add notes: {e}")
            
            # Add created_date and updated_date columns
            try:
                conn.execute(text("""
                    ALTER TABLE bugs ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT NOW()
                """))
                conn.execute(text("""
                    ALTER TABLE bugs ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP DEFAULT NOW()
                """))
                logger.info("Added created_date and updated_date columns to bugs table")
            except Exception as e:
                logger.warning(f"Could not add date columns: {e}")
            
            # Step 4: Add missing columns to bacteria table
            logger.info("Step 4: Adding missing columns to bacteria table...")
            
            # Add large_wells, small_wells columns
            try:
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS large_wells INTEGER
                """))
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS small_wells INTEGER
                """))
                logger.info("Added large_wells and small_wells columns to bacteria table")
            except Exception as e:
                logger.warning(f"Could not add wells columns: {e}")
            
            # Add color change columns
            try:
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS color_change_large_wells INTEGER
                """))
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS color_change_small_wells INTEGER
                """))
                logger.info("Added color change columns to bacteria table")
            except Exception as e:
                logger.warning(f"Could not add color change columns: {e}")
            
            # Add data conditions and quality notes
            try:
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS data_conditions VARCHAR(200)
                """))
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS quality_notes TEXT
                """))
                logger.info("Added data_conditions and quality_notes columns to bacteria table")
            except Exception as e:
                logger.warning(f"Could not add condition columns: {e}")
            
            # Add created_date and updated_date columns
            try:
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT NOW()
                """))
                conn.execute(text("""
                    ALTER TABLE bacteria ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP DEFAULT NOW()
                """))
                logger.info("Added created_date and updated_date columns to bacteria table")
            except Exception as e:
                logger.warning(f"Could not add date columns: {e}")
            
            # Step 5: Add missing columns to volunteers table
            logger.info("Step 5: Adding missing columns to volunteers table...")
            
            # Add is_active column
            try:
                conn.execute(text("""
                    ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true
                """))
                logger.info("Added is_active column to volunteers table")
            except Exception as e:
                logger.warning(f"Could not add is_active: {e}")
            
            # Add created_date and updated_date columns
            try:
                conn.execute(text("""
                    ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS created_date TIMESTAMP DEFAULT NOW()
                """))
                conn.execute(text("""
                    ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP DEFAULT NOW()
                """))
                logger.info("Added created_date and updated_date columns to volunteers table")
            except Exception as e:
                logger.warning(f"Could not add date columns: {e}")
            
            # Step 6: Create users table if it doesn't exist
            logger.info("Step 6: Creating users table...")
            
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100),
                        role VARCHAR(20) NOT NULL,
                        is_active BOOLEAN DEFAULT true,
                        created_date TIMESTAMP DEFAULT NOW(),
                        last_login TIMESTAMP
                    )
                """))
                logger.info("Created users table")
            except Exception as e:
                logger.warning(f"Could not create users table: {e}")
            
            # Step 7: Add constraints and checks
            logger.info("Step 7: Adding constraints and checks...")
            
            # Add check constraints for pH
            try:
                conn.execute(text("""
                    ALTER TABLE samples ADD CONSTRAINT IF NOT EXISTS check_ph_range 
                    CHECK (ph >= 0 AND ph <= 14)
                """))
                conn.execute(text("""
                    ALTER TABLE bacteria ADD CONSTRAINT IF NOT EXISTS check_ph_range 
                    CHECK (ph >= 0 AND ph <= 14)
                """))
                logger.info("Added pH range constraints")
            except Exception as e:
                logger.warning(f"Could not add pH constraints: {e}")
            
            # Add check constraints for temperature
            try:
                conn.execute(text("""
                    ALTER TABLE samples ADD CONSTRAINT IF NOT EXISTS check_temp_range 
                    CHECK (water_temperature >= -5 AND water_temperature <= 50)
                """))
                conn.execute(text("""
                    ALTER TABLE bacteria ADD CONSTRAINT IF NOT EXISTS check_temp_range 
                    CHECK (water_temperature >= -5 AND water_temperature <= 50)
                """))
                logger.info("Added temperature range constraints")
            except Exception as e:
                logger.warning(f"Could not add temperature constraints: {e}")
            
            # Add check constraints for tolerance values
            try:
                conn.execute(text("""
                    ALTER TABLE bugs ADD CONSTRAINT IF NOT EXISTS check_tolerance_range 
                    CHECK (tolerance >= 1 AND tolerance <= 10)
                """))
                conn.execute(text("""
                    ALTER TABLE taxonomy ADD CONSTRAINT IF NOT EXISTS check_tolerance_range 
                    CHECK (tolerance_value >= 1 AND tolerance_value <= 10)
                """))
                logger.info("Added tolerance range constraints")
            except Exception as e:
                logger.warning(f"Could not add tolerance constraints: {e}")
            
            # Add check constraints for percentage
            try:
                conn.execute(text("""
                    ALTER TABLE bugs ADD CONSTRAINT IF NOT EXISTS check_percentage_range 
                    CHECK (percentage >= 0 AND percentage <= 100)
                """))
                logger.info("Added percentage range constraints")
            except Exception as e:
                logger.warning(f"Could not add percentage constraints: {e}")
            
            # Add check constraints for count
            try:
                conn.execute(text("""
                    ALTER TABLE bugs ADD CONSTRAINT IF NOT EXISTS check_count_positive 
                    CHECK (count >= 0)
                """))
                logger.info("Added count positive constraints")
            except Exception as e:
                logger.warning(f"Could not add count constraints: {e}")
            
            # Step 8: Add indexes for performance
            logger.info("Step 8: Adding performance indexes...")
            
            # Add foreign key indexes
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_samples_site_code ON samples(site_code)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bugs_sample_code ON bugs(sample_code)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bacteria_site_code ON bacteria(site_code)
                """))
                logger.info("Added foreign key indexes")
            except Exception as e:
                logger.warning(f"Could not add foreign key indexes: {e}")
            
            # Add date indexes
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_samples_date ON samples(sample_date)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bacteria_date ON bacteria(collection_date)
                """))
                logger.info("Added date indexes")
            except Exception as e:
                logger.warning(f"Could not add date indexes: {e}")
            
            # Add taxonomic indexes
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bugs_family ON bugs(family)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_bugs_order ON bugs(order_name)
                """))
                logger.info("Added taxonomic indexes")
            except Exception as e:
                logger.warning(f"Could not add taxonomic indexes: {e}")
            
            # Step 9: Update data to populate new columns
            logger.info("Step 9: Populating new columns with data...")
            
            # Populate site_name from existing data
            try:
                conn.execute(text("""
                    UPDATE sites 
                    SET site_name = COALESCE(site_name, 'Site ' || site_code)
                    WHERE site_name IS NULL
                """))
                logger.info("Populated site_name column")
            except Exception as e:
                logger.warning(f"Could not populate site_name: {e}")
            
            # Populate watershed from subwatershed
            try:
                conn.execute(text("""
                    UPDATE sites 
                    SET watershed = COALESCE(watershed, subwatershed, 'Unknown Watershed')
                    WHERE watershed IS NULL
                """))
                logger.info("Populated watershed column")
            except Exception as e:
                logger.warning(f"Could not populate watershed: {e}")
            
            # Populate genus_species in bugs table
            try:
                conn.execute(text("""
                    UPDATE bugs 
                    SET genus_species = COALESCE(genus_species, order_name)
                    WHERE genus_species IS NULL
                """))
                logger.info("Populated genus_species column in bugs table")
            except Exception as e:
                logger.warning(f"Could not populate genus_species: {e}")
            
            # Commit all changes
            conn.commit()
            logger.info("All changes committed successfully")
            
            # Step 10: Verify the changes
            logger.info("Step 10: Verifying schema alignment...")
            
            # Check sites table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'sites' 
                AND column_name IN ('site_name', 'elevation', 'watershed', 'created_date', 'updated_date')
                ORDER BY column_name
            """))
            sites_columns = result.fetchall()
            logger.info("Sites table new columns:")
            for col in sites_columns:
                logger.info(f"  {col[0]}: {col[1]} ({col[2]})")
            
            # Check samples table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'samples' 
                AND column_name IN ('notes', 'created_date', 'updated_date')
                ORDER BY column_name
            """))
            samples_columns = result.fetchall()
            logger.info("Samples table new columns:")
            for col in samples_columns:
                logger.info(f"  {col[0]}: {col[1]} ({col[2]})")
            
            # Check bugs table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'bugs' 
                AND column_name IN ('genus_species', 'notes', 'created_date', 'updated_date')
                ORDER BY column_name
            """))
            bugs_columns = result.fetchall()
            logger.info("Bugs table new columns:")
            for col in bugs_columns:
                logger.info(f"  {col[0]}: {col[1]} ({col[2]})")
            
            # Check bacteria table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'bacteria' 
                AND column_name IN ('large_wells', 'small_wells', 'data_conditions', 'quality_notes', 'created_date', 'updated_date')
                ORDER BY column_name
            """))
            bacteria_columns = result.fetchall()
            logger.info("Bacteria table new columns:")
            for col in bacteria_columns:
                logger.info(f"  {col[0]}: {col[1]} ({col[2]})")
            
            logger.info("=== SCHEMA ALIGNMENT COMPLETE ===")
            logger.info("Database structure now matches schema documentation!")
            
    except Exception as e:
        logger.error(f"Error aligning database with schema: {e}")
        raise

if __name__ == "__main__":
    align_database_with_schema()





