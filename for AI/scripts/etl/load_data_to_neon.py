#!/usr/bin/env python3
"""
Load StreamWatch data from Excel files into Neon PostgreSQL database
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import os
from pathlib import Path

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

def load_sites_data():
    """Load sites data from StreamWatch Locations file"""
    logger.info("Loading sites data...")
    
    try:
        # Read sites data
        file_path = "data/raw/2025 StreamWatch Locations.xlsx"
        df = pd.read_excel(file_path)
        
        # Clean and transform data to match database schema
        df['site_code'] = df.get('SiteCode', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['is_active'] = df.get('isActive', pd.Series([True] * len(df))).apply(convert_to_boolean)
        df['groundtruthing_priority'] = df.get('Groundtruthing Priority', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['groundtruthing_status'] = df.get('Groundtruthing Status', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['waterbody'] = df.get('WaterBody', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['subwatershed'] = df.get('Subwatershed', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['description'] = df.get('Description', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['property_type'] = df.get('Type of Property', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['permission'] = df.get('Permission', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['walk_time'] = df.get('Walk Time', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['walk_distance'] = df.get('Walk Distance', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['walk_gradient'] = df.get('Walk Gradient', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['water_access'] = df.get('Water Access', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['additional_comments'] = df.get('Additional Comments', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['environmental_hazards'] = df.get('Environmental Hazards', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['parking_details'] = df.get('Parking Details', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['walking_directions'] = df.get('Walking Directions', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['habitat_type'] = df.get('HabitatType', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['latitude'] = pd.to_numeric(df.get('Latitude', pd.Series([''] * len(df))), errors='coerce')
        df['longitude'] = pd.to_numeric(df.get('Longitude', pd.Series([''] * len(df))), errors='coerce')
        df['site_type'] = df.get('Type', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['cat_priority'] = df.get('CAT_Priority', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['cat_status'] = df.get('CAT_Status', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['last_cat_sample_date'] = pd.to_datetime(df.get('Last_CAT_Sample_Date', pd.Series([''] * len(df))), errors='coerce')
        df['bat_priority'] = df.get('BAT_Priority', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['bat_status'] = df.get('BAT_Status', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['last_bat_sample_date'] = pd.to_datetime(df.get('Last_BAT_Sa,mple_Date', pd.Series([''] * len(df))), errors='coerce')
        df['bact_priority'] = df.get('BACT_Priority', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['bact_status'] = df.get('BACT_Status', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['drainage_area'] = pd.to_numeric(df.get('DrainageArea', pd.Series([''] * len(df))), errors='coerce')
        
        # Select columns to keep (matching database schema)
        columns_to_keep = [
            'site_code', 'is_active', 'groundtruthing_priority', 'groundtruthing_status',
            'waterbody', 'subwatershed', 'description', 'property_type', 'permission',
            'walk_time', 'walk_distance', 'walk_gradient', 'water_access',
            'additional_comments', 'environmental_hazards', 'parking_details',
            'walking_directions', 'habitat_type', 'latitude', 'longitude',
            'site_type', 'cat_priority', 'cat_status', 'last_cat_sample_date',
            'bat_priority', 'bat_status', 'last_bat_sample_date',
            'bact_priority', 'bact_status', 'drainage_area'
        ]
        df = df[columns_to_keep]
        
        # Remove rows with missing site_code
        df = df.dropna(subset=['site_code'])
        df = df[df['site_code'] != '']
        
        # Connect to database and load data
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        df.to_sql('sites', engine, if_exists='append', index=False, method='multi')
        logger.info(f"Successfully loaded {len(df)} site records")
        
    except Exception as e:
        logger.error(f"Error loading sites data: {e}")
        raise

def load_samples_data():
    """Load samples data from main StreamWatch data file"""
    logger.info("Loading samples data...")
    
    try:
        # Read samples data
        file_path = "data/raw/All StreamWatch Data.xlsx"
        df = pd.read_excel(file_path, sheet_name='Samples')
        
        # Clean and transform data
        df['sample_id'] = df.get('Sample ID', df.get('SampleID', pd.Series([''] * len(df)))).astype(str).apply(clean_text_field)
        df['site_code'] = df.get('Site Code', df.get('SiteCode', pd.Series([''] * len(df)))).astype(str).apply(clean_text_field)
        df['sample_date'] = pd.to_datetime(df.get('Date', df.get('SampleDate', pd.Series([''] * len(df)))), errors='coerce')
        df['sample_time'] = pd.to_datetime(df.get('Time', df.get('SampleTime', pd.Series([''] * len(df)))), errors='coerce').dt.time
        df['water_temperature'] = pd.to_numeric(df.get('Water Temperature', df.get('Temp', pd.Series([''] * len(df)))), errors='coerce')
        df['ph'] = pd.to_numeric(df.get('pH', df.get('PH', pd.Series([''] * len(df)))), errors='coerce')
        df['do_ppm'] = pd.to_numeric(df.get('DO (ppm)', df.get('DO', pd.Series([''] * len(df)))), errors='coerce')
        df['do_percent'] = pd.to_numeric(df.get('DO (%)', df.get('DO_Percent', pd.Series([''] * len(df)))), errors='coerce')
        df['nitrate'] = pd.to_numeric(df.get('Nitrate', df.get('NO3', pd.Series([''] * len(df)))), errors='coerce')
        df['phosphates'] = pd.to_numeric(df.get('Phosphates', df.get('PO4', pd.Series([''] * len(df)))), errors='coerce')
        df['turbidity'] = pd.to_numeric(df.get('Turbidity', df.get('Turb', pd.Series([''] * len(df)))), errors='coerce')
        df['conductivity'] = pd.to_numeric(df.get('Conductivity', df.get('Cond', pd.Series([''] * len(df)))), errors='coerce')
        df['total_solids'] = pd.to_numeric(df.get('Total Solids', df.get('TS', pd.Series([''] * len(df)))), errors='coerce')
        df['total_suspended_solids'] = pd.to_numeric(df.get('Total Suspended Solids', df.get('TSS', pd.Series([''] * len(df)))), errors='coerce')
        df['total_dissolved_solids'] = pd.to_numeric(df.get('Total Dissolved Solids', df.get('TDS', pd.Series([''] * len(df)))), errors='coerce')
        df['alkalinity'] = pd.to_numeric(df.get('Alkalinity', df.get('Alk', pd.Series([''] * len(df)))), errors='coerce')
        df['hardness'] = pd.to_numeric(df.get('Hardness', df.get('Hard', pd.Series([''] * len(df)))), errors='coerce')
        df['chloride'] = pd.to_numeric(df.get('Chloride', df.get('Cl', pd.Series([''] * len(df)))), errors='coerce')
        df['sulfate'] = pd.to_numeric(df.get('Sulfate', df.get('SO4', pd.Series([''] * len(df)))), errors='coerce')
        df['calcium'] = pd.to_numeric(df.get('Calcium', df.get('Ca', pd.Series([''] * len(df)))), errors='coerce')
        df['magnesium'] = pd.to_numeric(df.get('Magnesium', df.get('Mg', pd.Series([''] * len(df)))), errors='coerce')
        df['sodium'] = pd.to_numeric(df.get('Sodium', df.get('Na', pd.Series([''] * len(df)))), errors='coerce')
        df['potassium'] = pd.to_numeric(df.get('Potassium', df.get('K', pd.Series([''] * len(df)))), errors='coerce')
        df['iron'] = pd.to_numeric(df.get('Iron', df.get('Fe', pd.Series([''] * len(df)))), errors='coerce')
        df['manganese'] = pd.to_numeric(df.get('Manganese', df.get('Mn', pd.Series([''] * len(df)))), errors='coerce')
        df['copper'] = pd.to_numeric(df.get('Copper', df.get('Cu', pd.Series([''] * len(df)))), errors='coerce')
        df['zinc'] = pd.to_numeric(df.get('Zinc', df.get('Zn', pd.Series([''] * len(df)))), errors='coerce')
        df['lead'] = pd.to_numeric(df.get('Lead', df.get('Pb', pd.Series([''] * len(df)))), errors='coerce')
        df['cadmium'] = pd.to_numeric(df.get('Cadmium', df.get('Cd', pd.Series([''] * len(df)))), errors='coerce')
        df['chromium'] = pd.to_numeric(df.get('Chromium', df.get('Cr', pd.Series([''] * len(df)))), errors='coerce')
        df['nickel'] = pd.to_numeric(df.get('Nickel', df.get('Ni', pd.Series([''] * len(df)))), errors='coerce')
        df['mercury'] = pd.to_numeric(df.get('Mercury', df.get('Hg', pd.Series([''] * len(df)))), errors='coerce')
        df['arsenic'] = pd.to_numeric(df.get('Arsenic', df.get('As', pd.Series([''] * len(df)))), errors='coerce')
        df['selenium'] = pd.to_numeric(df.get('Selenium', df.get('Se', pd.Series([''] * len(df)))), errors='coerce')
        df['aluminum'] = pd.to_numeric(df.get('Aluminum', df.get('Al', pd.Series([''] * len(df)))), errors='coerce')
        df['boron'] = pd.to_numeric(df.get('Boron', df.get('B', pd.Series([''] * len(df)))), errors='coerce')
        df['fluoride'] = pd.to_numeric(df.get('Fluoride', df.get('F', pd.Series([''] * len(df)))), errors='coerce')
        df['silica'] = pd.to_numeric(df.get('Silica', df.get('SiO2', pd.Series([''] * len(df)))), errors='coerce')
        df['total_nitrogen'] = pd.to_numeric(df.get('Total Nitrogen', df.get('TN', pd.Series([''] * len(df)))), errors='coerce')
        df['total_phosphorus'] = pd.to_numeric(df.get('Total Phosphorus', df.get('TP', pd.Series([''] * len(df)))), errors='coerce')
        df['ammonia'] = pd.to_numeric(df.get('Ammonia', df.get('NH3', pd.Series([''] * len(df)))), errors='coerce')
        df['nitrite'] = pd.to_numeric(df.get('Nitrite', df.get('NO2', pd.Series([''] * len(df)))), errors='coerce')
        df['organic_nitrogen'] = pd.to_numeric(df.get('Organic Nitrogen', df.get('ON', pd.Series([''] * len(df)))), errors='coerce')
        df['organic_phosphorus'] = pd.to_numeric(df.get('Organic Phosphorus', df.get('OP', pd.Series([''] * len(df)))), errors='coerce')
        df['inorganic_phosphorus'] = pd.to_numeric(df.get('Inorganic Phosphorus', df.get('IP', pd.Series([''] * len(df)))), errors='coerce')
        df['total_carbon'] = pd.to_numeric(df.get('Total Carbon', df.get('TC', pd.Series([''] * len(df)))), errors='coerce')
        df['organic_carbon'] = pd.to_numeric(df.get('Organic Carbon', df.get('OC', pd.Series([''] * len(df)))), errors='coerce')
        df['inorganic_carbon'] = pd.to_numeric(df.get('Inorganic Carbon', df.get('IC', pd.Series([''] * len(df)))), errors='coerce')
        df['total_organic_carbon'] = pd.to_numeric(df.get('Total Organic Carbon', df.get('TOC', pd.Series([''] * len(df)))), errors='coerce')
        df['dissolved_organic_carbon'] = pd.to_numeric(df.get('Dissolved Organic Carbon', df.get('DOC', pd.Series([''] * len(df)))), errors='coerce')
        df['particulate_organic_carbon'] = pd.to_numeric(df.get('Particulate Organic Carbon', df.get('POC', pd.Series([''] * len(df)))), errors='coerce')
        df['biochemical_oxygen_demand'] = pd.to_numeric(df.get('Biochemical Oxygen Demand', df.get('BOD', pd.Series([''] * len(df)))), errors='coerce')
        df['chemical_oxygen_demand'] = pd.to_numeric(df.get('Chemical Oxygen Demand', df.get('COD', pd.Series([''] * len(df)))), errors='coerce')
        df['total_coliforms'] = pd.to_numeric(df.get('Total Coliforms', df.get('TC', pd.Series([''] * len(df)))), errors='coerce')
        df['fecal_coliforms'] = pd.to_numeric(df.get('Fecal Coliforms', df.get('FC', pd.Series([''] * len(df)))), errors='coerce')
        df['e_coli'] = pd.to_numeric(df.get('E. coli', df.get('Ecoli', pd.Series([''] * len(df)))), errors='coerce')
        df['enterococci'] = pd.to_numeric(df.get('Enterococci', df.get('Ent', pd.Series([''] * len(df)))), errors='coerce')
        df['heterotrophic_plate_count'] = pd.to_numeric(df.get('Heterotrophic Plate Count', df.get('HPC', pd.Series([''] * len(df)))), errors='coerce')
        df['total_heterotrophic_bacteria'] = pd.to_numeric(df.get('Total Heterotrophic Bacteria', df.get('THB', pd.Series([''] * len(df)))), errors='coerce')
        df['total_plate_count'] = pd.to_numeric(df.get('Total Plate Count', df.get('TPC', pd.Series([''] * len(df)))), errors='coerce')
        df['total_bacteria'] = pd.to_numeric(df.get('Total Bacteria', df.get('TB', pd.Series([''] * len(df)))), errors='coerce')
        
        # Select columns to keep
        columns_to_keep = [
            'sample_id', 'site_code', 'sample_date', 'sample_time', 'water_temperature',
            'ph', 'do_ppm', 'do_percent', 'nitrate', 'phosphates', 'turbidity',
            'conductivity', 'total_solids', 'total_suspended_solids', 'total_dissolved_solids',
            'alkalinity', 'hardness', 'chloride', 'sulfate', 'calcium', 'magnesium',
            'sodium', 'potassium', 'iron', 'manganese', 'copper', 'zinc', 'lead',
            'cadmium', 'chromium', 'nickel', 'mercury', 'arsenic', 'selenium',
            'aluminum', 'boron', 'fluoride', 'silica', 'total_nitrogen', 'total_phosphorus',
            'ammonia', 'nitrite', 'organic_nitrogen', 'organic_phosphorus', 'inorganic_phosphorus',
            'total_carbon', 'organic_carbon', 'inorganic_carbon', 'total_organic_carbon',
            'dissolved_organic_carbon', 'particulate_organic_carbon', 'biochemical_oxygen_demand',
            'chemical_oxygen_demand', 'total_coliforms', 'fecal_coliforms', 'e_coli',
            'enterococci', 'heterotrophic_plate_count', 'total_heterotrophic_bacteria',
            'total_plate_count', 'total_bacteria'
        ]
        df = df[columns_to_keep]
        
        # Remove rows with missing sample_id
        df = df.dropna(subset=['sample_id'])
        df = df[df['sample_id'] != '']
        
        # Connect to database and load data
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        df.to_sql('samples', engine, if_exists='append', index=False, method='multi')
        logger.info(f"Successfully loaded {len(df)} sample records")
        
    except Exception as e:
        logger.error(f"Error loading samples data: {e}")
        raise

def load_bacteria_data():
    """Load bacteria data from BACT and HAB file"""
    logger.info("Loading bacteria data...")
    
    try:
        # Read bacteria data
        file_path = "data/raw/BACT and HAB 2025 Data.xlsx"
        df = pd.read_excel(file_path)
        
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
        
        # Remove rows with missing site_code
        df = df.dropna(subset=['site_code'])
        df = df[df['site_code'] != '']
        
        # Connect to database and load data
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        df.to_sql('bacteria', engine, if_exists='append', index=False, method='multi')
        logger.info(f"Successfully loaded {len(df)} bacteria records")
        
    except Exception as e:
        logger.error(f"Error loading bacteria data: {e}")
        raise

def load_volunteer_data():
    """Load volunteer data from Volunteer Tracking file"""
    logger.info("Loading volunteer data...")
    
    try:
        # Read volunteer data
        file_path = "data/raw/Volunteer_Tracking.xlsm"
        df = pd.read_excel(file_path, sheet_name='Volunteers', header=2)
        
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
        
        # Remove rows with missing volunteer_id
        df = df.dropna(subset=['volunteer_id'])
        df = df[df['volunteer_id'] != '']
        
        # Connect to database and load data
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        df.to_sql('volunteers', engine, if_exists='append', index=False, method='multi')
        logger.info(f"Successfully loaded {len(df)} volunteer records")
        
    except Exception as e:
        logger.error(f"Error loading volunteer data: {e}")
        raise

def main():
    """Main function to load all data into Neon database"""
    logger.info("Starting to load StreamWatch data into Neon database...")
    
    try:
        # Load data in order (sites first, then samples, then others)
        load_sites_data()
        load_samples_data()
        load_bacteria_data()
        load_volunteer_data()
        
        logger.info("Successfully loaded all data into Neon database!")
        
        # Test connection to verify data was loaded
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check record counts
            sites_count = conn.execute(text("SELECT COUNT(*) FROM sites")).scalar()
            samples_count = conn.execute(text("SELECT COUNT(*) FROM samples")).scalar()
            bacteria_count = conn.execute(text("SELECT COUNT(*) FROM bacteria")).scalar()
            volunteers_count = conn.execute(text("SELECT COUNT(*) FROM volunteers")).scalar()
            
            logger.info(f"Data loaded successfully:")
            logger.info(f"  Sites: {sites_count} records")
            logger.info(f"  Samples: {samples_count} records")
            logger.info(f"  Bacteria: {bacteria_count} records")
            logger.info(f"  Volunteers: {volunteers_count} records")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise

if __name__ == "__main__":
    main()
