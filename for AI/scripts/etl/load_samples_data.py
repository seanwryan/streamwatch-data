#!/usr/bin/env python3
"""
Load samples data from All StreamWatch Data.xlsx into Neon database
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
    return str(value).strip().upper()

def load_samples_data():
    """Load samples data from All StreamWatch Data file"""
    logger.info("Loading samples data...")
    
    try:
        # Read samples data
        file_path = "data/raw/All StreamWatch Data.xlsx"
        df = pd.read_excel(file_path, sheet_name='All Data')
        
        logger.info(f"Excel file has {len(df)} rows")
        
        # Clean and transform data to match database schema
        df['sample_id'] = df.apply(lambda row: f"SAMPLE_{row.name}", axis=1)
        df['site_code'] = df.get('Site', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['sample_date'] = pd.to_datetime(df.get('Date', pd.Series([''] * len(df))), errors='coerce')
        df['sample_time'] = pd.to_datetime(df.get('Time', pd.Series([''] * len(df))), errors='coerce').dt.time
        
        # Water quality parameters (only basic ones that exist in database schema)
        df['water_temperature'] = pd.to_numeric(df.get('Water Temperature', pd.Series([''] * len(df))), errors='coerce')
        df['ph'] = pd.to_numeric(df.get('pH', pd.Series([''] * len(df))), errors='coerce')
        df['do_ppm'] = pd.to_numeric(df.get('DO ppm', pd.Series([''] * len(df))), errors='coerce')
        df['do_percent'] = pd.to_numeric(df.get('%DO', pd.Series([''] * len(df))), errors='coerce')
        
        # Handle large values that exceed database precision
        df['nitrate'] = pd.to_numeric(df.get('Nitrate', pd.Series([''] * len(df))), errors='coerce')
        df['nitrate'] = df['nitrate'].clip(upper=99999.999)  # Cap at database limit
        
        df['phosphates'] = pd.to_numeric(df.get('Phosphates', pd.Series([''] * len(df))), errors='coerce')
        df['phosphates'] = df['phosphates'].clip(upper=99999.999)  # Cap at database limit
        
        df['turbidity'] = pd.to_numeric(df.get('Turbidity', pd.Series([''] * len(df))), errors='coerce')
        df['turbidity'] = df['turbidity'].clip(upper=99999.99)  # Cap at database limit
        
        df['conductivity'] = pd.to_numeric(df.get('Conductivity', pd.Series([''] * len(df))), errors='coerce')
        df['conductivity'] = df['conductivity'].clip(upper=99999.99)  # Cap at database limit
        
        df['chloride'] = pd.to_numeric(df.get('Chloride (mg/L)', pd.Series([''] * len(df))), errors='coerce')
        df['chloride'] = df['chloride'].clip(upper=99999.99)  # Cap at database limit
        
        df['e_coli'] = pd.to_numeric(df.get('E. coli Result', pd.Series([''] * len(df))), errors='coerce')
        df['e_coli'] = df['e_coli'].clip(upper=9999999999)  # Cap at database limit
        
        # Select columns to keep (matching database schema - only basic water quality)
        columns_to_keep = [
            'sample_id', 'site_code', 'sample_date', 'sample_time',
            'water_temperature', 'ph', 'do_ppm', 'do_percent',
            'nitrate', 'phosphates', 'turbidity', 'conductivity', 'chloride',
            'e_coli'
        ]
        df = df[columns_to_keep]
        
        # Remove rows with missing site_code
        df = df.dropna(subset=['site_code'])
        df = df[df['site_code'] != '']
        
        # Connect to database first
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Filter out samples with site codes that don't exist in the sites table
        with engine.connect() as conn:
            valid_sites = conn.execute(text("SELECT site_code FROM sites")).fetchall()
            valid_site_codes = {row[0] for row in valid_sites}
        
        original_count = len(df)
        df = df[df['site_code'].isin(valid_site_codes)]
        filtered_count = len(df)
        logger.info(f"Filtered out {original_count - filtered_count} samples with invalid site codes")
        
        logger.info(f"Processed {len(df)} sample records for loading")
        
        # Load data in smaller batches to avoid SQL query issues
        batch_size = 100
        total_loaded = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('samples', engine, if_exists='append', index=False, method=None)
            total_loaded += len(batch_df)
            logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_df)} records (Total: {total_loaded})")
        
        logger.info(f"Successfully loaded {total_loaded} sample records")
        
        # Verify the data was loaded
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM samples")).scalar()
            logger.info(f"Total samples in database: {count}")
            
            # Show sample of loaded data
            result = conn.execute(text("SELECT sample_id, site_code, sample_date, water_temperature, ph, do_ppm FROM samples ORDER BY sample_date DESC LIMIT 5"))
            logger.info("Sample of loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} on {row[2]} - Temp: {row[3]}, pH: {row[4]}, DO: {row[5]}")
        
    except Exception as e:
        logger.error(f"Error loading samples data: {e}")
        raise

if __name__ == "__main__":
    load_samples_data()
