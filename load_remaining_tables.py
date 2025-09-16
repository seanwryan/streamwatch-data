#!/usr/bin/env python3
"""
Load remaining tables for StreamWatch ETL Pipeline
Loads bacteria and volunteer data into PostgreSQL database
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG, DATA_PATHS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_text_field(value):
    """Clean and standardize text fields"""
    if pd.isna(value) or value == '':
        return None
    return str(value).strip().upper()

def convert_to_boolean(value):
    """Convert various boolean representations to proper boolean"""
    if pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'y', 'active']
    return bool(value)

def load_bacteria_data():
    """Load bacteria data into the database"""
    logger.info("Loading bacteria data...")
    
    try:
        # Read bacteria data
        df = pd.read_excel(DATA_PATHS['bacteria'], sheet_name='BACT and HAB 2025 Data')
        
        # Clean and transform data
        df['bacteria_record_id'] = df.apply(lambda row: f"BACT_{row.name}", axis=1)
        df['sample_code'] = df.get('Sample Code', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['site_code'] = df.get('Monitoring Site ID', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['collection_date'] = pd.to_datetime(df.get('Date', pd.Series([''] * len(df))), errors='coerce')
        df['collection_time'] = pd.to_datetime(df.get('Time', pd.Series([''] * len(df))), errors='coerce').dt.time
        df['bacteria_type'] = pd.Series(['E.coli'] * len(df)).astype(str).apply(clean_text_field)
        df['detection_method'] = pd.Series(['Unknown'] * len(df)).astype(str).apply(clean_text_field)
        df['measurement_value'] = df.get('E. coli', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['measurement_unit'] = df.get('MeasurementUnit', pd.Series(['CFU/100mL'] * len(df))).astype(str).apply(clean_text_field)
        df['data_conditions'] = df.get('Additional Comments (optional)', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['hab_status'] = df.get('HAB Status', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['water_temperature'] = pd.to_numeric(df.get('Water Temperature', pd.Series([''] * len(df))), errors='coerce')
        df['turbidity_ntu'] = pd.to_numeric(df.get('Turbidity (NTU)', pd.Series([''] * len(df))), errors='coerce')
        
        # Select columns to keep
        columns_to_keep = [
            'bacteria_record_id', 'sample_code', 'site_code', 'collection_date', 
            'collection_time', 'bacteria_type', 'detection_method', 'measurement_value',
            'measurement_unit', 'data_conditions', 'hab_status', 'water_temperature', 'turbidity_ntu'
        ]
        df = df[columns_to_keep]
        
        # Connect to database and load data
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        df.to_sql('bacteria', engine, if_exists='append', index=False, method='multi')
        logger.info(f"Successfully loaded {len(df)} bacteria records")
        
    except Exception as e:
        logger.error(f"Error loading bacteria data: {e}")
        raise

def load_volunteer_data():
    """Load volunteer data into the database"""
    logger.info("Loading volunteer data...")
    
    try:
        # Read volunteer data
        df = pd.read_excel(DATA_PATHS['volunteers'], sheet_name='Volunteers', header=2)
        
        # Clean and transform data
        df['volunteer_id'] = df.get('VolunteerID', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['first_name'] = df.get('FirstName', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['last_name'] = df.get('LastName', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['email'] = df.get('Email', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['phone'] = df.get('Phone', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['street'] = df.get('Street', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['city'] = df.get('City', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['state'] = df.get('State', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['zip_code'] = df.get('ZipCode', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['start_date'] = pd.to_datetime(df.get('StartDate', pd.Series([''] * len(df))), errors='coerce')
        df['under_16'] = df.get('Under16', pd.Series([False] * len(df))).apply(convert_to_boolean)
        df['parent_id'] = df.get('ParentID', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['active_cat'] = df.get('ActiveCAT', pd.Series([False] * len(df))).apply(convert_to_boolean)
        df['active_bat'] = df.get('ActiveBAT', pd.Series([False] * len(df))).apply(convert_to_boolean)
        df['active_bact'] = df.get('ActiveBACT', pd.Series([False] * len(df))).apply(convert_to_boolean)
        df['status'] = df.get('Status', pd.Series(['Active'] * len(df))).astype(str).apply(clean_text_field)
        df['full_name'] = (df['first_name'] + ' ' + df['last_name']).str.strip()
        df['dpid'] = df.get('DPID', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        
        # Select columns to keep
        columns_to_keep = [
            'volunteer_id', 'first_name', 'last_name', 'email', 'phone', 'street',
            'city', 'state', 'zip_code', 'start_date', 'under_16', 'parent_id',
            'active_cat', 'active_bat', 'active_bact', 'status', 'full_name', 'dpid'
        ]
        df = df[columns_to_keep]
        
        # Connect to database and load data
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        df.to_sql('volunteers', engine, if_exists='append', index=False, method='multi')
        logger.info(f"Successfully loaded {len(df)} volunteer records")
        
    except Exception as e:
        logger.error(f"Error loading volunteer data: {e}")
        raise

def main():
    """Main function to load remaining tables"""
    logger.info("Starting to load remaining tables...")
    
    try:
        load_bacteria_data()
        load_volunteer_data()
        logger.info("Successfully loaded all remaining tables!")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main()
