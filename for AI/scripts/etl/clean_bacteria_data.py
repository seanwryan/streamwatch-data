#!/usr/bin/env python3
"""
Clean and reformat bacteria data from the messy Excel structure
This script handles the complex, multi-section organization of the bacteria data
"""

import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_bacteria_data():
    """Clean and reformat the bacteria data from the messy Excel structure"""
    logger.info("Starting bacteria data cleaning...")
    
    file_path = "data/raw/BACT and HAB 2025 Data.xlsx"
    
    # Read the IDEXX sheet with proper header handling
    logger.info("Reading IDEXX sheet...")
    idexx_raw = pd.read_excel(file_path, sheet_name='IDEXX', header=0)
    
    logger.info(f"Raw IDEXX data: {len(idexx_raw)} rows, {len(idexx_raw.columns)} columns")
    logger.info(f"Columns: {list(idexx_raw.columns)}")
    
    # Clean the data by removing quality notes and non-data rows
    logger.info("Cleaning data - removing quality notes and non-data rows...")
    
    # Create a clean dataframe
    clean_data = []
    
    for idx, row in idexx_raw.iterrows():
        # Skip rows that are clearly not data
        sample_code = str(row.get('Sample Code', '')).strip()
        
        # Skip if sample code is empty, NaN, or contains quality note keywords
        if (pd.isna(sample_code) or 
            sample_code == '' or 
            sample_code == 'nan' or
            any(keyword in sample_code.lower() for keyword in [
                'bacteria', 'data', 'conditions', 'exceeded', 'holding', 
                'time', 'temperature', 'positive', 'blank', 'missing',
                'wrong', 'date', 'read', 'outside', 'window', 'empty',
                'well', 'relative', 'difference', 'original', 'dilution',
                'other', 'describe'
            ])):
            continue
            
        # Skip if sample code doesn't look like a proper sample code (should contain underscore and date)
        if '_' not in sample_code or '2025' not in sample_code:
            continue
            
        # Extract clean data
        clean_row = {
            'sample_code': sample_code,
            'site_code': str(row.get('Sample ID', '')).strip(),
            'collection_date': row.get('Date Collected'),
            'e_coli': row.get('E. coli'),
            'total_coliforms': row.get('Ttl Coli'),
            'large_wells': row.get('Color Change'),  # This seems to be large wells count
            'small_wells': row.get('Unnamed: 4'),    # This seems to be small wells count
            'fluorescence_large': row.get('Flourescence'),
            'fluorescence_small': row.get('Unnamed: 7'),
            'data_conditions': str(row.get('Data Conditions', '')).strip()
        }
        
        # Only add if we have essential data
        if clean_row['sample_code'] and clean_row['site_code'] and pd.notna(clean_row['collection_date']):
            clean_data.append(clean_row)
    
    # Convert to DataFrame
    df_clean = pd.DataFrame(clean_data)
    
    logger.info(f"Cleaned data: {len(df_clean)} rows")
    
    # Data type conversions
    logger.info("Converting data types...")
    df_clean['collection_date'] = pd.to_datetime(df_clean['collection_date'], errors='coerce')
    
    # Clean E.coli values
    def parse_e_coli(value):
        if pd.isna(value) or value == '' or value == 'nan':
            return None
        val_str = str(value).strip()
        if '>' in val_str:
            try:
                return float(val_str.split('>')[1].strip())
            except:
                return None
        try:
            return float(val_str)
        except:
            return None
    
    df_clean['e_coli'] = df_clean['e_coli'].apply(parse_e_coli)
    df_clean['total_coliforms'] = pd.to_numeric(df_clean['total_coliforms'], errors='coerce')
    df_clean['large_wells'] = pd.to_numeric(df_clean['large_wells'], errors='coerce')
    df_clean['small_wells'] = pd.to_numeric(df_clean['small_wells'], errors='coerce')
    df_clean['fluorescence_large'] = pd.to_numeric(df_clean['fluorescence_large'], errors='coerce')
    df_clean['fluorescence_small'] = pd.to_numeric(df_clean['fluorescence_small'], errors='coerce')
    
    # Remove rows with invalid dates
    df_clean = df_clean.dropna(subset=['collection_date'])
    
    logger.info(f"After date cleaning: {len(df_clean)} rows")
    
    # Sort by date and sample code
    df_clean = df_clean.sort_values(['collection_date', 'sample_code'])
    
    # Show sample of cleaned data
    logger.info("Sample of cleaned data:")
    print(df_clean.head(10).to_string())
    
    # Show data quality summary
    logger.info("\\nData quality summary:")
    logger.info(f"Total samples: {len(df_clean)}")
    logger.info(f"Date range: {df_clean['collection_date'].min()} to {df_clean['collection_date'].max()}")
    logger.info(f"Unique sites: {df_clean['site_code'].nunique()}")
    logger.info(f"E.coli measurements: {df_clean['e_coli'].notna().sum()}/{len(df_clean)} ({df_clean['e_coli'].notna().sum()/len(df_clean)*100:.1f}%)")
    logger.info(f"Total coliforms measurements: {df_clean['total_coliforms'].notna().sum()}/{len(df_clean)} ({df_clean['total_coliforms'].notna().sum()/len(df_clean)*100:.1f}%)")
    
    # Check for duplicates
    duplicates = df_clean[df_clean.duplicated(subset=['sample_code'], keep=False)]
    if len(duplicates) > 0:
        logger.warning(f"Found {len(duplicates)} duplicate sample codes:")
        for sample_code in duplicates['sample_code'].unique():
            logger.warning(f"  {sample_code}: {len(duplicates[duplicates['sample_code'] == sample_code])} occurrences")
    else:
        logger.info("No duplicate sample codes found")
    
    # Save cleaned data
    output_file = "data/processed/cleaned_bacteria_data.csv"
    df_clean.to_csv(output_file, index=False)
    logger.info(f"Cleaned data saved to: {output_file}")
    
    return df_clean

if __name__ == "__main__":
    clean_bacteria_data()



