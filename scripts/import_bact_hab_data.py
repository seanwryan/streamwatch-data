#!/usr/bin/env python3
"""
Import BACT and HAB 2025 Data
Safely imports BACT and HAB 2025 Data.xlsx (1.0 MB) - bacterial testing and algal bloom data
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
        print("Database not found!")
        return None
    
    conn = sqlite3.connect(db_path)
    return conn

def analyze_bact_hab_file():
    """First, let's analyze the BACT and HAB file structure"""
    print("ANALYZING BACT AND HAB 2025 DATA FILE")
    print("=" * 50)
    
    file_path = '../data/BACT and HAB 2025 Data.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return None
    
    try:
        # Get sheet names first
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Analyze each sheet
        for sheet_name in xl_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)  # Just first 10 rows
            print(f"Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
            print("Sample data:")
            print(df.head(3).to_string(index=False))
            print("-" * 40)
        
        return xl_file.sheet_names
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return None

def import_bact_hab_data(conn):
    """Import BACT and HAB data"""
    print("\nIMPORTING BACT AND HAB 2025 DATA")
    print("=" * 50)
    
    file_path = '../data/BACT and HAB 2025 Data.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Get sheet names
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        cursor = conn.cursor()
        total_bacterial_imported = 0
        total_algal_imported = 0
        
        # Import from each sheet
        for sheet_name in xl_file.sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            
            try:
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"Loaded {len(df)} rows from {sheet_name}")
                print(f"Columns: {list(df.columns)}")
                
                # Skip empty sheets
                if len(df) == 0:
                    print("Sheet is empty, skipping...")
                    continue
                
                # Determine if this is bacterial or algal data based on sheet name
                is_bacterial = any(keyword in sheet_name.lower() for keyword in ['idexx', 'coli', 'bact', 'bacterial'])
                is_algal = any(keyword in sheet_name.lower() for keyword in ['hab', 'algal', 'bloom', 'phyco'])
                
                # Import bacterial data
                if is_bacterial:
                    imported = 0
                    for _, row in df.iterrows():
                        # Skip empty rows
                        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                            continue
                        
                        try:
                            # Extract bacterial information
                            site_id = ''
                            sample_date = ''
                            test_type = 'E. coli'
                            result = 0.0
                            unit = 'CFU/100ml'
                            method = 'IDEXX'
                            quality_flag = 'clean'
                            notes = ''
                            
                            # Try to extract information from available columns
                            for i, col in enumerate(df.columns):
                                col_str = str(col).lower()
                                if 'site' in col_str or 'station' in col_str or 'location' in col_str:
                                    site_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'date' in col_str:
                                    sample_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                                elif 'coli' in col_str or 'mpn' in col_str or 'result' in col_str:
                                    try:
                                        result = float(row.iloc[i]) if pd.notna(row.iloc[i]) else 0.0
                                    except (ValueError, TypeError):
                                        result = 0.0
                                elif 'method' in col_str:
                                    method = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'IDEXX'
                                elif 'flag' in col_str or 'quality' in col_str:
                                    quality_flag = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'clean'
                                elif 'note' in col_str or 'comment' in col_str:
                                    notes = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            
                            # If no site_id found, try to extract from sample code
                            if not site_id:
                                for i, col in enumerate(df.columns):
                                    if pd.notna(row.iloc[i]) and str(row.iloc[i]).strip() != '':
                                        potential_site = str(row.iloc[i]).strip()
                                        # Check if it looks like a site code
                                        if len(potential_site) <= 4 and potential_site.isalnum():
                                            site_id = potential_site
                                            break
                            
                            # Only import if we have meaningful data
                            if site_id and result > 0:
                                # Insert into bacterial data table
                                cursor.execute('''
                                    INSERT INTO bacterial_data 
                                    (site_id, sample_date, test_type, result, unit, method, quality_flag, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (site_id, sample_date, test_type, result, unit, method, quality_flag, notes))
                                
                                imported += 1
                            
                        except Exception as e:
                            print(f"Error importing bacterial row: {e}")
                            continue
                    
                    print(f"Imported {imported} bacterial records from {sheet_name}")
                    total_bacterial_imported += imported
                
                # Import algal bloom data
                elif is_algal:
                    imported = 0
                    for _, row in df.iterrows():
                        # Skip empty rows
                        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                            continue
                        
                        try:
                            # Extract algal information
                            site_id = ''
                            sample_date = ''
                            parameter = 'Phycocyanin'
                            value = 0.0
                            unit = 'μg/L'
                            bloom_status = 'Unknown'
                            quality_flag = 'clean'
                            notes = ''
                            
                            # Try to extract information from available columns
                            for i, col in enumerate(df.columns):
                                col_str = str(col).lower()
                                if 'site' in col_str or 'station' in col_str or 'location' in col_str:
                                    site_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'date' in col_str:
                                    sample_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                                elif 'phyco' in col_str or 'algal' in col_str or 'bloom' in col_str or 'result' in col_str:
                                    try:
                                        value = float(row.iloc[i]) if pd.notna(row.iloc[i]) else 0.0
                                    except (ValueError, TypeError):
                                        value = 0.0
                                elif 'status' in col_str or 'condition' in col_str:
                                    bloom_status = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'Unknown'
                                elif 'flag' in col_str or 'quality' in col_str:
                                    quality_flag = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'clean'
                                elif 'note' in col_str or 'comment' in col_str:
                                    notes = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            
                            # If no site_id found, try to extract from sample code
                            if not site_id:
                                for i, col in enumerate(df.columns):
                                    if pd.notna(row.iloc[i]) and str(row.iloc[i]).strip() != '':
                                        potential_site = str(row.iloc[i]).strip()
                                        # Check if it looks like a site code
                                        if len(potential_site) <= 4 and potential_site.isalnum():
                                            site_id = potential_site
                                            break
                            
                            # Only import if we have meaningful data
                            if site_id and value > 0:
                                # Insert into algal bloom data table
                                cursor.execute('''
                                    INSERT INTO algal_bloom_data 
                                    (site_id, sample_date, parameter, value, unit, bloom_status, quality_flag, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (site_id, sample_date, parameter, value, unit, bloom_status, quality_flag, notes))
                                
                                imported += 1
                            
                        except Exception as e:
                            print(f"Error importing algal row: {e}")
                            continue
                    
                    print(f"Imported {imported} algal bloom records from {sheet_name}")
                    total_algal_imported += imported
                
                # If neither bacterial nor algal, try to import as general water quality
                else:
                    imported = 0
                    for _, row in df.iterrows():
                        # Skip empty rows
                        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                            continue
                        
                        try:
                            # Extract general information
                            site_id = ''
                            sample_date = ''
                            parameter = ''
                            value = 0.0
                            unit = ''
                            method = ''
                            quality_flag = 'clean'
                            notes = ''
                            
                            # Try to extract information from available columns
                            for i, col in enumerate(df.columns):
                                col_str = str(col).lower()
                                if 'site' in col_str or 'station' in col_str or 'location' in col_str:
                                    site_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'date' in col_str:
                                    sample_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                                elif 'parameter' in col_str or 'analyte' in col_str:
                                    parameter = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'value' in col_str or 'result' in col_str or 'concentration' in col_str:
                                    try:
                                        value = float(row.iloc[i]) if pd.notna(row.iloc[i]) else 0.0
                                    except (ValueError, TypeError):
                                        value = 0.0
                                elif 'unit' in col_str:
                                    unit = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'method' in col_str:
                                    method = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'flag' in col_str or 'quality' in col_str:
                                    quality_flag = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'clean'
                                elif 'note' in col_str or 'comment' in col_str:
                                    notes = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            
                            # Only import if we have meaningful data
                            if site_id and (parameter or value > 0):
                                # Insert into historical water quality table
                                cursor.execute('''
                                    INSERT INTO historical_water_quality 
                                    (site_id, measurement_date, parameter, value, unit, method, quality_flag, notes)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (site_id, sample_date, parameter, value, unit, method, quality_flag, notes))
                                
                                imported += 1
                            
                        except Exception as e:
                            print(f"Error importing general row: {e}")
                            continue
                    
                    print(f"Imported {imported} general records from {sheet_name}")
                
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                continue
        
        conn.commit()
        print(f"\nTotal bacterial records imported: {total_bacterial_imported}")
        print(f"Total algal bloom records imported: {total_algal_imported}")
        
    except Exception as e:
        print(f"Error importing BACT and HAB data: {e}")

def test_bact_hab_import(conn):
    """Test the BACT and HAB import"""
    print("\nTESTING BACT AND HAB IMPORT")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    try:
        # Count bacterial records
        cursor.execute("SELECT COUNT(*) FROM bacterial_data")
        bacterial_count = cursor.fetchone()[0]
        print(f"Total bacterial records: {bacterial_count}")
        
        # Count algal bloom records
        cursor.execute("SELECT COUNT(*) FROM algal_bloom_data")
        algal_count = cursor.fetchone()[0]
        print(f"Total algal bloom records: {algal_count}")
        
        if bacterial_count > 0:
            # Show sample bacterial data
            df = pd.read_sql_query("SELECT * FROM bacterial_data LIMIT 5", conn)
            print("\nSample bacterial data:")
            print(df.to_string(index=False))
            
            # Show test types
            cursor.execute("SELECT test_type, COUNT(*) FROM bacterial_data GROUP BY test_type")
            test_types = cursor.fetchall()
            print(f"\nBacterial test types:")
            for test_type, count in test_types:
                print(f"  {test_type}: {count} records")
        
        if algal_count > 0:
            # Show sample algal data
            df = pd.read_sql_query("SELECT * FROM algal_bloom_data LIMIT 5", conn)
            print("\nSample algal bloom data:")
            print(df.to_string(index=False))
            
            # Show parameters
            cursor.execute("SELECT parameter, COUNT(*) FROM algal_bloom_data GROUP BY parameter")
            parameters = cursor.fetchall()
            print(f"\nAlgal bloom parameters:")
            for param, count in parameters:
                print(f"  {param}: {count} records")
        
    except Exception as e:
        print(f"Error testing BACT and HAB import: {e}")

def main():
    """Main function to import BACT and HAB data"""
    print("IMPORTING BACT AND HAB 2025 DATA (SAFE TEST)")
    print("=" * 60)
    print("File size: 1.0 MB (next file)")
    print("Purpose: Bacterial testing (E. coli) and harmful algal bloom data")
    print("=" * 60)
    
    # First analyze the file structure
    sheets = analyze_bact_hab_file()
    if not sheets:
        return
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Import the data
        import_bact_hab_data(conn)
        
        # Test the import
        test_bact_hab_import(conn)
        
        print("\n" + "=" * 60)
        print("BACT AND HAB 2025 DATA IMPORT COMPLETE!")
        print("This was another safe test with a medium-sized file.")
        print("Ready to proceed to the next file.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
