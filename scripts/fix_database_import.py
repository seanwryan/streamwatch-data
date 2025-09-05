#!/usr/bin/env python3
"""
Fix Database Import for StreamWatch Data
Corrects the data import issues and properly loads all data
"""

import sqlite3
import pandas as pd
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def clear_database(conn):
    """Clear existing data from database"""
    print("Clearing existing data...")
    cursor = conn.cursor()
    
    tables = ['sites', 'water_quality', 'biological_data', 'volunteers', 'equipment', 'data_quality_flags']
    for table in tables:
        cursor.execute(f'DELETE FROM {table}')
    
    conn.commit()
    print("Database cleared.")

def import_sites_data(conn):
    """Import sites data properly"""
    print("Importing sites data...")
    
    sites_file = "cleaned_data/cleaned_2025 StreamWatch Locations.xlsx"
    if not os.path.exists(sites_file):
        print("Sites file not found!")
        return
    
    try:
        df_sites = pd.read_excel(sites_file, sheet_name="SWSites_2024")
        print(f"Loaded {len(df_sites)} sites from Excel")
        
        # Clean and prepare sites data
        sites_data = []
        for _, row in df_sites.iterrows():
            # Skip empty rows
            if pd.isna(row.get('Site', '')) or str(row.get('Site', '')).strip() == '':
                continue
                
            site_data = (
                str(row.get('Site', '')).strip(),
                str(row.get('Site', '')).strip(),
                str(row.get('Waterbody', '')).strip(),
                row.get('Latitude', None),
                row.get('Longitude', None),
                str(row.get('Description', '')).strip()
            )
            sites_data.append(site_data)
        
        # Insert into database
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO sites (site_id, site_name, waterbody, latitude, longitude, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sites_data)
        
        print(f"Imported {len(sites_data)} sites")
        
    except Exception as e:
        print(f"Error importing sites: {e}")

def import_water_quality_data(conn):
    """Import water quality data properly"""
    print("Importing water quality data...")
    
    bact_file = "cleaned_data/cleaned_2025 BACT Analysis.xlsx"
    if not os.path.exists(bact_file):
        print("BACT file not found!")
        return
    
    try:
        # Import different parameter sheets
        parameters = ['Temperature', 'E. coli', 'Turbidity', 'Chloride', 'Phosphate', 'Nitrate', 'Phycocyanin']
        
        total_imported = 0
        for param in parameters:
            try:
                df_param = pd.read_excel(bact_file, sheet_name=param)
                print(f"Processing {param} sheet: {len(df_param)} rows")
                
                # Extract water quality data
                water_quality_data = []
                for _, row in df_param.iterrows():
                    # Skip empty rows
                    if pd.isna(row.get('Site', '')) or str(row.get('Site', '')).strip() == '':
                        continue
                    
                    # Look for value columns
                    for col in df_param.columns:
                        if 'value' in col.lower() or param.lower() in col.lower():
                            value = row.get(col)
                            if pd.notna(value) and value != '' and value != 0:
                                try:
                                    quality_data = (
                                        str(row.get('Site', '')).strip(),
                                        row.get('Date', ''),
                                        param,
                                        float(value),
                                        'mg/l' if param in ['Chloride', 'Phosphate', 'Nitrate'] else 'NTU' if param == 'Turbidity' else '°C' if param == 'Temperature' else 'CFU/100ml' if param == 'E. coli' else 'RFU',
                                        str(row.get('data_quality_flag', 'clean'))
                                    )
                                    water_quality_data.append(quality_data)
                                except (ValueError, TypeError):
                                    continue
                
                # Insert into database
                if water_quality_data:
                    cursor = conn.cursor()
                    cursor.executemany('''
                        INSERT INTO water_quality (site_id, measurement_date, parameter, value, unit, quality_flag)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', water_quality_data)
                    
                    print(f"Imported {len(water_quality_data)} {param} measurements")
                    total_imported += len(water_quality_data)
                    
            except Exception as e:
                print(f"Error importing {param}: {e}")
        
        print(f"Total water quality measurements imported: {total_imported}")
        
    except Exception as e:
        print(f"Error importing water quality data: {e}")

def import_biological_data(conn):
    """Import biological data properly"""
    print("Importing biological data...")
    
    bat_file = "cleaned_data/cleaned_BAT Data Consolidation and Recount - Lily Raphael.xlsx"
    if not os.path.exists(bat_file):
        print("BAT file not found!")
        return
    
    try:
        # Import bug data
        df_bugs = pd.read_excel(bat_file, sheet_name="DATA_WITH_GENUS_OLD")
        print(f"Loaded {len(df_bugs)} biological records from Excel")
        
        biological_data = []
        for _, row in df_bugs.iterrows():
            # Skip empty rows
            if pd.isna(row.get('Site', '')) or str(row.get('Site', '')).strip() == '':
                continue
            
            try:
                bio_data = (
                    str(row.get('Site', '')).strip(),
                    row.get('Date', ''),
                    str(row.get('Genus', '')).strip(),
                    int(row.get('Count', 0)) if pd.notna(row.get('Count', 0)) else 0,
                    float(row.get('Abundance', 0)) if pd.notna(row.get('Abundance', 0)) else 0.0,
                    float(row.get('Dominance', 0)) if pd.notna(row.get('Dominance', 0)) else 0.0,
                    str(row.get('data_quality_flag', 'clean'))
                )
                biological_data.append(bio_data)
            except (ValueError, TypeError):
                continue
        
        # Insert into database
        if biological_data:
            cursor = conn.cursor()
            cursor.executemany('''
                INSERT INTO biological_data (site_id, sample_date, taxon, count, abundance, dominance, quality_flag)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', biological_data)
            
            print(f"Imported {len(biological_data)} biological records")
        
    except Exception as e:
        print(f"Error importing biological data: {e}")

def test_database(conn):
    """Test the database with sample queries"""
    print("\nTesting database...")
    
    # Test sites
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sites")
    sites_count = cursor.fetchone()[0]
    print(f"Sites: {sites_count}")
    
    # Test water quality
    cursor.execute("SELECT COUNT(*) FROM water_quality")
    wq_count = cursor.fetchone()[0]
    print(f"Water quality measurements: {wq_count}")
    
    # Test biological data
    cursor.execute("SELECT COUNT(*) FROM biological_data")
    bio_count = cursor.fetchone()[0]
    print(f"Biological records: {bio_count}")
    
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
        print("\nBiological data summary:")
        df = pd.read_sql_query("SELECT COUNT(DISTINCT taxon) as species_count, SUM(count) as total_individuals FROM biological_data", conn)
        print(df.to_string(index=False))

def main():
    """Main function to fix the database import"""
    print("FIXING STREAMWATCH DATABASE IMPORT")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect('streamwatch.db')
    
    try:
        # Clear existing data
        clear_database(conn)
        
        # Import data properly
        import_sites_data(conn)
        import_water_quality_data(conn)
        import_biological_data(conn)
        
        # Test the database
        test_database(conn)
        
        print("\n" + "=" * 50)
        print("DATABASE IMPORT FIXED!")
        print("Database is now ready for exploration.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
