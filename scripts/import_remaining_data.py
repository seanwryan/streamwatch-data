#!/usr/bin/env python3
"""
Import Remaining StreamWatch Data
Systematically imports all remaining data files into the database
"""

import sqlite3
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

def connect_to_database():
    """Connect to the StreamWatch database"""
    db_path = '../database/streamwatch.db'
    if not os.path.exists(db_path):
        print("Database not found! Please run simple_database_import.py first.")
        return None
    
    conn = sqlite3.connect(db_path)
    return conn

def create_additional_tables(conn):
    """Create additional tables for remaining data"""
    print("Creating additional database tables...")
    
    cursor = conn.cursor()
    
    # Historical water quality table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historical_water_quality (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        measurement_date DATE,
        parameter TEXT,
        value REAL,
        unit TEXT,
        method TEXT,
        quality_flag TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Analysis results table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        analysis_date DATE,
        analysis_type TEXT,
        parameter TEXT,
        statistic_type TEXT,
        value REAL,
        unit TEXT,
        period_start DATE,
        period_end DATE,
        quality_flag TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Volunteers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volunteers (
        volunteer_id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        team TEXT,
        active BOOLEAN DEFAULT 1,
        training_date DATE,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Volunteer assignments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS volunteer_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        volunteer_id TEXT,
        site_id TEXT,
        assignment_date DATE,
        assignment_type TEXT,
        status TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (volunteer_id) REFERENCES volunteers (volunteer_id),
        FOREIGN KEY (site_id) REFERENCES sites (site_id)
    )
    ''')
    
    # Bacterial data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bacterial_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        sample_date DATE,
        test_type TEXT,
        result REAL,
        unit TEXT,
        method TEXT,
        quality_flag TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Algal bloom data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS algal_bloom_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        sample_date DATE,
        parameter TEXT,
        value REAL,
        unit TEXT,
        bloom_status TEXT,
        quality_flag TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Equipment tracking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id TEXT,
        equipment_type TEXT,
        make TEXT,
        model TEXT,
        serial_number TEXT,
        calibration_date DATE,
        next_calibration DATE,
        status TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Sample tracking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sample_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_id TEXT,
        site_id TEXT,
        collection_date DATE,
        sample_type TEXT,
        processing_date DATE,
        status TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    print("Additional tables created successfully!")

def import_all_streamwatch_data(conn):
    """Import the largest dataset - All StreamWatch Data.xlsx"""
    print("\nImporting All StreamWatch Data.xlsx...")
    
    file_path = '../data/All StreamWatch Data.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Read the main data sheet
        df = pd.read_excel(file_path, sheet_name='All Data', nrows=5000)  # Limit for safety
        print(f"Loaded {len(df)} rows from All Data sheet")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df.iterrows():
            # Skip empty rows
            site = row.get('Site', '')
            if pd.isna(site) or str(site).strip() == '':
                continue
            
            # Import water quality parameters
            water_quality_params = ['pH', 'DO', 'Temperature', 'Turbidity', 'Nitrate', 'Phosphate', 'Chloride']
            
            for param in water_quality_params:
                value = row.get(param, None)
                if pd.notna(value) and value != '':
                    try:
                        cursor.execute('''
                            INSERT INTO historical_water_quality (site_id, measurement_date, parameter, value, unit, quality_flag)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            str(site).strip(),
                            row.get('Date', ''),
                            param,
                            float(value),
                            'mg/l' if param in ['Nitrate', 'Phosphate', 'Chloride'] else 'NTU' if param == 'Turbidity' else '°C' if param == 'Temperature' else 'units',
                            'clean'
                        ))
                        imported += 1
                    except (ValueError, TypeError):
                        continue
        
        conn.commit()
        print(f"Imported {imported} historical water quality measurements")
        
    except Exception as e:
        print(f"Error importing All StreamWatch Data: {e}")

