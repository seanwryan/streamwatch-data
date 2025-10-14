#!/usr/bin/env python3
"""
Load RBP100 bugs data from tblSampleDates.xlsx
"""

import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_rbp100_bugs():
    """Load RBP100 bugs data from Excel file"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Loading RBP100 bugs data...")
        
        # Read Excel file
        file_path = 'data/raw/tblSampleDates.xlsx'
        df = pd.read_excel(file_path, sheet_name='tblRBP100Bugs')
        
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Clean the data
        df = df.dropna(subset=['RBP_ID'])  # Remove rows without RBP_ID
        
        # Convert data types
        df['RBP_ID'] = pd.to_numeric(df['RBP_ID'], errors='coerce').astype('Int64')
        df['SampleID'] = pd.to_numeric(df['SampleID'], errors='coerce').astype('Int64')
        df['BugID'] = pd.to_numeric(df['BugID'], errors='coerce').astype('Int64')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').astype('Int64')
        
        # Truncate string fields to match database schema
        df['SampleCode'] = df['SampleCode'].astype(str).str[:50]
        df['Family'] = df['Family'].astype(str).str[:100]
        df['GenusSpecies'] = df['GenusSpecies'].astype(str).str[:100]
        
        # Rename columns to match database schema (lowercase)
        df = df.rename(columns={
            'RBP_ID': 'rbp_id',
            'SampleID': 'sample_id',
            'SampleCode': 'sample_code',
            'BugID': 'bug_id',
            'Family': 'family',
            'GenusSpecies': 'genus_species',
            'Amount': 'amount'
        })
        
        # Clear existing data
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM rbp100_bugs"))
            conn.commit()
        
        # Load data in batches
        batch_size = 1000
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('rbp100_bugs', engine, if_exists='append', index=False, method='multi')
            logger.info(f"Loaded batch {i//batch_size + 1}/{(total_rows-1)//batch_size + 1}")
        
        logger.info(f"Successfully loaded {total_rows} RBP100 bugs records")
        return True
        
    except Exception as e:
        logger.error(f"Error loading RBP100 bugs data: {e}")
        return False

if __name__ == "__main__":
    load_rbp100_bugs()
