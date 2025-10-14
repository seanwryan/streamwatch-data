#!/usr/bin/env python3
"""
Load CAT meters data from CAT Meter Tracking.xlsx
"""

import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_cat_meters():
    """Load CAT meters data from Excel file"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Loading CAT meters data...")
        
        # Read Excel file - Sheet2 has the basic meter info
        file_path = 'data/raw/CAT Meter Tracking.xlsx'
        df = pd.read_excel(file_path, sheet_name='Sheet2')
        
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Clean the data
        df = df.dropna(subset=['Meter ID'])  # Remove rows without Meter ID
        
        # Truncate string fields to match database schema
        df['Meter ID'] = df['Meter ID'].astype(str).str[:20]
        df['Volunteer'] = df['Volunteer'].astype(str).str[:200]
        
        # Rename columns to match database schema (lowercase)
        df = df.rename(columns={
            'Meter ID': 'meter_id',
            'Volunteer': 'volunteer'
        })
        
        # Add default values for other columns
        df['serial_number'] = None
        df['probe_id'] = None
        df['meter_type'] = 'CAT'
        df['status'] = 'Active'
        df['last_calibration_date'] = None
        df['notes'] = None
        
        # Clear existing data
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM cat_meters"))
            conn.commit()
        
        # Load data
        df.to_sql('cat_meters', engine, if_exists='append', index=False, method='multi')
        
        logger.info(f"Successfully loaded {len(df)} CAT meters records")
        return True
        
    except Exception as e:
        logger.error(f"Error loading CAT meters data: {e}")
        return False

if __name__ == "__main__":
    load_cat_meters()
