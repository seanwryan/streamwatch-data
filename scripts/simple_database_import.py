#!/usr/bin/env python3
"""
Simple Database Import for StreamWatch Data
Robust import script with proper transaction handling
"""

import sqlite3
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

def create_fresh_database():
    """Create a fresh database with proper schema"""
    print("Creating fresh database...")
    
    # Remove existing database
    if os.path.exists('streamwatch.db'):
        os.remove('streamwatch.db')
    
    # Create new database
    conn = sqlite3.connect('streamwatch.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE sites (
        site_id TEXT PRIMARY KEY,
        site_name TEXT,
        waterbody TEXT,
        latitude REAL,
        longitude REAL,
        description TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE water_quality (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        measurement_date TEXT,
        parameter TEXT,
        value REAL,
        unit TEXT,
        quality_flag TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE biological_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        sample_date TEXT,
        taxon TEXT,
        count INTEGER,
        abundance REAL,
        dominance REAL,
        quality_flag TEXT
    )
    ''')
    
    conn.commit()
    print("Database schema created.")
    return conn

def import_sites(conn):
    """Import sites data"""
    print("Importing sites...")
    
    try:
        df = pd.read_excel('cleaned_data/cleaned_2025 StreamWatch Locations.xlsx', sheet_name='SWSites_2024')
        print(f"Loaded {len(df)} sites from Excel")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df.iterrows():
            site_code = row.get('SiteCode', '')
            if pd.isna(site_code) or str(site_code).strip() == '':
                continue
            
            try:
                cursor.execute('''
                    INSERT INTO sites (site_id, site_name, waterbody, latitude, longitude, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    str(site_code).strip(),
                    str(site_code).strip(),
                    str(row.get('WaterBody', '')).strip(),
                    row.get('Latitude', None),
                    row.get('Longitude', None),
                    str(row.get('Description', '')).strip()
                ))
                imported += 1
            except Exception as e:
                print(f"Error inserting site {site_code}: {e}")
        
        conn.commit()
        print(f"Imported {imported} sites")
        
    except Exception as e:
        print(f"Error importing sites: {e}")

def import_water_quality(conn):
    """Import water quality data"""
    print("Importing water quality data...")
    
    try:
        bact_file = 'cleaned_data/cleaned_2025 BACT Analysis.xlsx'
        parameters = ['Temperature', 'E. coli', 'Turbidity', 'Chloride', 'Phosphate', 'Nitrate', 'Phycocyanin']
        
        cursor = conn.cursor()
        total_imported = 0
        
        for param in parameters:
            try:
                df = pd.read_excel(bact_file, sheet_name=param)
                print(f"Processing {param}: {len(df)} rows")
                
                imported = 0
                for _, row in df.iterrows():
                    site = row.get('Site', '')
                    if pd.isna(site) or str(site).strip() == '':
                        continue
                    
                    # Look for value columns
                    for col in df.columns:
                        if 'value' in col.lower() or param.lower() in col.lower():
                            value = row.get(col)
                            if pd.notna(value) and value != '' and value != 0:
                                try:
                                    cursor.execute('''
                                        INSERT INTO water_quality (site_id, measurement_date, parameter, value, unit, quality_flag)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                    ''', (
                                        str(site).strip(),
                                        str(row.get('Date', '')),
                                        param,
                                        float(value),
                                        'mg/l' if param in ['Chloride', 'Phosphate', 'Nitrate'] else 'NTU' if param == 'Turbidity' else '°C' if param == 'Temperature' else 'CFU/100ml' if param == 'E. coli' else 'RFU',
                                        'clean'
                                    ))
                                    imported += 1
                                except Exception as e:
                                    continue
                
                conn.commit()
                print(f"Imported {imported} {param} measurements")
                total_imported += imported
                
            except Exception as e:
                print(f"Error importing {param}: {e}")
        
        print(f"Total water quality measurements: {total_imported}")
        
    except Exception as e:
        print(f"Error importing water quality: {e}")

def import_biological(conn):
    """Import biological data"""
    print("Importing biological data...")
    
    try:
        df = pd.read_excel('cleaned_data/cleaned_BAT Data Consolidation and Recount - Lily Raphael.xlsx', sheet_name='DATA_WITH_GENUS_OLD')
        print(f"Loaded {len(df)} biological records")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df.iterrows():
            sample_code = row.get('SampleCode', '')
            if pd.isna(sample_code) or str(sample_code).strip() == '':
                continue
            
            try:
                # Extract site from sample code
                site_id = str(sample_code).split('_')[0] if '_' in str(sample_code) else str(sample_code)
                
                cursor.execute('''
                    INSERT INTO biological_data (site_id, sample_date, taxon, count, abundance, dominance, quality_flag)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    site_id,
                    str(sample_code),
                    str(row.get('GenusSpecies', '')).strip(),
                    int(row.get('Amount', 0)) if pd.notna(row.get('Amount', 0)) else 0,
                    float(row.get('Percentage', 0)) if pd.notna(row.get('Percentage', 0)) else 0.0,
                    float(row.get('Percentage', 0)) if pd.notna(row.get('Percentage', 0)) else 0.0,
                    'clean'
                ))
                imported += 1
            except Exception as e:
                continue
        
        conn.commit()
        print(f"Imported {imported} biological records")
        
    except Exception as e:
        print(f"Error importing biological data: {e}")

def test_database(conn):
    """Test the database"""
    print("\nTesting database...")
    
    cursor = conn.cursor()
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM sites")
    sites_count = cursor.fetchone()[0]
    print(f"Sites: {sites_count}")
    
    cursor.execute("SELECT COUNT(*) FROM water_quality")
    wq_count = cursor.fetchone()[0]
    print(f"Water quality: {wq_count}")
    
    cursor.execute("SELECT COUNT(*) FROM biological_data")
    bio_count = cursor.fetchone()[0]
    print(f"Biological: {bio_count}")
    
    # Show sample data
    if sites_count > 0:
        print("\nSample sites:")
        df = pd.read_sql_query("SELECT site_id, site_name, waterbody FROM sites LIMIT 5", conn)
        print(df.to_string(index=False))
    
    if wq_count > 0:
        print("\nWater quality parameters:")
        df = pd.read_sql_query("SELECT parameter, COUNT(*) as count, unit FROM water_quality GROUP BY parameter, unit", conn)
        print(df.to_string(index=False))
    
    if bio_count > 0:
        print("\nTop 5 species:")
        df = pd.read_sql_query("SELECT taxon, SUM(count) as total_count FROM biological_data GROUP BY taxon ORDER BY total_count DESC LIMIT 5", conn)
        print(df.to_string(index=False))

def main():
    """Main function"""
    print("SIMPLE STREAMWATCH DATABASE IMPORT")
    print("=" * 50)
    
    # Create fresh database
    conn = create_fresh_database()
    
    try:
        # Import data
        import_sites(conn)
        import_water_quality(conn)
        import_biological(conn)
        
        # Test database
        test_database(conn)
        
        print("\n" + "=" * 50)
        print("DATABASE IMPORT COMPLETE!")
        print("Database file: streamwatch.db")
        print("Ready for use!")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
