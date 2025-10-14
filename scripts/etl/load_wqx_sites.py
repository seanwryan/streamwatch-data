#!/usr/bin/env python3
"""
Load WQX sites data from 2024 TWI WQX Submission.xlsx
"""

import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_wqx_sites():
    """Load WQX sites data from Excel file"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Loading WQX sites data...")
        
        # Read Excel file
        file_path = 'data/raw/2024 TWI WQX Submission.xlsx'
        df = pd.read_excel(file_path, sheet_name='WQX sites')
        
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Clean the data
        df = df.dropna(subset=['Monitoring Location ID'])  # Remove rows without Location ID
        
        # Convert data types
        df['Latitude Measure'] = pd.to_numeric(df['Latitude Measure'], errors='coerce')
        df['Longitude Measure'] = pd.to_numeric(df['Longitude Measure'], errors='coerce')
        df['Source Map Scale Numeric'] = pd.to_numeric(df['Source Map Scale Numeric'], errors='coerce').astype('Int64')
        
        # Handle boolean column
        df['Tribal Land Indicator'] = df['Tribal Land Indicator'].astype(bool)
        
        # Truncate string fields to match database schema
        string_columns = {
            'Monitoring Location ID': 50,
            'Monitoring Location Name': 200,
            'Monitoring Location Type Name': 100,
            'Tribal Land Name': 200,
            'Horizontal Collection Method Name': 100,
            'Horizontal Coordinate Reference System Datum Name': 100,
            'State Code': 2,
            'County Name': 100,
            'Auto-Generated County Code': 10,
            'HUC Eight Digit Code': 8,
            'HUC Twelve Digit Code': 12
        }
        
        for col, max_len in string_columns.items():
            if col in df.columns:
                df[col] = df[col].astype(str).str[:max_len]
        
        # Rename columns to match database schema (lowercase with underscores)
        df = df.rename(columns={
            'Monitoring Location ID': 'monitoring_location_id',
            'Monitoring Location Name': 'monitoring_location_name',
            'Monitoring Location Type Name': 'monitoring_location_type_name',
            'Tribal Land Indicator': 'tribal_land_indicator',
            'Tribal Land Name': 'tribal_land_name',
            'Latitude Measure': 'latitude_measure',
            'Longitude Measure': 'longitude_measure',
            'Source Map Scale Numeric': 'source_map_scale_numeric',
            'Horizontal Collection Method Name': 'horizontal_collection_method_name',
            'Horizontal Coordinate Reference System Datum Name': 'horizontal_coordinate_reference_system_datum_name',
            'State Code': 'state_code',
            'County Name': 'county_name',
            'Auto-Generated County Code': 'auto_generated_county_code',
            'HUC Eight Digit Code': 'huc_eight_digit_code',
            'HUC Twelve Digit Code': 'huc_twelve_digit_code'
        })
        
        # Clear existing data
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM wqx_sites"))
            conn.commit()
        
        # Load data
        df.to_sql('wqx_sites', engine, if_exists='append', index=False, method='multi')
        
        logger.info(f"Successfully loaded {len(df)} WQX sites records")
        return True
        
    except Exception as e:
        logger.error(f"Error loading WQX sites data: {e}")
        return False

if __name__ == "__main__":
    load_wqx_sites()
