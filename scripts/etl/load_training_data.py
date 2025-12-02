#!/usr/bin/env python3
"""
Load training data from Volunteer_Tracking.xlsm TrainingLog sheet into training table
"""

import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import DB_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_training_data():
    """Load training records from TrainingLog sheet"""
    logger.info("Loading training data from Volunteer_Tracking.xlsm...")
    
    try:
        # Read training data - headers are in row 3 (0-indexed)
        file_path = "data/raw/Volunteer_Tracking.xlsm"
        df = pd.read_excel(file_path, sheet_name='TrainingLog', header=3)
        
        logger.info(f"Read {len(df)} rows from TrainingLog sheet")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Map Excel columns to database columns
        # Expected: AttendanceID, TrainingID, VolunteerID, TrainingType, FullName, Status, ExpirationDate
        training_records = []
        
        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get('VolunteerID')) or row.get('VolunteerID') == '':
                continue
            
            # Get volunteer_id - may need to convert to string
            volunteer_id = str(int(row['VolunteerID'])) if not pd.isna(row.get('VolunteerID')) else None
            if not volunteer_id:
                continue
            
            # Parse training type
            training_type = str(row.get('TrainingType', '')).strip() if not pd.isna(row.get('TrainingType')) else None
            
            # Parse dates
            training_date = None
            expiration_date = None
            
            # Try to get training date from TrainingID or use current date as fallback
            # For now, we'll use expiration date minus a reasonable period, or current date
            if not pd.isna(row.get('ExpirationDate')):
                try:
                    expiration_date = pd.to_datetime(row['ExpirationDate']).date()
                    # Assume training was 1 year before expiration for annual trainings
                    if training_type and 'annual' in training_type.lower():
                        from dateutil.relativedelta import relativedelta
                        training_date = expiration_date - relativedelta(years=1)
                    else:
                        training_date = expiration_date  # Use expiration as training date if no other info
                except:
                    pass
            
            if not training_date:
                training_date = datetime.now().date()
            
            # Parse status/score
            status = str(row.get('Status', '')).strip() if not pd.isna(row.get('Status')) else None
            test_score = None
            if status and 'passed' in status.lower():
                test_score = 100.0  # Assume passed = 100%
            elif status and any(char.isdigit() for char in status):
                # Try to extract numeric score
                try:
                    test_score = float(''.join(filter(str.isdigit, status)))
                except:
                    pass
            
            training_records.append({
                'volunteer_id': volunteer_id,
                'training_type': training_type,
                'training_date': training_date,
                'expiration_date': expiration_date,
                'test_score': test_score,
                'notes': f"Status: {status}" if status else None
            })
        
        logger.info(f"Processed {len(training_records)} training records")
        
        # Connect to database
        DATABASE_URL = "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Clear existing training data (optional - comment out if you want to keep existing)
                # conn.execute(text("TRUNCATE TABLE training RESTART IDENTITY CASCADE"))
                
                # Insert training records - check volunteer exists first
                inserted = 0
                skipped = 0
                for record in training_records:
                    try:
                        # Check if volunteer exists
                        vol_check = conn.execute(text("SELECT COUNT(*) FROM volunteers WHERE volunteer_id = :vid"), {'vid': record['volunteer_id']}).scalar()
                        if vol_check == 0:
                            logger.debug(f"Volunteer {record['volunteer_id']} not found, skipping training record")
                            skipped += 1
                            continue
                        
                        conn.execute(text("""
                            INSERT INTO training (volunteer_id, training_type, training_date, expiration_date, test_score, notes)
                            VALUES (:volunteer_id, :training_type, :training_date, :expiration_date, :test_score, :notes)
                        """), record)
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"Error inserting training record for volunteer {record['volunteer_id']}: {e}")
                        skipped += 1
                        # Rollback this transaction and start a new one
                        trans.rollback()
                        trans = conn.begin()
                        continue
                
                trans.commit()
                if skipped > 0:
                    logger.info(f"⚠️  Skipped {skipped} training records (volunteer not found or other error)")
                logger.info(f"✅ Successfully inserted {inserted} training records")
                
                # Verify
                count = conn.execute(text("SELECT COUNT(*) FROM training")).scalar()
                logger.info(f"Total training records in database: {count}")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error loading training data: {e}")
                raise
        
    except Exception as e:
        logger.error(f"Error loading training data: {e}")
        raise

if __name__ == "__main__":
    load_training_data()

