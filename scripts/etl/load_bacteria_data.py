#!/usr/bin/env python3
"""
Load bacteria data from BACT and HAB 2025 Data.xlsx into Neon database
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

def load_bacteria_data():
    """Load bacteria data from BACT and HAB 2025 Data file"""
    logger.info("Loading bacteria data...")
    
    try:
        # Read bacteria data
        file_path = "data/raw/BACT and HAB 2025 Data.xlsx"
        df = pd.read_excel(file_path, sheet_name='IDEXX')
        
        logger.info(f"Excel file has {len(df)} rows")
        
        # Clean and transform data to match actual database schema
        df['bacteria_record_id'] = df.apply(lambda row: f"BACT_{row.name}", axis=1)
        df['sample_code'] = df.get('Sample Code', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['site_code'] = df.get('Sample ID', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['collection_date'] = pd.to_datetime(df.get('Date Collected', pd.Series([''] * len(df))), errors='coerce')
        df['collection_time'] = None  # Not available in this data
        
        # Map E.coli values to the e_coli column
        e_coli_values = df.get('E. coli', pd.Series([''] * len(df))).astype(str)
        # Convert text values to numeric, handling "> 2419.6" format
        e_coli_numeric = []
        for val in e_coli_values:
            if pd.isna(val) or val == '' or val == 'nan':
                e_coli_numeric.append(None)
            elif '>' in str(val):
                # Extract number after ">"
                try:
                    num = float(str(val).split('>')[1].strip())
                    e_coli_numeric.append(num)
                except:
                    e_coli_numeric.append(None)
            else:
                try:
                    e_coli_numeric.append(float(val))
                except:
                    e_coli_numeric.append(None)
        df['e_coli'] = e_coli_numeric
        
        # Set other bacteria columns to None (not available in this data)
        df['total_coliforms'] = None
        df['fecal_coliforms'] = None
        df['enterococci'] = None
        
        # Map other measurements
        df['water_temperature'] = None  # Not available in this data
        df['turbidity'] = None  # Not available in this data
        df['ph'] = None  # Not available in this data
        df['do_ppm'] = None  # Not available in this data
        df['conductivity'] = None  # Not available in this data
        
        # Store the original measurement value as text for reference
        df['measurement_value'] = df.get('E. coli', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        
        # Select columns to keep (matching actual database schema)
        columns_to_keep = [
            'bacteria_record_id', 'sample_code', 'site_code', 'collection_date', 
            'collection_time', 'measurement_value', 'water_temperature', 'turbidity',
            'ph', 'do_ppm', 'conductivity', 'total_coliforms', 'fecal_coliforms', 
            'e_coli', 'enterococci'
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
        logger.info(f"Filtered out {original_count - filtered_count} bacteria records with invalid site codes")
        
        logger.info(f"Processed {len(df)} bacteria records for loading")
        
        # Load data in smaller batches to avoid SQL query issues
        batch_size = 100
        total_loaded = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('bacteria', engine, if_exists='append', index=False, method=None)
            total_loaded += len(batch_df)
            logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_df)} records (Total: {total_loaded})")
        
        logger.info(f"Successfully loaded {total_loaded} bacteria records")
        
        # Verify the data was loaded
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM bacteria")).scalar()
            logger.info(f"Total bacteria records in database: {count}")
            
            # Show sample of loaded data
            result = conn.execute(text("SELECT bacteria_record_id, site_code, collection_date, e_coli FROM bacteria ORDER BY collection_date DESC LIMIT 5"))
            logger.info("Sample of loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} on {row[2]} - E.coli: {row[3]}")
        
    except Exception as e:
        logger.error(f"Error loading bacteria data: {e}")
        raise

if __name__ == "__main__":
    load_bacteria_data()