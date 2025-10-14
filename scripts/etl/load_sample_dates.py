#!/usr/bin/env python3
"""
Load sample dates data from tblSampleDates.xlsx
"""

import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_sample_dates():
    """Load sample dates data from Excel file"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Loading sample dates data...")
        
        # Read Excel file
        file_path = 'data/raw/tblSampleDates.xlsx'
        df = pd.read_excel(file_path, sheet_name='tblSampleDates')
        
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Clean the data
        df = df.dropna(subset=['SampleID'])  # Remove rows without SampleID
        
        # Convert data types
        df['SampleID'] = df['SampleID'].astype(int)
        df['SampleDate'] = pd.to_datetime(df['SampleDate'], errors='coerce')
        
        # Truncate string fields to match database schema
        df['Station'] = df['Station'].astype(str).str[:20]
        df['SampleCode'] = df['SampleCode'].astype(str).str[:50]
        
        # Rename columns to match database schema (lowercase)
        df = df.rename(columns={
            'SampleID': 'sample_id',
            'Station': 'station', 
            'SampleDate': 'sample_date',
            'SampleCode': 'sample_code'
        })
        
        # Clear existing data
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM sample_dates"))
            conn.commit()
        
        # Load data in batches
        batch_size = 1000
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('sample_dates', engine, if_exists='append', index=False, method='multi')
            logger.info(f"Loaded batch {i//batch_size + 1}/{(total_rows-1)//batch_size + 1}")
        
        logger.info(f"Successfully loaded {total_rows} sample dates records")
        return True
        
    except Exception as e:
        logger.error(f"Error loading sample dates data: {e}")
        return False

if __name__ == "__main__":
    load_sample_dates()
