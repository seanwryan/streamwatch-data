#!/usr/bin/env python3
"""
Load volunteer assignments from Volunteer_Tracking.xlsm Assignments sheet into volunteer_assignments table
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

def load_volunteer_assignments():
    """Load volunteer-site assignments from Assignments sheet"""
    logger.info("Loading volunteer assignments from Volunteer_Tracking.xlsm...")
    
    try:
        # Read assignments data - headers are in row 3 (0-indexed)
        file_path = "data/raw/Volunteer_Tracking.xlsm"
        df = pd.read_excel(file_path, sheet_name='Assignments', header=3)
        
        logger.info(f"Read {len(df)} rows from Assignments sheet")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Map Excel columns to database columns
        # Expected: AssignmentID, VolunteerID, SiteID, FullName, StartDate, EndDate, Role
        assignment_records = []
        
        for idx, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row.get('VolunteerID')) or row.get('VolunteerID') == '':
                continue
            if pd.isna(row.get('SiteID')) or row.get('SiteID') == '':
                continue
            
            # Get volunteer_id and site_code
            volunteer_id = str(int(row['VolunteerID'])) if not pd.isna(row.get('VolunteerID')) else None
            site_code = str(row['SiteID']).strip() if not pd.isna(row.get('SiteID')) else None
            
            if not volunteer_id or not site_code:
                continue
            
            # Parse dates
            assign_start = None
            assign_end = None
            
            if not pd.isna(row.get('StartDate')):
                try:
                    assign_start = pd.to_datetime(row['StartDate']).date()
                except:
                    pass
            
            if not pd.isna(row.get('EndDate')):
                try:
                    assign_end = pd.to_datetime(row['EndDate']).date()
                except:
                    pass
            
            # Use current date as fallback for start date
            if not assign_start:
                assign_start = datetime.now().date()
            
            # Get role/sector
            role = str(row.get('Role', '')).strip() if not pd.isna(row.get('Role')) else None
            
            assignment_records.append({
                'volunteer_id': volunteer_id,
                'site_code': site_code,
                'sector': role,  # Using Role as sector
                'assign_start': assign_start,
                'assign_end': assign_end,
                'is_valid': assign_end is None or assign_end >= datetime.now().date(),  # Valid if no end date or end date in future
                'notes': None
            })
        
        logger.info(f"Processed {len(assignment_records)} assignment records")
        
        # Connect to database
        DATABASE_URL = "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"
        engine = create_engine(DATABASE_URL)
        
        # Load data
        with engine.connect() as conn:
            trans = conn.begin()
            try:
                # Clear existing assignments (optional - comment out if you want to keep existing)
                # conn.execute(text("TRUNCATE TABLE volunteer_assignments RESTART IDENTITY CASCADE"))
                
                # Insert assignment records - handle errors per record
                inserted = 0
                skipped = 0
                for record in assignment_records:
                    try:
                        # Check if volunteer and site exist
                        vol_check = conn.execute(text("SELECT COUNT(*) FROM volunteers WHERE volunteer_id = :vid"), {'vid': record['volunteer_id']}).scalar()
                        site_check = conn.execute(text("SELECT COUNT(*) FROM sites WHERE site_code = :scode"), {'scode': record['site_code']}).scalar()
                        
                        if vol_check == 0:
                            logger.debug(f"Volunteer {record['volunteer_id']} not found, skipping assignment")
                            skipped += 1
                            continue
                        if site_check == 0:
                            logger.debug(f"Site {record['site_code']} not found, skipping assignment")
                            skipped += 1
                            continue
                        
                        conn.execute(text("""
                            INSERT INTO volunteer_assignments (volunteer_id, site_code, sector, assign_start, assign_end, is_valid, notes)
                            VALUES (:volunteer_id, :site_code, :sector, :assign_start, :assign_end, :is_valid, :notes)
                            ON CONFLICT (volunteer_id, site_code, assign_start) DO NOTHING
                        """), record)
                        inserted += 1
                    except Exception as e:
                        logger.warning(f"Error inserting assignment for volunteer {record['volunteer_id']}, site {record['site_code']}: {e}")
                        skipped += 1
                        # Rollback and restart transaction
                        trans.rollback()
                        trans = conn.begin()
                        continue
                
                trans.commit()
                logger.info(f"✅ Successfully inserted {inserted} assignment records")
                if skipped > 0:
                    logger.info(f"⚠️  Skipped {skipped} records (missing volunteer or site)")
                
                # Verify
                count = conn.execute(text("SELECT COUNT(*) FROM volunteer_assignments")).scalar()
                logger.info(f"Total assignment records in database: {count}")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Error loading assignment data: {e}")
                raise
        
    except Exception as e:
        logger.error(f"Error loading assignment data: {e}")
        raise

if __name__ == "__main__":
    load_volunteer_assignments()

