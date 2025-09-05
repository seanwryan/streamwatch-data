#!/usr/bin/env python3
"""
Import CAT Meter Tracking Data
Safely imports the smallest file first - CAT Meter Tracking.xlsx (100 KB)
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

def analyze_cat_meter_file():
    """First, let's analyze the CAT Meter Tracking file structure"""
    print("ANALYZING CAT METER TRACKING FILE")
    print("=" * 50)
    
    file_path = '../data/CAT Meter Tracking.xlsx'
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

def import_cat_meter_data(conn):
    """Import CAT meter tracking data"""
    print("\nIMPORTING CAT METER TRACKING DATA")
    print("=" * 50)
    
    file_path = '../data/CAT Meter Tracking.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Get sheet names
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        cursor = conn.cursor()
        total_imported = 0
        
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
                
                # Import equipment data
                imported = 0
                for _, row in df.iterrows():
                    # Skip empty rows
                    if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                        continue
                    
                    try:
                        # Extract equipment information
                        equipment_id = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                        equipment_type = 'CAT Meter'  # Default type
                        make = ''
                        model = ''
                        serial_number = ''
                        calibration_date = ''
                        next_calibration = ''
                        status = 'Active'
                        notes = ''
                        
                        # Try to extract more information from available columns
                        for i, col in enumerate(df.columns):
                            if 'make' in col.lower() or 'brand' in col.lower():
                                make = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            elif 'model' in col.lower():
                                model = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            elif 'serial' in col.lower():
                                serial_number = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            elif 'calibrat' in col.lower() and 'date' in col.lower():
                                calibration_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                            elif 'next' in col.lower() or 'due' in col.lower():
                                next_calibration = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                            elif 'status' in col.lower() or 'condition' in col.lower():
                                status = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'Active'
                            elif 'note' in col.lower() or 'comment' in col.lower():
                                notes = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                        
                        # Insert into database
                        cursor.execute('''
                            INSERT INTO equipment_tracking 
                            (equipment_id, equipment_type, make, model, serial_number, 
                             calibration_date, next_calibration, status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (equipment_id, equipment_type, make, model, serial_number,
                              calibration_date, next_calibration, status, notes))
                        
                        imported += 1
                        
                    except Exception as e:
                        print(f"Error importing row: {e}")
                        continue
                
                print(f"Imported {imported} equipment records from {sheet_name}")
                total_imported += imported
                
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                continue
        
        conn.commit()
        print(f"\nTotal equipment records imported: {total_imported}")
        
    except Exception as e:
        print(f"Error importing CAT meter data: {e}")

def test_equipment_import(conn):
    """Test the equipment import"""
    print("\nTESTING EQUIPMENT IMPORT")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    try:
        # Count equipment records
        cursor.execute("SELECT COUNT(*) FROM equipment_tracking")
        count = cursor.fetchone()[0]
        print(f"Total equipment records: {count}")
        
        if count > 0:
            # Show sample data
            df = pd.read_sql_query("SELECT * FROM equipment_tracking LIMIT 5", conn)
            print("\nSample equipment data:")
            print(df.to_string(index=False))
            
            # Show equipment types
            cursor.execute("SELECT equipment_type, COUNT(*) FROM equipment_tracking GROUP BY equipment_type")
            types = cursor.fetchall()
            print(f"\nEquipment types:")
            for eq_type, count in types:
                print(f"  {eq_type}: {count} records")
        
    except Exception as e:
        print(f"Error testing equipment import: {e}")

def main():
    """Main function to import CAT meter tracking data"""
    print("IMPORTING CAT METER TRACKING DATA (SAFE TEST)")
    print("=" * 60)
    print("File size: 100 KB (smallest file)")
    print("Purpose: Equipment tracking and calibration")
    print("=" * 60)
    
    # First analyze the file structure
    sheets = analyze_cat_meter_file()
    if not sheets:
        return
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Import the data
        import_cat_meter_data(conn)
        
        # Test the import
        test_equipment_import(conn)
        
        print("\n" + "=" * 60)
        print("CAT METER TRACKING IMPORT COMPLETE!")
        print("This was a safe test with the smallest file.")
        print("Ready to proceed to the next file.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
