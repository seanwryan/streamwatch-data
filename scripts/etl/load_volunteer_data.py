#!/usr/bin/env python3
"""
Load volunteer data from Volunteer_Tracking.xlsm into Neon database
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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

def load_volunteer_data():
    """Load volunteer data from Volunteer_Tracking.xlsm file"""
    logger.info("Loading volunteer data...")
    
    try:
        # Read volunteer data
        file_path = "data/raw/Volunteer_Tracking.xlsm"
        df = pd.read_excel(file_path, sheet_name='Volunteers', skiprows=2)
        
        logger.info(f"Excel file has {len(df)} rows")
        
        # Set proper column names
        df.columns = [
            'VolunteerID', 'FirstName', 'LastName', 'Email', 'Phone', 'Address', 
            'City', 'State', 'ZipCode', 'EmergencyContact', 'EmergencyPhone', 
            'Skills', 'Interests', 'Availability', 'Notes', 'Status', 'FullName', 'DPID'
        ]
        
        # Clean and transform data to match actual database schema with length constraints
        df['volunteer_id'] = df['VolunteerID'].astype(str).apply(clean_text_field)
        df['volunteer_id'] = df['volunteer_id'].apply(lambda x: x[:20] if x else None)  # varchar(20)
        
        df['first_name'] = df['FirstName'].astype(str).apply(clean_text_field)
        df['first_name'] = df['first_name'].apply(lambda x: x[:50] if x else None)  # varchar(50)
        
        df['last_name'] = df['LastName'].astype(str).apply(clean_text_field)
        df['last_name'] = df['last_name'].apply(lambda x: x[:50] if x else None)  # varchar(50)
        
        df['full_name'] = df['FullName'].astype(str).apply(clean_text_field)
        df['full_name'] = df['full_name'].apply(lambda x: x[:100] if x else None)  # varchar(100)
        
        df['email'] = df['Email'].astype(str).apply(clean_text_field)
        df['email'] = df['email'].apply(lambda x: x[:100] if x else None)  # varchar(100)
        
        df['phone'] = df['Phone'].astype(str).apply(clean_text_field)
        df['phone'] = df['phone'].apply(lambda x: x[:20] if x else None)  # varchar(20)
        
        df['address'] = df['Address'].astype(str).apply(clean_text_field)  # text field, no limit
        
        df['city'] = df['City'].astype(str).apply(clean_text_field)
        df['city'] = df['city'].apply(lambda x: x[:50] if x else None)  # varchar(50)
        
        df['state'] = df['State'].astype(str).apply(clean_text_field)
        # Fix state field - convert 'nan' to None and truncate to 2 chars
        df['state'] = df['state'].apply(lambda x: None if x == 'NAN' or x == 'nan' else x[:2] if x else None)  # varchar(2)
        
        df['zip_code'] = df['ZipCode'].astype(str).apply(clean_text_field)
        df['zip_code'] = df['zip_code'].apply(lambda x: x[:10] if x else None)  # varchar(10)
        
        # Map training status from the Status column
        df['training_status'] = df['Status'].astype(str).apply(clean_text_field)
        df['training_status'] = df['training_status'].apply(lambda x: x[:50] if x else None)  # varchar(50)
        
        # Map boolean fields from the Skills, Interests, Availability columns
        # These seem to contain boolean-like data based on the error output
        df['active_cat'] = df['Skills'].apply(convert_to_boolean)
        df['active_bat'] = df['Interests'].apply(convert_to_boolean)
        df['active_bact'] = df['Availability'].apply(convert_to_boolean)
        
        # Notes field
        df['notes'] = df['Notes'].astype(str).apply(clean_text_field)
        
        # Start date - not available in this data, set to None
        df['start_date'] = None
        
        # Select columns to keep (matching actual database schema)
        columns_to_keep = [
            'volunteer_id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 
            'address', 'city', 'state', 'zip_code', 'start_date', 'active_cat', 
            'active_bat', 'active_bact', 'training_status', 'notes'
        ]
        df = df[columns_to_keep]
        
        # Remove rows with missing volunteer_id and filter out header row
        df = df.dropna(subset=['volunteer_id'])
        df = df[df['volunteer_id'] != '']
        # Remove the header row (where volunteer_id is 'VolunteerID')
        df = df[df['volunteer_id'] != 'VolunteerID']
        
        logger.info(f"Processed {len(df)} volunteer records for loading")
        
        # Connect to database
        # Connect to database
        # Using hardcoded credentials from test_team_access.py to ensure it works without env vars
        DATABASE_URL = "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"
        engine = create_engine(DATABASE_URL)
        
        # Load data in smaller batches
        batch_size = 100
        total_loaded = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('volunteers', engine, if_exists='append', index=False, method=None)
            total_loaded += len(batch_df)
            logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_df)} records (Total: {total_loaded})")
        
        logger.info(f"Successfully loaded {total_loaded} volunteer records")
        
        # Verify the data was loaded
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM volunteers")).scalar()
            logger.info(f"Total volunteer records in database: {count}")
            
            # Show sample of loaded data
            result = conn.execute(text("SELECT volunteer_id, first_name, last_name, training_status FROM volunteers ORDER BY volunteer_id LIMIT 5"))
            logger.info("Sample of loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} {row[2]} - Status: {row[3]}")
        
    except Exception as e:
        logger.error(f"Error loading volunteer data: {e}")
        raise

if __name__ == "__main__":
    load_volunteer_data()