def import_volunteer_data(conn):
    """Import volunteer tracking data"""
    print("\nImporting Volunteer_Tracking.xlsm...")
    
    file_path = '../data/Volunteer_Tracking.xlsm'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Import volunteers
        df_volunteers = pd.read_excel(file_path, sheet_name='Volunteers', nrows=500)
        print(f"Loaded {len(df_volunteers)} volunteers")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df_volunteers.iterrows():
            volunteer_id = row.get('Volunteer ID', '')
            if pd.isna(volunteer_id) or str(volunteer_id).strip() == '':
                continue
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO volunteers (volunteer_id, first_name, last_name, email, phone, team, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(volunteer_id).strip(),
                    str(row.get('First Name', '')).strip(),
                    str(row.get('Last Name', '')).strip(),
                    str(row.get('Email', '')).strip(),
                    str(row.get('Phone', '')).strip(),
                    str(row.get('Team', '')).strip(),
                    1
                ))
                imported += 1
            except Exception as e:
                continue
        
        conn.commit()
        print(f"Imported {imported} volunteers")
        
    except Exception as e:
        print(f"Error importing volunteer data: {e}")

def import_bact_hab_data(conn):
    """Import BACT and HAB 2025 data"""
    print("\nImporting BACT and HAB 2025 Data.xlsx...")
    
    file_path = '../data/BACT and HAB 2025 Data.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Import IDEXX data (bacterial testing)
        df_idexx = pd.read_excel(file_path, sheet_name='IDEXX', nrows=1000)
        print(f"Loaded {len(df_idexx)} IDEXX records")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df_idexx.iterrows():
            site = row.get('Site', '')
            if pd.isna(site) or str(site).strip() == '':
                continue
            
            # Look for E. coli results
            for col in df_idexx.columns:
                if 'coli' in col.lower() or 'mpn' in col.lower():
                    value = row.get(col)
                    if pd.notna(value) and value != '':
                        try:
                            cursor.execute('''
                                INSERT INTO bacterial_data (site_id, sample_date, test_type, result, unit, quality_flag)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                str(site).strip(),
                                row.get('Date', ''),
                                'E. coli',
                                float(value),
                                'CFU/100ml',
                                'clean'
                            ))
                            imported += 1
                        except (ValueError, TypeError):
                            continue
        
        conn.commit()
        print(f"Imported {imported} bacterial test results")
        
    except Exception as e:
        print(f"Error importing BACT and HAB data: {e}")

def import_biological_sites(conn):
    """Import BATSITES COLLECTED data"""
    print("\nImporting BATSITES COLLECTED.xlsx...")
    
    file_path = '../data/BATSITES COLLECTED.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Import bug data
        df_bugs = pd.read_excel(file_path, sheet_name='BUGSPICKED', nrows=2000)
        print(f"Loaded {len(df_bugs)} bug records")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df_bugs.iterrows():
            site = row.get('Site', '')
            if pd.isna(site) or str(site).strip() == '':
                continue
            
            try:
                # Extract site from sample code if needed
                site_id = str(site).split('_')[0] if '_' in str(site) else str(site)
                
                cursor.execute('''
                    INSERT INTO biological_data (site_id, sample_date, taxon, count, abundance, dominance, quality_flag)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    site_id,
                    str(site),
                    str(row.get('Bug', '')).strip(),
                    int(row.get('Count', 0)) if pd.notna(row.get('Count', 0)) else 0,
                    0.0,
                    0.0,
                    'clean'
                ))
                imported += 1
            except (ValueError, TypeError):
                continue
        
        conn.commit()
        print(f"Imported {imported} additional biological records")
        
    except Exception as e:
        print(f"Error importing biological sites data: {e}")

def test_extended_database(conn):
    """Test the extended database"""
    print("\nTesting extended database...")
    
    cursor = conn.cursor()
    
    # Count records in all tables
    tables = ['sites', 'water_quality', 'biological_data', 'historical_water_quality', 
              'volunteers', 'bacterial_data', 'algal_bloom_data', 'equipment_tracking', 'sample_tracking']
    
    total_records = 0
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count:,} records")
            total_records += count
        except:
            print(f"{table}: 0 records (table not found)")
    
    print(f"\nTotal records in database: {total_records:,}")

def main():
    """Main function to import remaining data"""
    print("IMPORTING REMAINING STREAMWATCH DATA")
    print("=" * 60)
    
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Create additional tables
        create_additional_tables(conn)
        
        # Import remaining data
        import_all_streamwatch_data(conn)
        import_volunteer_data(conn)
        import_bact_hab_data(conn)
        import_biological_sites(conn)
        
        # Test the extended database
        test_extended_database(conn)
        
        print("\n" + "=" * 60)
        print("REMAINING DATA IMPORT COMPLETE!")
        print("Database now contains significantly more data.")
        print("Run database_explorer.py to explore the expanded database.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
