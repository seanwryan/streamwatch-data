#!/usr/bin/env python3
"""
Fix bugs table by populating calculated fields
This script addresses the critical issue of 100% NULL values in calculated fields
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_bugs_table():
    """Populate calculated fields in bugs table"""
    logger.info("Starting bugs table fixes...")
    
    try:
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # First, let's understand the current state
            logger.info("Analyzing current bugs table state...")
            
            # Check current NULL percentages
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(percentage) as percentage_count,
                    COUNT(tolerance) as tolerance_count,
                    COUNT(ept) as ept_count,
                    COUNT(insect) as insect_count
                FROM bugs
            """))
            stats = result.fetchone()
            logger.info(f"Total records: {stats[0]:,}")
            logger.info(f"Records with percentage: {stats[1]:,}")
            logger.info(f"Records with tolerance: {stats[2]:,}")
            logger.info(f"Records with ept: {stats[3]:,}")
            logger.info(f"Records with insect: {stats[4]:,}")
            
            # Step 1: Calculate percentages for each sample
            logger.info("Step 1: Calculating percentages for each sample...")
            
            # Get total counts per sample
            result = conn.execute(text("""
                SELECT sample_code, SUM(count) as total_count
                FROM bugs 
                WHERE sample_code IS NOT NULL AND sample_code != ''
                GROUP BY sample_code
            """))
            sample_totals = {row[0]: row[1] for row in result.fetchall()}
            logger.info(f"Found {len(sample_totals)} samples with bug counts")
            
            # Update percentages
            updated_count = 0
            for sample_code, total_count in sample_totals.items():
                if total_count > 0:
                    result = conn.execute(text("""
                        UPDATE bugs 
                        SET percentage = (count::float / :total_count * 100)
                        WHERE sample_code = :sample_code
                    """), {"total_count": total_count, "sample_code": sample_code})
                    updated_count += result.rowcount
            
            logger.info(f"Updated percentages for {updated_count} records")
            
            # Step 2: Populate tolerance values from taxonomy table
            logger.info("Step 2: Populating tolerance values from taxonomy...")
            
            result = conn.execute(text("""
                UPDATE bugs 
                SET tolerance = t.tolerance_value
                FROM taxonomy t 
                WHERE bugs.family = t.family 
                AND bugs.tolerance IS NULL
            """))
            logger.info(f"Updated tolerance for {result.rowcount} records")
            
            # Step 3: Populate EPT and insect flags from taxonomy
            logger.info("Step 3: Populating EPT and insect flags...")
            
            result = conn.execute(text("""
                UPDATE bugs 
                SET ept = t.ept
                FROM taxonomy t 
                WHERE bugs.family = t.family 
                AND bugs.ept IS NULL
            """))
            logger.info(f"Updated EPT flag for {result.rowcount} records")
            
            result = conn.execute(text("""
                UPDATE bugs 
                SET insect = t.insect
                FROM taxonomy t 
                WHERE bugs.family = t.family 
                AND bugs.insect IS NULL
            """))
            logger.info(f"Updated insect flag for {result.rowcount} records")
            
            # Step 4: Calculate derived fields
            logger.info("Step 4: Calculating derived fields...")
            
            # Calculate sensitive flag (EPT taxa are generally more sensitive)
            result = conn.execute(text("""
                UPDATE bugs 
                SET sensitive = CASE 
                    WHEN ept = true THEN true
                    WHEN order_name IN ('Ephemeroptera', 'Plecoptera', 'Trichoptera') THEN true
                    ELSE false
                END
                WHERE sensitive IS NULL
            """))
            logger.info(f"Updated sensitive flag for {result.rowcount} records")
            
            # Calculate functional feeding groups based on order/family
            result = conn.execute(text("""
                UPDATE bugs 
                SET scraper = CASE 
                    WHEN order_name = 'Ephemeroptera' AND family LIKE '%Heptageniidae%' THEN true
                    WHEN order_name = 'Trichoptera' AND family LIKE '%Glossosomatidae%' THEN true
                    ELSE false
                END
                WHERE scraper IS NULL
            """))
            logger.info(f"Updated scraper flag for {result.rowcount} records")
            
            result = conn.execute(text("""
                UPDATE bugs 
                SET clinger = CASE 
                    WHEN order_name = 'Trichoptera' AND family LIKE '%Hydropsychidae%' THEN true
                    WHEN order_name = 'Ephemeroptera' AND family LIKE '%Heptageniidae%' THEN true
                    ELSE false
                END
                WHERE clinger IS NULL
            """))
            logger.info(f"Updated clinger flag for {result.rowcount} records")
            
            # Step 5: Calculate product values
            logger.info("Step 5: Calculating product values...")
            
            result = conn.execute(text("""
                UPDATE bugs 
                SET product_ftv = count * 8.0  -- Default FTV value
                WHERE product_ftv IS NULL AND count IS NOT NULL
            """))
            logger.info(f"Updated product_ftv for {result.rowcount} records")
            
            result = conn.execute(text("""
                UPDATE bugs 
                SET product_tolerance = count * tolerance
                WHERE product_tolerance IS NULL AND count IS NOT NULL AND tolerance IS NOT NULL
            """))
            logger.info(f"Updated product_tolerance for {result.rowcount} records")
            
            # Commit all changes
            conn.commit()
            logger.info("All changes committed successfully")
            
            # Verify the fixes
            logger.info("Verifying fixes...")
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(percentage) as percentage_count,
                    COUNT(tolerance) as tolerance_count,
                    COUNT(ept) as ept_count,
                    COUNT(insect) as insect_count,
                    COUNT(sensitive) as sensitive_count,
                    COUNT(scraper) as scraper_count,
                    COUNT(clinger) as clinger_count,
                    COUNT(product_ftv) as product_ftv_count,
                    COUNT(product_tolerance) as product_tolerance_count
                FROM bugs
            """))
            stats = result.fetchone()
            
            logger.info("=== FINAL RESULTS ===")
            logger.info(f"Total records: {stats[0]:,}")
            logger.info(f"Records with percentage: {stats[1]:,} ({stats[1]/stats[0]*100:.1f}%)")
            logger.info(f"Records with tolerance: {stats[2]:,} ({stats[2]/stats[0]*100:.1f}%)")
            logger.info(f"Records with ept: {stats[3]:,} ({stats[3]/stats[0]*100:.1f}%)")
            logger.info(f"Records with insect: {stats[4]:,} ({stats[4]/stats[0]*100:.1f}%)")
            logger.info(f"Records with sensitive: {stats[5]:,} ({stats[5]/stats[0]*100:.1f}%)")
            logger.info(f"Records with scraper: {stats[6]:,} ({stats[6]/stats[0]*100:.1f}%)")
            logger.info(f"Records with clinger: {stats[7]:,} ({stats[7]/stats[0]*100:.1f}%)")
            logger.info(f"Records with product_ftv: {stats[8]:,} ({stats[8]/stats[0]*100:.1f}%)")
            logger.info(f"Records with product_tolerance: {stats[9]:,} ({stats[9]/stats[0]*100:.1f}%)")
            
            # Show sample of fixed data
            logger.info("Sample of fixed data:")
            result = conn.execute(text("""
                SELECT sample_code, order_name, family, count, percentage, tolerance, ept, insect, sensitive
                FROM bugs 
                WHERE percentage IS NOT NULL
                LIMIT 5
            """))
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} - {row[2]} | Count: {row[3]}, %: {row[4]:.1f}, Tol: {row[5]}, EPT: {row[6]}, Insect: {row[7]}, Sensitive: {row[8]}")
            
    except Exception as e:
        logger.error(f"Error fixing bugs table: {e}")
        raise

if __name__ == "__main__":
    fix_bugs_table()



