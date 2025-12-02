#!/usr/bin/env python3
"""
Load taxonomy data by creating a reference table from bugs data
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
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

def load_taxonomy_data():
    """Load taxonomy data by creating a reference table from bugs data"""
    logger.info("Loading taxonomy data from bugs data...")
    
    try:
        # Read bugs data to create taxonomy reference
        file_path = "data/raw/BATSITES COLLECTED.xlsx"
        df_bugs = pd.read_excel(file_path, sheet_name='BUGSPICKED')
        
        logger.info(f"Bugs file has {len(df_bugs)} rows")
        
        # Get unique combinations of Order and Family
        unique_combinations = df_bugs[['Order', 'Family']].drop_duplicates()
        unique_combinations = unique_combinations.dropna()
        
        logger.info(f"Found {len(unique_combinations)} unique order/family combinations")
        
        # Create taxonomy records
        taxonomy_data = []
        for idx, (_, row) in enumerate(unique_combinations.iterrows()):
            order = str(row['Order']).strip()
            family = str(row['Family']).strip()
            
            # Create unique bug_id
            bug_id = f"TAX_{idx+1:03d}"
            
            # Determine if it's an EPT (Ephemeroptera, Plecoptera, Trichoptera)
            ept = order in ['Ephemeroptera', 'Plecoptera', 'Trichoptera']
            
            # Determine if it's an insect (most orders are insects)
            insect = order in ['Diptera', 'Trichoptera', 'Coleoptera', 'Ephemeroptera', 'Plecoptera', 
                             'Odonata', 'Hemiptera', 'Neuroptera', 'Megaloptera', 'Hymenoptera']
            
            taxonomy_data.append({
                'bug_id': bug_id,
                'family': family[:100] if family else None,  # varchar(100)
                'genus_species': order[:100] if order else None,  # varchar(100)
                'tolerance_value': None,
                'ept': ept,
                'insect': insect,
                'functional_group': None,
                'habitat_preference': None,
                'pollution_tolerance': None,
                'notes': f"Created from bugs data: {order} - {family}"
            })
        
        # Convert to DataFrame
        df_taxonomy = pd.DataFrame(taxonomy_data)
        
        logger.info(f"Created {len(df_taxonomy)} taxonomy records")
        
        # Connect to database
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        # Load data in smaller batches
        batch_size = 50
        total_loaded = 0
        
        for i in range(0, len(df_taxonomy), batch_size):
            batch_df = df_taxonomy.iloc[i:i+batch_size]
            batch_df.to_sql('taxonomy', engine, if_exists='append', index=False, method=None)
            total_loaded += len(batch_df)
            logger.info(f"Loaded batch {i//batch_size + 1}: {len(batch_df)} records (Total: {total_loaded})")
        
        logger.info(f"Successfully loaded {total_loaded} taxonomy records")
        
        # Verify the data was loaded
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM taxonomy")).scalar()
            logger.info(f"Total taxonomy records in database: {count}")
            
            # Show sample of loaded data
            result = conn.execute(text("SELECT bug_id, family, genus_species, ept, insect FROM taxonomy ORDER BY bug_id LIMIT 5"))
            logger.info("Sample of loaded records:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} - {row[2]} (EPT: {row[3]}, Insect: {row[4]})")
        
    except Exception as e:
        logger.error(f"Error loading taxonomy data: {e}")
        raise

if __name__ == "__main__":
    load_taxonomy_data()