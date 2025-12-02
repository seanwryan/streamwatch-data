#!/usr/bin/env python3
"""
Test script to verify database fixes work correctly
This script runs before and after fixes to measure improvement
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_quality():
    """Test database quality before and after fixes"""
    logger.info("Testing database quality...")
    
    try:
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Test 1: Bugs table data completeness
            logger.info("=== BUGS TABLE QUALITY TEST ===")
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(percentage) as percentage_count,
                    COUNT(tolerance) as tolerance_count,
                    COUNT(ept) as ept_count,
                    COUNT(insect) as insect_count,
                    COUNT(sensitive) as sensitive_count
                FROM bugs
            """))
            stats = result.fetchone()
            
            logger.info(f"Total bug records: {stats[0]:,}")
            logger.info(f"Records with percentage: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
            logger.info(f"Records with tolerance: {stats[2]:,} ({stats[2]/stats[0]*100:.1f}%)")
            logger.info(f"Records with ept: {stats[3]:,} ({stats[3]/stats[0]*100:.1f}%)")
            logger.info(f"Records with insect: {stats[4]:,} ({stats[4]/stats[0]*100:.1f}%)")
            logger.info(f"Records with sensitive: {stats[5]:,} ({stats[5]/stats[0]*100:.1f}%)")
            
            # Test 2: Foreign key relationships
            logger.info("\n=== FOREIGN KEY RELATIONSHIPS TEST ===")
            result = conn.execute(text("""
                SELECT COUNT(*) as orphaned_bugs
                FROM bugs bg 
                LEFT JOIN samples s ON bg.sample_code = s.sample_id 
                WHERE s.sample_id IS NULL
            """))
            orphaned_bugs = result.fetchone()[0]
            logger.info(f"Orphaned bug records: {orphaned_bugs}")
            
            # Test 3: Samples table data quality
            logger.info("\n=== SAMPLES TABLE QUALITY TEST ===")
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_samples,
                    COUNT(CASE WHEN water_temperature < 0 THEN 1 END) as negative_temps,
                    COUNT(CASE WHEN ph < 0 OR ph > 14 THEN 1 END) as invalid_ph,
                    COUNT(CASE WHEN water_temperature IS NULL AND ph IS NULL AND do_ppm IS NULL THEN 1 END) as no_measurements
                FROM samples
            """))
            stats = result.fetchone()
            
            logger.info(f"Total samples: {stats[0]:,}")
            logger.info(f"Negative temperatures: {stats[1]:,}")
            logger.info(f"Invalid pH values: {stats[2]:,}")
            logger.info(f"Samples with no measurements: {stats[3]:,}")
            
            # Test 4: Data completeness summary
            logger.info("\n=== DATA COMPLETENESS SUMMARY ===")
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_samples,
                    COUNT(water_temperature) as temp_count,
                    COUNT(ph) as ph_count,
                    COUNT(do_ppm) as do_count,
                    COUNT(nitrate) as nitrate_count,
                    COUNT(phosphates) as phosphates_count,
                    COUNT(turbidity) as turbidity_count
                FROM samples
            """))
            stats = result.fetchone()
            
            logger.info(f"Water temperature: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
            logger.info(f"pH: {stats[2]:,} ({stats[2]/stats[0]*100:.1f}%)")
            logger.info(f"Dissolved oxygen: {stats[3]:,} ({stats[3]/stats[0]*100:.1f}%)")
            logger.info(f"Nitrate: {stats[4]:,} ({stats[4]/stats[0]*100:.1f}%)")
            logger.info(f"Phosphates: {stats[5]:,} ({stats[5]/stats[0]*100:.1f}%)")
            logger.info(f"Turbidity: {stats[6]:,} ({stats[6]/stats[0]*100:.1f}%)")
            
            # Test 5: Sample some actual data
            logger.info("\n=== SAMPLE DATA PREVIEW ===")
            result = conn.execute(text("""
                SELECT sample_code, order_name, family, count, percentage, tolerance, ept
                FROM bugs 
                WHERE percentage IS NOT NULL
                LIMIT 5
            """))
            sample_bugs = result.fetchall()
            logger.info("Sample bug records:")
            for row in sample_bugs:
                logger.info(f"  {row[0]}: {row[1]} - {row[2]} | Count: {row[3]}, %: {row[4]:.1f}, Tol: {row[5]}, EPT: {row[6]}")
            
            result = conn.execute(text("""
                SELECT sample_id, site_code, sample_date, water_temperature, ph, do_ppm
                FROM samples 
                WHERE water_temperature IS NOT NULL
                LIMIT 5
            """))
            sample_samples = result.fetchall()
            logger.info("Sample water quality records:")
            for row in sample_samples:
                logger.info(f"  {row[0]}: {row[1]} on {row[2]} - Temp: {row[3]}, pH: {row[4]}, DO: {row[5]}")
            
            # Overall assessment
            logger.info("\n=== OVERALL ASSESSMENT ===")
            
            bugs_quality = (stats[1] + stats[2] + stats[3] + stats[4] + stats[5]) / (stats[0] * 5) * 100
            samples_quality = (stats[1] + stats[2] + stats[3] + stats[4] + stats[5] + stats[6]) / (stats[0] * 6) * 100
            
            logger.info(f"Bugs table data completeness: {bugs_quality:.1f}%")
            logger.info(f"Samples table data completeness: {samples_quality:.1f}%")
            logger.info(f"Foreign key integrity: {'✅ Good' if orphaned_bugs == 0 else '❌ Issues'}")
            
            if bugs_quality > 80 and samples_quality > 50 and orphaned_bugs == 0:
                logger.info("🎉 DATABASE QUALITY: EXCELLENT")
            elif bugs_quality > 60 and samples_quality > 30 and orphaned_bugs < 100:
                logger.info("✅ DATABASE QUALITY: GOOD")
            else:
                logger.info("⚠️  DATABASE QUALITY: NEEDS IMPROVEMENT")
            
    except Exception as e:
        logger.error(f"Error testing database quality: {e}")
        raise

if __name__ == "__main__":
    test_database_quality()



