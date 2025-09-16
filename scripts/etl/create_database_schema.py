#!/usr/bin/env python3
"""
Database Setup for StreamWatch Data
Creates SQLite database and imports cleaned data for visualization
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def create_database_schema():
    """Create the database schema for StreamWatch data"""
    print("Creating StreamWatch database schema...")
    
    # Connect to SQLite database (creates if doesn't exist)
    conn = sqlite3.connect('streamwatch.db')
    cursor = conn.cursor()
    
    # Create tables for different data types
    
    # 1. Sites table - monitoring locations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sites (
        site_id TEXT PRIMARY KEY,
        site_name TEXT,
        waterbody TEXT,
        latitude REAL,
        longitude REAL,
        description TEXT,
        active BOOLEAN DEFAULT 1,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Water quality measurements table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS water_quality (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        measurement_date DATE,
        parameter TEXT,
        value REAL,
        unit TEXT,
        method TEXT,
        quality_flag TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (site_id) REFERENCES sites (site_id)
    )
    ''')
    
    # 3. Volunteers table
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
    
    # 4. Equipment table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        equipment_id TEXT PRIMARY KEY,
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
    
    # 5. Biological data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS biological_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id TEXT,
        sample_date DATE,
        taxon TEXT,
        count INTEGER,
        abundance REAL,
        dominance REAL,
        index_value REAL,
        quality_flag TEXT,
        notes TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (site_id) REFERENCES sites (site_id)
    )
    ''')
    
    # 6. Data quality flags table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data_quality_flags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT,
        record_id TEXT,
        flag_type TEXT,
        flag_value TEXT,
        description TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_water_quality_site_date ON water_quality (site_id, measurement_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_water_quality_parameter ON water_quality (parameter)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_biological_site_date ON biological_data (site_id, sample_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_biological_taxon ON biological_data (taxon)')
    
    conn.commit()
    print("Database schema created successfully!")
    return conn

def import_cleaned_data(conn):
    """Import cleaned data from Excel files into the database"""
    print("Importing cleaned data...")
    
    cleaned_data_folder = "cleaned_data"
    if not os.path.exists(cleaned_data_folder):
        print("No cleaned data folder found!")
        return
    
    # Import sites data
    try:
        sites_file = os.path.join(cleaned_data_folder, "cleaned_2025 StreamWatch Locations.xlsx")
        if os.path.exists(sites_file):
            print("Importing sites data...")
            df_sites = pd.read_excel(sites_file, sheet_name="SWSites_2024")
            
            # Clean and prepare sites data
            sites_data = []
            for _, row in df_sites.iterrows():
                site_data = {
                    'site_id': str(row.get('Site', '')),
                    'site_name': str(row.get('Site', '')),
                    'waterbody': str(row.get('Waterbody', '')),
                    'latitude': row.get('Latitude', None),
                    'longitude': row.get('Longitude', None),
                    'description': str(row.get('Description', ''))
                }
                sites_data.append(site_data)
            
            # Insert into database
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT OR REPLACE INTO sites (site_id, site_name, waterbody, latitude, longitude, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', [(s['site_id'], s['site_name'], s['waterbody'], s['latitude'], s['longitude'], s['description']) for s in sites_data])
            
            print(f"Imported {len(sites_data)} sites")
    except Exception as e:
        print(f"Error importing sites: {e}")
    
    # Import water quality data from BACT analysis
    try:
        bact_file = os.path.join(cleaned_data_folder, "cleaned_2025 BACT Analysis.xlsx")
        if os.path.exists(bact_file):
            print("Importing water quality data...")
            
            # Import different parameter sheets
            parameters = ['Temperature', 'E. coli', 'Turbidity', 'Chloride', 'Phosphate', 'Nitrate', 'Phycocyanin']
            
            for param in parameters:
                try:
                    df_param = pd.read_excel(bact_file, sheet_name=param)
                    
                    # Extract water quality data
                    water_quality_data = []
                    for _, row in df_param.iterrows():
                        # Look for value columns
                        for col in df_param.columns:
                            if 'value' in col.lower() or param.lower() in col.lower():
                                value = row.get(col)
                                if pd.notna(value) and value != '':
                                    quality_data = {
                                        'site_id': str(row.get('Site', '')),
                                        'measurement_date': row.get('Date', ''),
                                        'parameter': param,
                                        'value': float(value) if pd.notna(value) else None,
                                        'unit': 'mg/l' if param in ['Chloride', 'Phosphate', 'Nitrate'] else 'NTU' if param == 'Turbidity' else '°C' if param == 'Temperature' else 'CFU/100ml' if param == 'E. coli' else 'RFU',
                                        'quality_flag': row.get('data_quality_flag', 'clean')
                                    }
                                    water_quality_data.append(quality_data)
                    
                    # Insert into database
                    if water_quality_data:
                        cursor.executemany('''
                            INSERT INTO water_quality (site_id, measurement_date, parameter, value, unit, quality_flag)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', [(w['site_id'], w['measurement_date'], w['parameter'], w['value'], w['unit'], w['quality_flag']) for w in water_quality_data])
                        
                        print(f"Imported {len(water_quality_data)} {param} measurements")
                        
                except Exception as e:
                    print(f"Error importing {param}: {e}")
    except Exception as e:
        print(f"Error importing water quality data: {e}")
    
    # Import biological data
    try:
        bat_file = os.path.join(cleaned_data_folder, "cleaned_BAT Data Consolidation and Recount - Lily Raphael.xlsx")
        if os.path.exists(bat_file):
            print("Importing biological data...")
            
            # Import bug data
            df_bugs = pd.read_excel(bat_file, sheet_name="DATA_WITH_GENUS_OLD")
            
            biological_data = []
            for _, row in df_bugs.iterrows():
                bio_data = {
                    'site_id': str(row.get('Site', '')),
                    'sample_date': row.get('Date', ''),
                    'taxon': str(row.get('Genus', '')),
                    'count': row.get('Count', 0),
                    'abundance': row.get('Abundance', 0),
                    'dominance': row.get('Dominance', 0),
                    'quality_flag': row.get('data_quality_flag', 'clean')
                }
                biological_data.append(bio_data)
            
            # Insert into database
            if biological_data:
                cursor.executemany('''
                    INSERT INTO biological_data (site_id, sample_date, taxon, count, abundance, dominance, quality_flag)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', [(b['site_id'], b['sample_date'], b['taxon'], b['count'], b['abundance'], b['dominance'], b['quality_flag']) for b in biological_data])
                
                print(f"Imported {len(biological_data)} biological records")
                
    except Exception as e:
        print(f"Error importing biological data: {e}")
    
    conn.commit()
    print("Data import completed!")

def create_sample_queries(conn):
    """Create some sample queries to test the database"""
    print("Creating sample queries...")
    
    cursor = conn.cursor()
    
    # Sample query 1: Water quality summary by site
    query1 = '''
    SELECT 
        s.site_name,
        s.waterbody,
        wq.parameter,
        COUNT(*) as measurement_count,
        AVG(wq.value) as avg_value,
        MIN(wq.value) as min_value,
        MAX(wq.value) as max_value
    FROM water_quality wq
    JOIN sites s ON wq.site_id = s.site_id
    GROUP BY s.site_name, s.waterbody, wq.parameter
    ORDER BY s.site_name, wq.parameter
    '''
    
    # Sample query 2: Recent measurements
    query2 = '''
    SELECT 
        s.site_name,
        s.waterbody,
        wq.measurement_date,
        wq.parameter,
        wq.value,
        wq.unit,
        wq.quality_flag
    FROM water_quality wq
    JOIN sites s ON wq.site_id = s.site_id
    ORDER BY wq.measurement_date DESC
    LIMIT 50
    '''
    
    # Sample query 3: Biological diversity by site
    query3 = '''
    SELECT 
        s.site_name,
        s.waterbody,
        COUNT(DISTINCT bd.taxon) as species_count,
        SUM(bd.count) as total_individuals,
        AVG(bd.dominance) as avg_dominance
    FROM biological_data bd
    JOIN sites s ON bd.site_id = s.site_id
    GROUP BY s.site_name, s.waterbody
    ORDER BY species_count DESC
    '''
    
    # Test queries
    print("\nTesting sample queries...")
    
    try:
        result1 = pd.read_sql_query(query1, conn)
        print(f"Query 1 - Water quality summary: {len(result1)} records")
        
        result2 = pd.read_sql_query(query2, conn)
        print(f"Query 2 - Recent measurements: {len(result2)} records")
        
        result3 = pd.read_sql_query(query3, conn)
        print(f"Query 3 - Biological diversity: {len(result3)} records")
        
    except Exception as e:
        print(f"Error testing queries: {e}")

def main():
    """Main function to set up the database"""
    print("STREAMWATCH DATABASE SETUP")
    print("=" * 50)
    
    # Create database schema
    conn = create_database_schema()
    
    # Import cleaned data
    import_cleaned_data(conn)
    
    # Test with sample queries
    create_sample_queries(conn)
    
    # Close connection
    conn.close()
    
    print("\n" + "=" * 50)
    print("DATABASE SETUP COMPLETE!")
    print("Database file: streamwatch.db")
    print("Ready for visualization dashboard!")

if __name__ == "__main__":
    main()
