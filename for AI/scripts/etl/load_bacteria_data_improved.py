#!/usr/bin/env python3
"""
Load bacteria data from BACT and HAB 2025 Data.xlsx into Neon database
This improved version combines data from multiple sheets to fill in missing values
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_text_field(value):
    """Clean and standardize text fields"""
    if pd.isna(value) or value == '':
        return None
    return str(value).strip()

def parse_e_coli_value(value):
    """Parse E.coli values, handling various formats"""
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    
    val_str = str(value).strip()
    
    # Handle "> 2419.6" format
    if '>' in val_str:
        try:
            num = float(val_str.split('>')[1].strip())
            return num
        except:
            return None
    
    # Handle regular numeric values
    try:
        return float(val_str)
    except:
        return None

def load_bacteria_data_improved():
    """Load bacteria data from multiple sheets in BACT and HAB 2025 Data file"""
    logger.info("Loading bacteria data from multiple sheets...")
    
    try:
        file_path = "data/raw/BACT and HAB 2025 Data.xlsx"
        
        # Load data from IDEXX sheet (E.coli data)
        logger.info("Loading IDEXX sheet...")
        idexx_df = pd.read_excel(file_path, sheet_name='IDEXX')
        logger.info(f"IDEXX sheet has {len(idexx_df)} rows")
        
        # Load data from SURVEY123 sheet (field measurements)
        logger.info("Loading SURVEY123 sheet...")
        survey_df = pd.read_excel(file_path, sheet_name='SURVEY123')
        logger.info(f"SURVEY123 sheet has {len(survey_df)} rows")
        
        # Load data from TURBIDITY sheet
        logger.info("Loading TURBIDITY sheet...")
        turbidity_df = pd.read_excel(file_path, sheet_name='TURBIDITY')
        logger.info(f"TURBIDITY sheet has {len(turbidity_df)} rows")
        
        # Load data from PHYCOCYANIN sheet (pH, DO, conductivity, temperature)
        logger.info("Loading PHYCOCYANIN sheet...")
        phycocyanin_df = pd.read_excel(file_path, sheet_name='PHYCOCYANIN')
        logger.info(f"PHYCOCYANIN sheet has {len(phycocyanin_df)} rows")
        
        # Start with IDEXX data as the base
        df = idexx_df.copy()
        
        # Clean and transform IDEXX data
        # Generate unique IDs using row index to ensure no duplicates
        df['bacteria_record_id'] = df.apply(lambda row: f"BACT_{row.name + 1:06d}", axis=1)
        df['sample_code'] = df.get('Sample Code', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['site_code'] = df.get('Sample ID', pd.Series([''] * len(df))).astype(str).apply(clean_text_field)
        df['collection_date'] = pd.to_datetime(df.get('Date Collected', pd.Series([''] * len(df))), errors='coerce')
        df['collection_time'] = None
        
        # Parse E.coli values
        e_coli_values = df.get('E. coli', pd.Series([''] * len(df)))
        df['e_coli'] = e_coli_values.apply(parse_e_coli_value)
        df['measurement_value'] = e_coli_values.astype(str).apply(clean_text_field)
        
        # Initialize other columns
        df['water_temperature'] = None
        df['turbidity'] = None
        df['ph'] = None
        df['do_ppm'] = None
        df['conductivity'] = None
        df['total_coliforms'] = None
        df['fecal_coliforms'] = None
        df['enterococci'] = None
        
        # Merge with SURVEY123 data for water temperature
        if not survey_df.empty:
            logger.info("Merging SURVEY123 data...")
            survey_clean = survey_df.copy()
            survey_clean['sample_code'] = survey_clean.get('Sample Code', pd.Series([''] * len(survey_clean))).astype(str).apply(clean_text_field)
            survey_clean['water_temp'] = pd.to_numeric(survey_clean.get('Water Temperature', pd.Series([''] * len(survey_clean))), errors='coerce')
            
            # Check for duplicate sample codes in survey data
            survey_duplicates = survey_clean[survey_clean.duplicated(subset=['sample_code'], keep=False)]
            if len(survey_duplicates) > 0:
                logger.warning(f"Found {len(survey_duplicates)} duplicate sample codes in SURVEY123 data")
                # Keep only the first occurrence
                survey_clean = survey_clean.drop_duplicates(subset=['sample_code'], keep='first')
                logger.info(f"Kept {len(survey_clean)} unique survey records")
            
            # Merge on sample_code
            df = df.merge(survey_clean[['sample_code', 'water_temp']], on='sample_code', how='left', suffixes=('', '_survey'))
            df['water_temperature'] = df['water_temperature'].fillna(df['water_temp'])
            df = df.drop(columns=['water_temp'])
            logger.info(f"After SURVEY123 merge: {len(df)} records")
        
        # Merge with TURBIDITY data
        if not turbidity_df.empty:
            logger.info("Merging TURBIDITY data...")
            turbidity_clean = turbidity_df.copy()
            turbidity_clean['sample_code'] = turbidity_clean.get('Sample Code', pd.Series([''] * len(turbidity_clean))).astype(str).apply(clean_text_field)
            turbidity_clean['turbidity_value'] = pd.to_numeric(turbidity_clean.get('Final Reading', pd.Series([''] * len(turbidity_clean))), errors='coerce')
            
            # Check for duplicate sample codes in turbidity data
            turbidity_duplicates = turbidity_clean[turbidity_clean.duplicated(subset=['sample_code'], keep=False)]
            if len(turbidity_duplicates) > 0:
                logger.warning(f"Found {len(turbidity_duplicates)} duplicate sample codes in TURBIDITY data")
                # Keep only the first occurrence
                turbidity_clean = turbidity_clean.drop_duplicates(subset=['sample_code'], keep='first')
                logger.info(f"Kept {len(turbidity_clean)} unique turbidity records")
            
            # Merge on sample_code
            df = df.merge(turbidity_clean[['sample_code', 'turbidity_value']], on='sample_code', how='left', suffixes=('', '_turb'))
            df['turbidity'] = df['turbidity'].fillna(df['turbidity_value'])
            df = df.drop(columns=['turbidity_value'])
            logger.info(f"After TURBIDITY merge: {len(df)} records")
        
        # Merge with PHYCOCYANIN data for pH, DO, conductivity
        if not phycocyanin_df.empty:
            logger.info("Merging PHYCOCYANIN data...")
            phycocyanin_clean = phycocyanin_df.copy()
            phycocyanin_clean['sample_code'] = phycocyanin_clean.get('Sample code', pd.Series([''] * len(phycocyanin_clean))).astype(str).apply(clean_text_field)
            phycocyanin_clean['ph_value'] = pd.to_numeric(phycocyanin_clean.get('pH', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            phycocyanin_clean['do_ppm_value'] = pd.to_numeric(phycocyanin_clean.get('DO (ppm)', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            phycocyanin_clean['conductivity_value'] = pd.to_numeric(phycocyanin_clean.get('Cond (µs/cm)', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            phycocyanin_clean['temp_value'] = pd.to_numeric(phycocyanin_clean.get('Temp (°C)', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            
            # Check for duplicate sample codes in phycocyanin data
            phycocyanin_duplicates = phycocyanin_clean[phycocyanin_clean.duplicated(subset=['sample_code'], keep=False)]
            if len(phycocyanin_duplicates) > 0:
                logger.warning(f"Found {len(phycocyanin_duplicates)} duplicate sample codes in PHYCOCYANIN data")
                # Keep only the first occurrence
                phycocyanin_clean = phycocyanin_clean.drop_duplicates(subset=['sample_code'], keep='first')
                logger.info(f"Kept {len(phycocyanin_clean)} unique phycocyanin records")
            
            # Merge on sample_code
            merge_cols = ['sample_code', 'ph_value', 'do_ppm_value', 'conductivity_value', 'temp_value']
            df = df.merge(phycocyanin_clean[merge_cols], on='sample_code', how='left', suffixes=('', '_phyco'))
            df['ph'] = df['ph'].fillna(df['ph_value'])
            df['do_ppm'] = df['do_ppm'].fillna(df['do_ppm_value'])
            df['conductivity'] = df['conductivity'].fillna(df['conductivity_value'])
            df['water_temperature'] = df['water_temperature'].fillna(df['temp_value'])
            df = df.drop(columns=['ph_value', 'do_ppm_value', 'conductivity_value', 'temp_value'])
            logger.info(f"After PHYCOCYANIN merge: {len(df)} records")
        
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
        
        # Connect to database
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
        
        # Clear existing bacteria data completely
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE bacteria RESTART IDENTITY CASCADE"))
            conn.commit()
            logger.info("Cleared all existing bacteria data")
        
        # Check for duplicate IDs in the dataframe
        duplicate_ids = df[df.duplicated(subset=['bacteria_record_id'], keep=False)]
        if len(duplicate_ids) > 0:
            logger.warning(f"Found {len(duplicate_ids)} duplicate bacteria_record_id values in dataframe:")
            for id_val in duplicate_ids['bacteria_record_id'].unique():
                logger.warning(f"  Duplicate ID: {id_val}")
        
        # Load data one record at a time to avoid batch issues
        total_loaded = 0
        
        for index, row in df.iterrows():
            try:
                row_df = pd.DataFrame([row])
                row_df.to_sql('bacteria', engine, if_exists='append', index=False, method=None)
                total_loaded += 1
                if total_loaded % 50 == 0:
                    logger.info(f"Loaded {total_loaded} records...")
            except Exception as e:
                logger.error(f"Error loading record {index}: {e}")
                logger.error(f"Record ID: {row['bacteria_record_id']}")
                raise
        
        logger.info(f"Successfully loaded {total_loaded} bacteria records")
        
        # Verify the data was loaded and show data quality
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM bacteria")).scalar()
            logger.info(f"Total bacteria records in database: {count}")
            
            # Check data completeness
            logger.info("Data completeness analysis:")
            columns_to_check = ['water_temperature', 'turbidity', 'ph', 'do_ppm', 'conductivity', 'e_coli']
            for col in columns_to_check:
                result = conn.execute(text(f"SELECT COUNT(*) FROM bacteria WHERE {col} IS NOT NULL"))
                non_null_count = result.scalar()
                percentage = (non_null_count / count * 100) if count > 0 else 0
                logger.info(f"  {col}: {non_null_count}/{count} ({percentage:.1f}%)")
            
            # Show sample of loaded data
            result = conn.execute(text("SELECT bacteria_record_id, site_code, collection_date, e_coli, water_temperature, turbidity, ph FROM bacteria ORDER BY collection_date DESC LIMIT 5"))
            logger.info("Sample of loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} on {row[2]} - E.coli: {row[3]}, Temp: {row[4]}, Turbidity: {row[5]}, pH: {row[6]}")
        
    except Exception as e:
        logger.error(f"Error loading bacteria data: {e}")
        raise

if __name__ == "__main__":
    load_bacteria_data_improved()
