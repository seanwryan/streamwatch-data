#!/usr/bin/env python3
"""
Load bug list data from tblSampleDates.xlsx
"""

import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_CONFIG
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_bug_list():
    """Load bug list data from Excel file"""
    try:
        # Create connection string
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        logger.info("Loading bug list data...")
        
        # Read Excel file
        file_path = 'data/raw/tblSampleDates.xlsx'
        df = pd.read_excel(file_path, sheet_name='BugList')
        
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Clean the data
        df = df.dropna(subset=['BugID'])  # Remove rows without BugID
        
        # Convert data types
        df['BugID'] = pd.to_numeric(df['BugID'], errors='coerce').astype('Int64')
        df['GenusID'] = pd.to_numeric(df['GenusID'], errors='coerce').astype('Int64')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').astype('Int64')
        df['FTV'] = pd.to_numeric(df['FTV'], errors='coerce')
        df['TolVal'] = pd.to_numeric(df['TolVal'], errors='coerce')
        df['NYTolVal'] = pd.to_numeric(df['NYTolVal'], errors='coerce')
        
        # Handle boolean columns
        boolean_columns = ['Adult', 'EPT', 'Tanytarsini', 'Orthocladiinae', 'Tanypodinae', 'Insect', 'Exclude', 'Hide?']
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        # Handle date column
        df['BugUpdated'] = pd.to_datetime(df['BugUpdated'], errors='coerce')
        
        # Truncate string fields to match database schema
        string_columns = {
            'OrderClass': 50, 'Family': 100, 'GenusSpecies': 100, 'Genus': 100,
            'FFG': 50, 'FFGRef': 100, 'TolValRef': 100, 'Synonyms': None,  # TEXT field
            'Habit': 100, 'TaluAttribute': 50, 'CommonName': 100, 'TSN': 50
        }
        
        for col, max_len in string_columns.items():
            if col in df.columns:
                if max_len:
                    df[col] = df[col].astype(str).str[:max_len]
                else:
                    df[col] = df[col].astype(str)
        
        # Rename columns to match database schema (lowercase)
        df = df.rename(columns={
            'BugID': 'bug_id',
            'OrderClass': 'order_class',
            'Family': 'family',
            'GenusSpecies': 'genus_species',
            'Genus': 'genus',
            'GenusID': 'genus_id',
            'Adult': 'adult',
            'EPT': 'ept',
            'Tanytarsini': 'tanytarsini',
            'Orthocladiinae': 'orthocladiinae',
            'Tanypodinae': 'tanypodinae',
            'Insect': 'insect',
            'Exclude': 'exclude',
            'FTV': 'ftv',
            'FTVRef': 'ftv_ref',
            'FFG': 'ffg',
            'FFGRef': 'ffg_ref',
            'TolVal': 'tol_val',
            'TolValRef': 'tol_val_ref',
            'NYTolVal': 'ny_tol_val',
            'Synonyms': 'synonyms',
            'Habit': 'habit',
            'TaluAttribute': 'talu_attribute',
            'CommonName': 'common_name',
            'TSN': 'tsn',
            'Hide?': 'hide',
            'Amount': 'amount',
            'BugUpdated': 'bug_updated'
        })
        
        # Clear existing data
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM bug_list"))
            conn.commit()
        
        # Load data in batches
        batch_size = 1000
        total_rows = len(df)
        
        for i in range(0, total_rows, batch_size):
            batch_df = df.iloc[i:i+batch_size]
            batch_df.to_sql('bug_list', engine, if_exists='append', index=False, method='multi')
            logger.info(f"Loaded batch {i//batch_size + 1}/{(total_rows-1)//batch_size + 1}")
        
        logger.info(f"Successfully loaded {total_rows} bug list records")
        return True
        
    except Exception as e:
        logger.error(f"Error loading bug list data: {e}")
        return False

if __name__ == "__main__":
    load_bug_list()
