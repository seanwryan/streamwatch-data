#!/usr/bin/env python3
"""
Test loading a few sites records to debug the issue
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_load_sites():
    """Test loading a few sites records"""
    logger.info("Testing sites data loading...")
    
    try:
        # Read sites data
        file_path = "data/raw/2025 StreamWatch Locations.xlsx"
        df = pd.read_excel(file_path)
        
        logger.info(f"Excel file has {len(df)} rows")
        logger.info(f"Columns: {df.columns.tolist()}")
        
        # Take just the first 3 rows for testing
        df = df.head(3)
        
        # Clean and transform data to match database schema
        df['site_code'] = df.get('SiteCode', pd.Series([''] * len(df))).astype(str).apply(lambda x: x.strip().upper() if pd.notna(x) and x != '' else None)
        df['is_active'] = df.get('isActive', pd.Series([True] * len(df))).apply(lambda x: bool(x) if pd.notna(x) else True)
        df['waterbody'] = df.get('WaterBody', pd.Series([''] * len(df))).astype(str).apply(lambda x: x.strip().upper() if pd.notna(x) and x != '' else None)
        df['latitude'] = pd.to_numeric(df.get('Latitude', pd.Series([''] * len(df))), errors='coerce')
        df['longitude'] = pd.to_numeric(df.get('Longitude', pd.Series([''] * len(df))), errors='coerce')
        
        # Select only essential columns for testing
        columns_to_keep = ['site_code', 'is_active', 'waterbody', 'latitude', 'longitude']
        df = df[columns_to_keep]
        
        # Remove rows with missing site_code
        df = df.dropna(subset=['site_code'])
        df = df[df['site_code'] != '']
        
        logger.info(f"Processed {len(df)} records for loading")
        logger.info(f"Sample data:")
        for idx, row in df.iterrows():
            logger.info(f"  {row['site_code']}: {row['waterbody']} ({row['latitude']}, {row['longitude']})")
        
        # Connect to database and load data
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        df.to_sql('sites', engine, if_exists='append', index=False, method='multi')
        logger.info(f"Successfully loaded {len(df)} site records")
        
        # Verify the data was loaded
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM sites")).scalar()
            logger.info(f"Total sites in database: {count}")
            
            # Show the loaded records
            result = conn.execute(text("SELECT site_code, waterbody, latitude, longitude FROM sites ORDER BY site_code LIMIT 5"))
            logger.info("Loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} ({row[2]}, {row[3]})")
        
    except Exception as e:
        logger.error(f"Error loading sites data: {e}")
        raise

if __name__ == "__main__":
    test_load_sites()
