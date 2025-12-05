#!/usr/bin/env python3
"""
Load sites data from 2025 StreamWatch Locations.xlsx into Neon database
Structure aligns with Volunteers table (Strict Enums, etc.)
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
    val_str = str(value).lower().strip()
    if val_str in ['true', '1', 'yes', 'y', 'active']:
        return True
    return False

def map_status(value):
    """Map raw status to allowed Enums: Active, Inactive, Proposed, Unknown"""
    if pd.isna(value) or value == '':
        return 'Unknown'
    
    val_str = str(value).strip().title() # Title case: "Active", "Vacant", "Retired"
    
    if val_str in ['Active', 'Vacant']:
        return 'Active'
    elif val_str in ['Inactive', 'Retired', 'Retire']:
        return 'Inactive'
    elif val_str in ['Groundtruth', 'Proposed', 'Pending', 'V. Req']:
        return 'Proposed'
    else:
        return 'Unknown'

def load_sites_data():
    """Load sites data from 2025 StreamWatch Locations.xlsx file"""
    logger.info("Loading sites data...")
    
    try:
        # Read Excel file
        file_path = "data/raw/2025 StreamWatch Locations.xlsx"
        # The file has no sheet name specified in previous check, probably first sheet
        df = pd.read_excel(file_path)
        
        logger.info(f"Excel file has {len(df)} rows")
        
        # Rename columns to match database schema
        # Handle the typo in Last_BAT_Sample_Date
        column_mapping = {
            'SiteCode': 'site_code',
            'isActive': 'is_active',
            'Groundtruthing Priority': 'groundtruthing_priority',
            'Groundtruthing Status': 'groundtruthing_status',
            'WaterBody': 'waterbody',
            'Subwatershed': 'subwatershed',
            'Description': 'description',
            'Type of Property': 'property_type',
            'Permission': 'permission',
            'Walk Time': 'walk_time',
            'Walk Distance': 'walk_distance',
            'Walk Gradient': 'walk_gradient',
            'Water Access': 'water_access',
            'Additional Comments': 'additional_comments',
            'Environmental Hazards': 'environmental_hazards',
            'Parking Details': 'parking_details',
            'Walking Directions': 'walking_directions',
            'HabitatType': 'habitat_type',
            'Latitude': 'latitude',
            'Longitude': 'longitude',
            'Type': 'site_type',
            'CAT_Priority': 'cat_priority',
            'CAT_Status': 'cat_status',
            'Last_CAT_Sample_Date': 'last_cat_sample_date',
            'BAT_Priority': 'bat_priority',
            'BAT_Status': 'bat_status',
            'Last_BAT_Sa,mple_Date': 'last_bat_sample_date', # Typo handled
            'BACT_Priority': 'bact_priority',
            'BACT_Status': 'bact_status',
            'DrainageArea': 'drainage_area'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Clean Data
        df['site_code'] = df['site_code'].apply(clean_text_field)
        df['is_active'] = df['is_active'].apply(convert_to_boolean)
        
        # Map Statuses
        status_cols = ['cat_status', 'bat_status', 'bact_status']
        for col in status_cols:
            if col in df.columns:
                df[col] = df[col].apply(map_status)
        
        # Handle Dates
        date_cols = ['last_cat_sample_date', 'last_bat_sample_date']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
        
        # Clean text fields and enforce lengths
        # VARCHAR(100)
        df['waterbody'] = df['waterbody'].apply(clean_text_field).apply(lambda x: x[:100] if x else None)
        df['subwatershed'] = df['subwatershed'].apply(clean_text_field).apply(lambda x: x[:100] if x else None)
        
        # VARCHAR(50)
        varchar_50_cols = [
            'groundtruthing_priority', 'groundtruthing_status', 'property_type', 
            'permission', 'walk_time', 'walk_distance', 'walk_gradient', 'water_access', 
            'habitat_type', 'site_type', 'cat_priority', 'cat_status', 
            'bat_priority', 'bat_status', 'bact_priority', 'bact_status'
        ]
        
        for col in varchar_50_cols:
             if col in df.columns:
                 df[col] = df[col].apply(clean_text_field).apply(lambda x: x[:50] if x else None)

        # TEXT fields (no limit)
        text_cols = ['description', 'additional_comments', 'environmental_hazards', 
                    'parking_details', 'walking_directions']
        for col in text_cols:
             if col in df.columns:
                 df[col] = df[col].apply(clean_text_field)

        # Numerics
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['drainage_area'] = pd.to_numeric(df['drainage_area'], errors='coerce')

        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        logger.info(f"Processed {len(df)} site records for loading")
        
        # UPSERT STRATEGY using temporary table
        # 1. Load to temp table
        # 2. Update existing in main table
        # 3. Insert new 
        
        with engine.connect() as conn:
            # Create temp table matching schema of dataframe
            df.to_sql('sites_staging', engine, if_exists='replace', index=False)
            
            # Upsert Logic
            upsert_query = text("""
                INSERT INTO sites (
                    site_code, is_active, groundtruthing_priority, groundtruthing_status,
                    waterbody, subwatershed, description, property_type, permission,
                    walk_time, walk_distance, walk_gradient, water_access,
                    additional_comments, environmental_hazards, parking_details,
                    walking_directions, habitat_type, latitude, longitude,
                    site_type, cat_priority, cat_status, last_cat_sample_date,
                    bat_priority, bat_status, last_bat_sample_date,
                    bact_priority, bact_status, drainage_area
                )
                SELECT 
                    site_code, is_active, groundtruthing_priority, groundtruthing_status,
                    waterbody, subwatershed, description, property_type, permission,
                    walk_time, walk_distance, walk_gradient, water_access,
                    additional_comments, environmental_hazards, parking_details,
                    walking_directions, habitat_type, latitude, longitude,
                    site_type, cat_priority, cat_status, last_cat_sample_date,
                    bat_priority, bat_status, last_bat_sample_date,
                    bact_priority, bact_status, drainage_area
                FROM sites_staging
                ON CONFLICT (site_code) DO UPDATE SET
                    is_active = EXCLUDED.is_active,
                    groundtruthing_priority = EXCLUDED.groundtruthing_priority,
                    groundtruthing_status = EXCLUDED.groundtruthing_status,
                    waterbody = EXCLUDED.waterbody,
                    subwatershed = EXCLUDED.subwatershed,
                    description = EXCLUDED.description,
                    property_type = EXCLUDED.property_type,
                    permission = EXCLUDED.permission,
                    walk_time = EXCLUDED.walk_time,
                    walk_distance = EXCLUDED.walk_distance,
                    walk_gradient = EXCLUDED.walk_gradient,
                    water_access = EXCLUDED.water_access,
                    additional_comments = EXCLUDED.additional_comments,
                    environmental_hazards = EXCLUDED.environmental_hazards,
                    parking_details = EXCLUDED.parking_details,
                    walking_directions = EXCLUDED.walking_directions,
                    habitat_type = EXCLUDED.habitat_type,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    site_type = EXCLUDED.site_type,
                    cat_priority = EXCLUDED.cat_priority,
                    cat_status = EXCLUDED.cat_status,
                    last_cat_sample_date = EXCLUDED.last_cat_sample_date,
                    bat_priority = EXCLUDED.bat_priority,
                    bat_status = EXCLUDED.bat_status,
                    last_bat_sample_date = EXCLUDED.last_bat_sample_date,
                    bact_priority = EXCLUDED.bact_priority,
                    bact_status = EXCLUDED.bact_status,
                    drainage_area = EXCLUDED.drainage_area;
            """)
            
            conn.execute(upsert_query)
            conn.commit()
            
            logger.info("Sites table updated successfully via Upsert.")
            
            # Drop staging
            conn.execute(text("DROP TABLE sites_staging"))
            conn.commit()

    except Exception as e:
        logger.error(f"Error loading sites data: {e}")
        raise

if __name__ == "__main__":
    load_sites_data()
