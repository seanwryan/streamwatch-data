#!/usr/bin/env python3
"""
Master script to run all database fixes
This script executes all the database improvement fixes in the correct order
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set up logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'database_fixes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_all_fixes():
    """Run all database fixes in the correct order"""
    logger.info("="*60)
    logger.info("STREAMWATCH DATABASE FIXES - STARTING")
    logger.info("="*60)
    
    try:
        # Import the fix modules
        from fix_bugs_table import fix_bugs_table
        from fix_sample_code_mismatches import fix_sample_code_mismatches
        from clean_samples_table import clean_samples_table
        
        # Fix 1: Populate bugs table calculated fields
        logger.info("\n" + "="*50)
        logger.info("FIX 1: POPULATING BUGS TABLE CALCULATED FIELDS")
        logger.info("="*50)
        fix_bugs_table()
        
        # Fix 2: Resolve sample code mismatches
        logger.info("\n" + "="*50)
        logger.info("FIX 2: RESOLVING SAMPLE CODE MISMATCHES")
        logger.info("="*50)
        fix_sample_code_mismatches()
        
        # Fix 3: Clean samples table data
        logger.info("\n" + "="*50)
        logger.info("FIX 3: CLEANING SAMPLES TABLE DATA")
        logger.info("="*50)
        clean_samples_table()
        
        logger.info("\n" + "="*60)
        logger.info("ALL FIXES COMPLETED SUCCESSFULLY!")
        logger.info("="*60)
        
        # Summary
        logger.info("\nSUMMARY OF FIXES APPLIED:")
        logger.info("✅ Bugs table: Populated calculated fields (percentage, tolerance, ept, etc.)")
        logger.info("✅ Sample codes: Fixed foreign key relationships between bugs and samples")
        logger.info("✅ Samples table: Fixed negative temperatures and invalid pH values")
        logger.info("✅ Data quality: Improved overall database integrity")
        
        logger.info("\nNEXT STEPS:")
        logger.info("1. Review the log file for any warnings or errors")
        logger.info("2. Test database queries to ensure fixes work correctly")
        logger.info("3. Consider running additional fixes for sites table data")
        logger.info("4. Implement data validation rules to prevent future issues")
        
    except Exception as e:
        logger.error(f"Error running fixes: {e}")
        logger.error("Check the log file for detailed error information")
        raise

if __name__ == "__main__":
    run_all_fixes()





