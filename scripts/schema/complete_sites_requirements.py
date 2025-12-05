#!/usr/bin/env python3
"""
Complete Sites Table Requirements Implementation

This script implements all missing pieces from the SITES Table Schema requirements:
- Adds missing fields (notes, site_flag, map_link, last_bact_sample_date)
- Creates lookup tables (waterbodies, subwatersheds)
- Creates junction tables for many-to-many relationships
- Migrates data from VARCHAR to FK relationships
- Creates VIEWs for calculated fields

Run with database owner credentials.
"""

import sys
import os
from sqlalchemy import create_engine, text
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def complete_sites_requirements():
    """Complete the sites table requirements implementation"""
    
    DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                logger.info("="*60)
                logger.info("COMPLETING SITES TABLE REQUIREMENTS")
                logger.info("="*60)
                
                # Read and execute the SQL script
                sql_file = os.path.join(os.path.dirname(__file__), 'complete_sites_requirements.sql')
                with open(sql_file, 'r') as f:
                    sql_script = f.read()
                
                # Split by semicolons and execute each statement
                # Skip comments and empty statements
                statements = [s.strip() for s in sql_script.split(';') if s.strip() and not s.strip().startswith('--')]
                
                for i, statement in enumerate(statements, 1):
                    if statement and not statement.startswith('--'):
                        try:
                            # Skip BEGIN/COMMIT as we handle transactions manually
                            if statement.upper().strip() in ['BEGIN', 'COMMIT']:
                                continue
                            
                            logger.info(f"Executing statement {i}/{len(statements)}...")
                            conn.execute(text(statement))
                        except Exception as e:
                            # Some statements might fail if already executed (IF NOT EXISTS)
                            if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                                logger.warning(f"Statement {i} skipped (already exists): {str(e)[:100]}")
                            else:
                                logger.error(f"Error in statement {i}: {e}")
                                raise
                
                # Commit transaction
                trans.commit()
                logger.info("="*60)
                logger.info("✅ SITES TABLE REQUIREMENTS COMPLETED SUCCESSFULLY")
                logger.info("="*60)
                
                # Run verification queries
                logger.info("\nVerification Results:")
                
                # Check new fields
                result = conn.execute(text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'sites'
                      AND column_name IN ('notes', 'site_flag', 'map_link', 'last_bact_sample_date', 'waterbody_id')
                    ORDER BY column_name
                """))
                logger.info("\nNew fields added:")
                for row in result:
                    logger.info(f"  - {row[0]}: {row[1]}")
                
                # Check lookup tables
                result = conn.execute(text("""
                    SELECT 'waterbodies' as table_name, COUNT(*) as count FROM waterbodies
                    UNION ALL
                    SELECT 'subwatersheds', COUNT(*) FROM subwatersheds
                """))
                logger.info("\nLookup tables populated:")
                for row in result:
                    logger.info(f"  - {row[0]}: {row[1]} records")
                
                # Check junction tables
                result = conn.execute(text("""
                    SELECT 'site_subwatersheds' as table_name, COUNT(*) as count FROM site_subwatersheds
                    UNION ALL
                    SELECT 'site_municipalities', COUNT(*) FROM site_municipalities
                """))
                logger.info("\nJunction tables:")
                for row in result:
                    logger.info(f"  - {row[0]}: {row[1]} records")
                
                # Check VIEWs
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.views
                    WHERE table_schema = 'public'
                      AND table_name LIKE 'sites%'
                    ORDER BY table_name
                """))
                logger.info("\nVIEWs created:")
                for row in result:
                    logger.info(f"  - {row[0]}")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error completing sites requirements: {e}")
                raise
                
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

if __name__ == "__main__":
    complete_sites_requirements()
