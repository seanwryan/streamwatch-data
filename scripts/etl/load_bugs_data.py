#!/usr/bin/env python3
"""
Load bugs data from BATSITES COLLECTED.xlsx into Neon database
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_text_field(value):
    """Clean and standardize text fields"""
    if pd.isna(value) or value == '':
        return None
    return str(value).strip()

def convert_to_boolean(value):
    """Convert various boolean representations to proper boolean"""
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'y', 'active']
    return bool(value)

def load_bugs_data():
    """Load bugs data from BATSITES COLLECTED.xlsx file"""
    logger.info("Loading bugs data...")
    
    try:
        # Read bugs data
        file_path = "data/raw/BATSITES COLLECTED.xlsx"
        df = pd.read_excel(file_path, sheet_name='BUGSPICKED')
        
        logger.info(f"Excel file has {len(df)} rows")
        
        # Clean and transform data to match database schema
        # Create unique bug_record_id by combining BUGID# with row index to handle duplicates
        df['bug_record_id'] = df.apply(lambda row: f"BUG_{row['BUGID#']}_{row.name}", axis=1)
        df['sample_code'] = df['SampleCode'].astype(str).apply(clean_text_field)
        df['order_name'] = df['Order'].astype(str).apply(clean_text_field)
        df['family'] = df['Family'].astype(str).apply(clean_text_field)
        df['count'] = pd.to_numeric(df['Number'], errors='coerce')
        
        # Set other columns to None (not available in this data)
        df['percentage'] = None
        df['tolerance'] = None
        df['ept'] = None
        df['insect'] = None
        df['sensitive'] = None
        df['scraper'] = None
        df['clinger'] = None
        df['product_ftv'] = None
        df['product_tolerance'] = None
        df['talu_attribute'] = None
        df['ftv'] = None
        
        # Select columns to keep (matching database schema)
        columns_to_keep = [
            'bug_record_id', 'sample_code', 'order_name', 'family', 'count',
            'percentage', 'tolerance', 'ept', 'insect', 'sensitive', 'scraper',
            'clinger', 'product_ftv', 'product_tolerance', 'talu_attribute', 'ftv'
        ]
        df = df[columns_to_keep]
        
        # Remove rows with missing bug_record_id or sample_code
        df = df.dropna(subset=['bug_record_id', 'sample_code'])
        df = df[df['bug_record_id'] != '']
        df = df[df['sample_code'] != '']
        
        logger.info(f"Processed {len(df)} bug records for loading")
        
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data in smaller batches
        batch_size = 1000
        total_loaded = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('bugs', engine, if_exists='append', index=False, method=None)
            total_loaded += len(batch_df)
            logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_df)} records (Total: {total_loaded})")
        
        logger.info(f"Successfully loaded {total_loaded} bug records")
        
        # Verify the data was loaded
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM bugs")).scalar()
            logger.info(f"Total bug records in database: {count}")
            
            # Show sample of loaded data
            result = conn.execute(text("SELECT bug_record_id, sample_code, order_name, family, count FROM bugs ORDER BY bug_record_id LIMIT 5"))
            logger.info("Sample of loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} - {row[2]} {row[3]} (count: {row[4]})")
        
    except Exception as e:
        logger.error(f"Error loading bugs data: {e}")
        raise

if __name__ == "__main__":
    load_bugs_data()
