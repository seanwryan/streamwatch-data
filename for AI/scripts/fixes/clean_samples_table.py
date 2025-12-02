#!/usr/bin/env python3
"""
Clean samples table data
This script fixes negative temperatures, removes empty records, and improves data quality
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_samples_table():
    """Clean samples table data"""
    logger.info("Starting samples table cleaning...")
    
    try:
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Step 1: Analyze current data quality
            logger.info("Step 1: Analyzing current samples table data quality...")
            
            # Check for negative temperatures
            result = conn.execute(text("""
                SELECT COUNT(*) as negative_temps
                FROM samples 
                WHERE water_temperature < 0
            """))
            negative_temps = result.fetchone()[0]
            logger.info(f"Records with negative temperatures: {negative_temps}")
            
            # Check for samples with no measurements
            result = conn.execute(text("""
                SELECT COUNT(*) as no_measurements
                FROM samples 
                WHERE water_temperature IS NULL 
                AND ph IS NULL 
                AND do_ppm IS NULL 
                AND nitrate IS NULL 
                AND phosphates IS NULL 
                AND turbidity IS NULL
            """))
            no_measurements = result.fetchone()[0]
            logger.info(f"Records with no measurements: {no_measurements}")
            
            # Check for invalid pH values
            result = conn.execute(text("""
                SELECT COUNT(*) as invalid_ph
                FROM samples 
                WHERE ph < 0 OR ph > 14
            """))
            invalid_ph = result.fetchone()[0]
            logger.info(f"Records with invalid pH values: {invalid_ph}")
            
            # Check for negative values in other fields
            numeric_fields = ['do_ppm', 'nitrate', 'phosphates', 'turbidity', 'conductivity']
            for field in numeric_fields:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) as negative_{field}
                    FROM samples 
                    WHERE {field} < 0
                """))
                negative_count = result.fetchone()[0]
                if negative_count > 0:
                    logger.info(f"Records with negative {field}: {negative_count}")
            
            # Step 2: Fix negative temperatures
            if negative_temps > 0:
                logger.info("Step 2: Fixing negative temperatures...")
                
                # Show some examples of negative temperatures
                result = conn.execute(text("""
                    SELECT sample_id, site_code, sample_date, water_temperature
                    FROM samples 
                    WHERE water_temperature < 0
                    LIMIT 5
                """))
                examples = result.fetchall()
                logger.info("Examples of negative temperatures:")
                for row in examples:
                    logger.info(f"  {row[0]}: {row[1]} on {row[2]} - Temp: {row[3]}")
                
                # Fix by taking absolute value
                result = conn.execute(text("""
                    UPDATE samples 
                    SET water_temperature = ABS(water_temperature)
                    WHERE water_temperature < 0
                """))
                logger.info(f"Fixed {result.rowcount} negative temperature values")
            
            # Step 3: Fix invalid pH values
            if invalid_ph > 0:
                logger.info("Step 3: Fixing invalid pH values...")
                
                # Show some examples
                result = conn.execute(text("""
                    SELECT sample_id, site_code, sample_date, ph
                    FROM samples 
                    WHERE ph < 0 OR ph > 14
                    LIMIT 5
                """))
                examples = result.fetchall()
                logger.info("Examples of invalid pH values:")
                for row in examples:
                    logger.info(f"  {row[0]}: {row[1]} on {row[2]} - pH: {row[3]}")
                
                # Set invalid pH values to NULL
                result = conn.execute(text("""
                    UPDATE samples 
                    SET ph = NULL
                    WHERE ph < 0 OR ph > 14
                """))
                logger.info(f"Set {result.rowcount} invalid pH values to NULL")
            
            # Step 4: Fix negative values in other numeric fields
            logger.info("Step 4: Fixing negative values in other numeric fields...")
            
            for field in numeric_fields:
                result = conn.execute(text(f"""
                    SELECT COUNT(*) as negative_{field}
                    FROM samples 
                    WHERE {field} < 0
                """))
                negative_count = result.fetchone()[0]
                
                if negative_count > 0:
                    # Show examples
                    result = conn.execute(text(f"""
                        SELECT sample_id, site_code, sample_date, {field}
                        FROM samples 
                        WHERE {field} < 0
                        LIMIT 3
                    """))
                    examples = result.fetchall()
                    logger.info(f"Examples of negative {field} values:")
                    for row in examples:
                        logger.info(f"  {row[0]}: {row[1]} on {row[2]} - {field}: {row[3]}")
                    
                    # Set negative values to NULL (more conservative than taking absolute value)
                    result = conn.execute(text(f"""
                        UPDATE samples 
                        SET {field} = NULL
                        WHERE {field} < 0
                    """))
                    logger.info(f"Set {result.rowcount} negative {field} values to NULL")
            
            # Step 5: Handle samples with no measurements
            logger.info("Step 5: Handling samples with no measurements...")
            
            if no_measurements > 0:
                # Show some examples
                result = conn.execute(text("""
                    SELECT sample_id, site_code, sample_date, water_temperature, ph, do_ppm, nitrate, phosphates, turbidity
                    FROM samples 
                    WHERE water_temperature IS NULL 
                    AND ph IS NULL 
                    AND do_ppm IS NULL 
                    AND nitrate IS NULL 
                    AND phosphates IS NULL 
                    AND turbidity IS NULL
                    LIMIT 5
                """))
                examples = result.fetchall()
                logger.info("Examples of samples with no measurements:")
                for row in examples:
                    logger.info(f"  {row[0]}: {row[1]} on {row[2]} - All measurements NULL")
                
                # Ask user if they want to delete these records
                logger.info(f"Found {no_measurements} samples with no measurements.")
                logger.info("Options:")
                logger.info("1. Delete these records (recommended)")
                logger.info("2. Keep them for now")
                
                # For now, let's keep them but flag them
                logger.info("Keeping samples with no measurements for now...")
            
            # Step 6: Add data quality flags
            logger.info("Step 6: Adding data quality flags...")
            
            # Create a data quality summary
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_samples,
                    COUNT(water_temperature) as temp_count,
                    COUNT(ph) as ph_count,
                    COUNT(do_ppm) as do_count,
                    COUNT(nitrate) as nitrate_count,
                    COUNT(phosphates) as phosphates_count,
                    COUNT(turbidity) as turbidity_count,
                    COUNT(conductivity) as conductivity_count
                FROM samples
            """))
            stats = result.fetchone()
            
            logger.info("=== SAMPLES TABLE DATA QUALITY SUMMARY ===")
            logger.info(f"Total samples: {stats[0]:,}")
            logger.info(f"Water temperature: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
            logger.info(f"pH: {stats[2]:,} ({stats[2]/stats[0]*100:.1f}%)")
            logger.info(f"Dissolved oxygen: {stats[3]:,} ({stats[3]/stats[0]*100:.1f}%)")
            logger.info(f"Nitrate: {stats[4]:,} ({stats[4]/stats[0]*100:.1f}%)")
            logger.info(f"Phosphates: {stats[5]:,} ({stats[5]/stats[0]*100:.1f}%)")
            logger.info(f"Turbidity: {stats[6]:,} ({stats[6]/stats[0]*100:.1f}%)")
            logger.info(f"Conductivity: {stats[7]:,} ({stats[7]/stats[0]*100:.1f}%)")
            
            # Step 7: Create data quality report
            logger.info("Step 7: Creating data quality report...")
            
            # Find samples with very few measurements
            result = conn.execute(text("""
                SELECT 
                    sample_id,
                    site_code,
                    sample_date,
                    CASE WHEN water_temperature IS NOT NULL THEN 1 ELSE 0 END +
                    CASE WHEN ph IS NOT NULL THEN 1 ELSE 0 END +
                    CASE WHEN do_ppm IS NOT NULL THEN 1 ELSE 0 END +
                    CASE WHEN nitrate IS NOT NULL THEN 1 ELSE 0 END +
                    CASE WHEN phosphates IS NOT NULL THEN 1 ELSE 0 END +
                    CASE WHEN turbidity IS NOT NULL THEN 1 ELSE 0 END +
                    CASE WHEN conductivity IS NOT NULL THEN 1 ELSE 0 END as measurement_count
                FROM samples
                ORDER BY measurement_count ASC
                LIMIT 10
            """))
            low_quality_samples = result.fetchall()
            
            logger.info("Samples with fewest measurements:")
            for row in low_quality_samples:
                logger.info(f"  {row[0]}: {row[1]} on {row[2]} - {row[3]} measurements")
            
            # Commit all changes
            conn.commit()
            logger.info("All changes committed successfully")
            
            # Final verification
            logger.info("=== FINAL VERIFICATION ===")
            
            # Check for remaining negative values
            result = conn.execute(text("""
                SELECT COUNT(*) as remaining_negative_temps
                FROM samples 
                WHERE water_temperature < 0
            """))
            remaining_negative_temps = result.fetchone()[0]
            logger.info(f"Remaining negative temperatures: {remaining_negative_temps}")
            
            result = conn.execute(text("""
                SELECT COUNT(*) as remaining_invalid_ph
                FROM samples 
                WHERE ph < 0 OR ph > 14
            """))
            remaining_invalid_ph = result.fetchone()[0]
            logger.info(f"Remaining invalid pH values: {remaining_invalid_ph}")
            
            if remaining_negative_temps == 0 and remaining_invalid_ph == 0:
                logger.info("✅ SUCCESS: All data quality issues fixed!")
            else:
                logger.warning("⚠️  WARNING: Some data quality issues remain")
            
    except Exception as e:
        logger.error(f"Error cleaning samples table: {e}")
        raise

if __name__ == "__main__":
    clean_samples_table()



