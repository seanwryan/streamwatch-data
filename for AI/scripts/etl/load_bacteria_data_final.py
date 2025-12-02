#!/usr/bin/env python3
"""
Load cleaned bacteria data into Neon database
This version uses the cleaned data structure for better data quality
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_bacteria_data_final():
    """Load cleaned bacteria data into the database"""
    logger.info("Loading cleaned bacteria data...")
    
    try:
        # Read the cleaned bacteria data
        file_path = "data/processed/cleaned_bacteria_data.csv"
        df = pd.read_csv(file_path)
        
        logger.info(f"Loaded {len(df)} cleaned bacteria records")
        
        # Create unique bacteria record IDs
        df['bacteria_record_id'] = df.apply(lambda row: f"BACT_{row.name + 1:06d}", axis=1)
        
        # Map to database schema
        df['sample_code'] = df['sample_code'].astype(str)
        df['site_code'] = df['site_code'].astype(str)
        df['collection_date'] = pd.to_datetime(df['collection_date'])
        df['collection_time'] = None  # Not available in this data
        
        # Map E.coli and other measurements
        df['e_coli'] = df['e_coli']
        df['total_coliforms'] = df['total_coliforms']
        df['fecal_coliforms'] = None  # Not available in this data
        df['enterococci'] = None  # Not available in this data
        
        # Store measurement value as text for reference
        df['measurement_value'] = df['e_coli'].astype(str)
        
        # Initialize other fields (will be filled from other sheets)
        df['water_temperature'] = None
        df['turbidity'] = None
        df['ph'] = None
        df['do_ppm'] = None
        df['conductivity'] = None
        
        # Now merge with data from other sheets for additional measurements
        logger.info("Merging with additional measurement data...")
        
        # Load and merge SURVEY123 data for water temperature
        try:
            survey_df = pd.read_excel("data/raw/BACT and HAB 2025 Data.xlsx", sheet_name='SURVEY123')
            survey_clean = survey_df.copy()
            survey_clean['sample_code'] = survey_clean.get('Sample Code', pd.Series([''] * len(survey_clean))).astype(str)
            survey_clean['water_temp'] = pd.to_numeric(survey_clean.get('Water Temperature', pd.Series([''] * len(survey_clean))), errors='coerce')
            
            # Remove duplicates
            survey_clean = survey_clean.drop_duplicates(subset=['sample_code'], keep='first')
            
            # Merge
            df = df.merge(survey_clean[['sample_code', 'water_temp']], on='sample_code', how='left', suffixes=('', '_survey'))
            df['water_temperature'] = df['water_temperature'].fillna(df['water_temp'])
            df = df.drop(columns=['water_temp'])
            logger.info(f"Added water temperature data for {df['water_temperature'].notna().sum()} samples")
        except Exception as e:
            logger.warning(f"Could not load SURVEY123 data: {e}")
        
        # Load and merge TURBIDITY data
        try:
            turbidity_df = pd.read_excel("data/raw/BACT and HAB 2025 Data.xlsx", sheet_name='TURBIDITY')
            turbidity_clean = turbidity_df.copy()
            turbidity_clean['sample_code'] = turbidity_clean.get('Sample Code', pd.Series([''] * len(turbidity_clean))).astype(str)
            turbidity_clean['turbidity_value'] = pd.to_numeric(turbidity_clean.get('Final Reading', pd.Series([''] * len(turbidity_clean))), errors='coerce')
            
            # Remove duplicates
            turbidity_clean = turbidity_clean.drop_duplicates(subset=['sample_code'], keep='first')
            
            # Merge
            df = df.merge(turbidity_clean[['sample_code', 'turbidity_value']], on='sample_code', how='left', suffixes=('', '_turb'))
            df['turbidity'] = df['turbidity'].fillna(df['turbidity_value'])
            df = df.drop(columns=['turbidity_value'])
            logger.info(f"Added turbidity data for {df['turbidity'].notna().sum()} samples")
        except Exception as e:
            logger.warning(f"Could not load TURBIDITY data: {e}")
        
        # Load and merge PHYCOCYANIN data for pH, DO, conductivity
        try:
            phycocyanin_df = pd.read_excel("data/raw/BACT and HAB 2025 Data.xlsx", sheet_name='PHYCOCYANIN')
            phycocyanin_clean = phycocyanin_df.copy()
            phycocyanin_clean['sample_code'] = phycocyanin_clean.get('Sample code', pd.Series([''] * len(phycocyanin_clean))).astype(str)
            phycocyanin_clean['ph_value'] = pd.to_numeric(phycocyanin_clean.get('pH', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            phycocyanin_clean['do_ppm_value'] = pd.to_numeric(phycocyanin_clean.get('DO (ppm)', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            phycocyanin_clean['conductivity_value'] = pd.to_numeric(phycocyanin_clean.get('Cond (µs/cm)', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            phycocyanin_clean['temp_value'] = pd.to_numeric(phycocyanin_clean.get('Temp (°C)', pd.Series([''] * len(phycocyanin_clean))), errors='coerce')
            
            # Remove duplicates
            phycocyanin_clean = phycocyanin_clean.drop_duplicates(subset=['sample_code'], keep='first')
            
            # Merge
            merge_cols = ['sample_code', 'ph_value', 'do_ppm_value', 'conductivity_value', 'temp_value']
            df = df.merge(phycocyanin_clean[merge_cols], on='sample_code', how='left', suffixes=('', '_phyco'))
            df['ph'] = df['ph'].fillna(df['ph_value'])
            df['do_ppm'] = df['do_ppm'].fillna(df['do_ppm_value'])
            df['conductivity'] = df['conductivity'].fillna(df['conductivity_value'])
            df['water_temperature'] = df['water_temperature'].fillna(df['temp_value'])
            df = df.drop(columns=['ph_value', 'do_ppm_value', 'conductivity_value', 'temp_value'])
            logger.info(f"Added pH/DO/conductivity data for {df['ph'].notna().sum()} samples")
        except Exception as e:
            logger.warning(f"Could not load PHYCOCYANIN data: {e}")
        
        # Select columns to keep (matching database schema)
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
        
        # Clear existing bacteria data
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE bacteria RESTART IDENTITY CASCADE"))
            conn.commit()
            logger.info("Cleared all existing bacteria data")
        
        # Load data in batches
        batch_size = 100
        total_loaded = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('bacteria', engine, if_exists='append', index=False, method=None)
            total_loaded += len(batch_df)
            logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_df)} records (Total: {total_loaded})")
        
        logger.info(f"Successfully loaded {total_loaded} bacteria records")
        
        # Verify the data was loaded and show data quality
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM bacteria")).scalar()
            logger.info(f"Total bacteria records in database: {count}")
            
            # Check data completeness
            logger.info("Final data completeness analysis:")
            columns_to_check = ['water_temperature', 'turbidity', 'ph', 'do_ppm', 'conductivity', 'e_coli', 'total_coliforms']
            for col in columns_to_check:
                result = conn.execute(text(f"SELECT COUNT(*) FROM bacteria WHERE {col} IS NOT NULL"))
                non_null_count = result.scalar()
                percentage = (non_null_count / count * 100) if count > 0 else 0
                logger.info(f"  {col}: {non_null_count}/{count} ({percentage:.1f}%)")
            
            # Show sample of loaded data
            result = conn.execute(text("SELECT bacteria_record_id, site_code, collection_date, e_coli, water_temperature, turbidity, ph, total_coliforms FROM bacteria ORDER BY collection_date DESC LIMIT 5"))
            logger.info("Sample of loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} on {row[2]} - E.coli: {row[3]}, Temp: {row[4]}, Turbidity: {row[5]}, pH: {row[6]}, Total Coliforms: {row[7]}")
        
    except Exception as e:
        logger.error(f"Error loading bacteria data: {e}")
        raise

if __name__ == "__main__":
    load_bacteria_data_final()



