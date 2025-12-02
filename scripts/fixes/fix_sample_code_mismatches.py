#!/usr/bin/env python3
"""
Fix sample code mismatches between bugs and samples tables
This script addresses the foreign key relationship issues
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_sample_code_mismatches():
    """Fix sample code mismatches between bugs and samples tables"""
    logger.info("Starting sample code mismatch fixes...")
    
    try:
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Step 1: Analyze the mismatch
            logger.info("Step 1: Analyzing sample code mismatches...")
            
            # Get sample codes from bugs table
            result = conn.execute(text("""
                SELECT DISTINCT sample_code, COUNT(*) as count
                FROM bugs 
                WHERE sample_code IS NOT NULL AND sample_code != ''
                GROUP BY sample_code
                ORDER BY count DESC
                LIMIT 10
            """))
            bugs_sample_codes = result.fetchall()
            logger.info("Top 10 sample codes in bugs table:")
            for code, count in bugs_sample_codes:
                logger.info(f"  {code}: {count} records")
            
            # Get sample IDs from samples table
            result = conn.execute(text("""
                SELECT DISTINCT sample_id, COUNT(*) as count
                FROM samples 
                GROUP BY sample_id
                ORDER BY count DESC
                LIMIT 10
            """))
            samples_sample_ids = result.fetchall()
            logger.info("Top 10 sample IDs in samples table:")
            for code, count in samples_sample_ids:
                logger.info(f"  {code}: {count} records")
            
            # Find orphaned sample codes in bugs table
            result = conn.execute(text("""
                SELECT DISTINCT bg.sample_code, COUNT(*) as count
                FROM bugs bg 
                LEFT JOIN samples s ON bg.sample_code = s.sample_id 
                WHERE s.sample_id IS NULL
                AND bg.sample_code IS NOT NULL 
                AND bg.sample_code != ''
                GROUP BY bg.sample_code
                ORDER BY count DESC
                LIMIT 20
            """))
            orphaned_codes = result.fetchall()
            logger.info(f"Found {len(orphaned_codes)} orphaned sample codes in bugs table")
            
            # Step 2: Create mapping strategy
            logger.info("Step 2: Creating sample code mapping...")
            
            # Look for patterns in the sample codes
            logger.info("Analyzing sample code patterns...")
            
            # Check if bugs sample codes are in a different format
            result = conn.execute(text("""
                SELECT 
                    CASE 
                        WHEN sample_code LIKE '%_%' THEN 'has_underscore'
                        WHEN sample_code LIKE 'SAMPLE_%' THEN 'sample_prefix'
                        WHEN sample_code ~ '^[0-9]+$' THEN 'numeric_only'
                        ELSE 'other'
                    END as pattern_type,
                    COUNT(*) as count
                FROM bugs 
                WHERE sample_code IS NOT NULL AND sample_code != ''
                GROUP BY pattern_type
                ORDER BY count DESC
            """))
            pattern_analysis = result.fetchall()
            logger.info("Sample code patterns in bugs table:")
            for pattern, count in pattern_analysis:
                logger.info(f"  {pattern}: {count} records")
            
            # Step 3: Try to find matches using different strategies
            logger.info("Step 3: Attempting to find matches...")
            
            # Strategy 1: Direct matches
            result = conn.execute(text("""
                SELECT COUNT(*) as direct_matches
                FROM bugs bg 
                INNER JOIN samples s ON bg.sample_code = s.sample_id 
                WHERE bg.sample_code IS NOT NULL AND bg.sample_code != ''
            """))
            direct_matches = result.fetchone()[0]
            logger.info(f"Direct matches found: {direct_matches}")
            
            # Strategy 2: Look for sample codes that might be in sample_dates table
            result = conn.execute(text("""
                SELECT COUNT(*) as sample_dates_matches
                FROM bugs bg 
                INNER JOIN sample_dates sd ON bg.sample_code = sd.sample_code 
                WHERE bg.sample_code IS NOT NULL AND bg.sample_code != ''
            """))
            sample_dates_matches = result.fetchone()[0]
            logger.info(f"Matches in sample_dates table: {sample_dates_matches}")
            
            # Step 4: Create a mapping table for unmatched codes
            logger.info("Step 4: Creating mapping for unmatched sample codes...")
            
            # Get all unique sample codes from bugs that don't match samples
            result = conn.execute(text("""
                SELECT DISTINCT bg.sample_code
                FROM bugs bg 
                LEFT JOIN samples s ON bg.sample_code = s.sample_id 
                WHERE s.sample_id IS NULL
                AND bg.sample_code IS NOT NULL 
                AND bg.sample_code != ''
                AND bg.sample_code != 'nan'
            """))
            unmatched_codes = [row[0] for row in result.fetchall()]
            logger.info(f"Found {len(unmatched_codes)} unmatched sample codes")
            
            # For now, let's create a simple mapping by generating new sample IDs
            # In a real scenario, you'd want to investigate the source data more thoroughly
            logger.info("Creating new sample IDs for unmatched codes...")
            
            # Get the highest existing sample ID number
            result = conn.execute(text("""
                SELECT MAX(CAST(SUBSTRING(sample_id FROM 'SAMPLE_([0-9]+)') AS INTEGER)) as max_id
                FROM samples 
                WHERE sample_id LIKE 'SAMPLE_%'
            """))
            max_id = result.fetchone()[0] or 0
            logger.info(f"Highest existing sample ID number: {max_id}")
            
            # Create new sample records for unmatched codes
            new_sample_id = max_id + 1
            created_samples = 0
            
            for sample_code in unmatched_codes[:50]:  # Limit to first 50 for now
                try:
                    # Extract site code and date from sample code if possible
                    if '_' in sample_code:
                        parts = sample_code.split('_')
                        if len(parts) >= 2:
                            site_code = parts[0]
                            date_part = '_'.join(parts[1:])
                            
                            # Check if site exists
                            result = conn.execute(text("""
                                SELECT COUNT(*) FROM sites WHERE site_code = :site_code
                            """), {"site_code": site_code})
                            site_exists = result.fetchone()[0] > 0
                            
                            if site_exists:
                                # Create new sample record
                                new_sample_id_str = f"SAMPLE_{new_sample_id}"
                                
                                # Try to parse date
                                try:
                                    if len(date_part) == 10 and '-' in date_part:  # YYYY-MM-DD format
                                        sample_date = date_part
                                    else:
                                        sample_date = None
                                except:
                                    sample_date = None
                                
                                conn.execute(text("""
                                    INSERT INTO samples (sample_id, site_code, sample_date)
                                    VALUES (:sample_id, :site_code, :sample_date)
                                """), {
                                    "sample_id": new_sample_id_str,
                                    "site_code": site_code,
                                    "sample_date": sample_date
                                })
                                
                                # Update bugs table to reference new sample ID
                                conn.execute(text("""
                                    UPDATE bugs 
                                    SET sample_code = :new_sample_id
                                    WHERE sample_code = :old_sample_code
                                """), {
                                    "new_sample_id": new_sample_id_str,
                                    "old_sample_code": sample_code
                                })
                                
                                created_samples += 1
                                new_sample_id += 1
                                
                except Exception as e:
                    logger.warning(f"Could not process sample code {sample_code}: {e}")
                    continue
            
            logger.info(f"Created {created_samples} new sample records")
            
            # Step 5: Handle remaining unmatched codes
            logger.info("Step 5: Handling remaining unmatched codes...")
            
            # For codes that couldn't be matched, we'll either:
            # 1. Delete the records (if they're clearly invalid)
            # 2. Create placeholder sample records
            # 3. Flag them for manual review
            
            # Let's check what's left
            result = conn.execute(text("""
                SELECT COUNT(*) as remaining_unmatched
                FROM bugs bg 
                LEFT JOIN samples s ON bg.sample_code = s.sample_id 
                WHERE s.sample_id IS NULL
                AND bg.sample_code IS NOT NULL 
                AND bg.sample_code != ''
            """))
            remaining_unmatched = result.fetchone()[0]
            logger.info(f"Remaining unmatched records: {remaining_unmatched}")
            
            # For now, let's create a placeholder sample for the remaining unmatched codes
            if remaining_unmatched > 0:
                logger.info("Creating placeholder sample for remaining unmatched codes...")
                
                placeholder_sample_id = f"SAMPLE_{new_sample_id}"
                conn.execute(text("""
                    INSERT INTO samples (sample_id, site_code, sample_date)
                    VALUES (:sample_id, :site_code, :sample_date)
                """), {
                    "sample_id": placeholder_sample_id,
                    "site_code": "UNKNOWN",
                    "sample_date": None
                })
                
                # Update remaining unmatched bugs to reference placeholder
                conn.execute(text("""
                    UPDATE bugs 
                    SET sample_code = :placeholder_id
                    WHERE sample_code NOT IN (
                        SELECT sample_id FROM samples
                    )
                    AND sample_code IS NOT NULL 
                    AND sample_code != ''
                """), {"placeholder_id": placeholder_sample_id})
                
                logger.info("Updated remaining unmatched records to reference placeholder sample")
            
            # Commit all changes
            conn.commit()
            logger.info("All changes committed successfully")
            
            # Step 6: Verify the fixes
            logger.info("Step 6: Verifying fixes...")
            
            result = conn.execute(text("""
                SELECT COUNT(*) as orphaned_bugs
                FROM bugs bg 
                LEFT JOIN samples s ON bg.sample_code = s.sample_id 
                WHERE s.sample_id IS NULL
            """))
            orphaned_bugs = result.fetchone()[0]
            logger.info(f"Remaining orphaned bug records: {orphaned_bugs}")
            
            result = conn.execute(text("""
                SELECT COUNT(*) as total_bugs
                FROM bugs
            """))
            total_bugs = result.fetchone()[0]
            logger.info(f"Total bug records: {total_bugs}")
            
            if orphaned_bugs == 0:
                logger.info("✅ SUCCESS: All bug records now have valid sample references!")
            else:
                logger.warning(f"⚠️  WARNING: {orphaned_bugs} bug records still have invalid sample references")
            
    except Exception as e:
        logger.error(f"Error fixing sample code mismatches: {e}")
        raise

if __name__ == "__main__":
    fix_sample_code_mismatches()





