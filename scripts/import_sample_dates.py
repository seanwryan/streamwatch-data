#!/usr/bin/env python3
"""
Import Sample Dates Data
Safely imports tblSampleDates.xlsx (384 KB) - sample tracking data
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

def analyze_sample_dates_file():
    """First, let's analyze the tblSampleDates file structure"""
    print("ANALYZING SAMPLE DATES FILE")
    print("=" * 50)
    
    file_path = '../data/tblSampleDates.xlsx'
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

def import_sample_dates_data(conn):
    """Import sample dates tracking data"""
    print("\nIMPORTING SAMPLE DATES DATA")
    print("=" * 50)
    
    file_path = '../data/tblSampleDates.xlsx'
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
                
                # Import sample tracking data
                imported = 0
                for _, row in df.iterrows():
                    # Skip empty rows
                    if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                        continue
                    
                    try:
                        # Extract sample information
                        sample_id = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
                        site_id = ''
                        collection_date = ''
                        sample_type = 'Unknown'
                        processing_date = ''
                        status = 'Collected'
                        notes = ''
                        
                        # Try to extract more information from available columns
                        for i, col in enumerate(df.columns):
                            col_str = str(col).lower()
                            if 'site' in col_str:
                                site_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            elif 'date' in col_str and 'collect' in col_str:
                                collection_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                            elif 'date' in col_str and 'process' in col_str:
                                processing_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                            elif 'type' in col_str:
                                sample_type = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'Unknown'
                            elif 'status' in col_str or 'condition' in col_str:
                                status = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'Collected'
                            elif 'note' in col_str or 'comment' in col_str:
                                notes = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                        
                        # If no site_id found, try to extract from sample_id
                        if not site_id and sample_id:
                            # Try to extract site from sample code (e.g., "AC1_2024_01" -> "AC1")
                            if '_' in sample_id:
                                site_id = sample_id.split('_')[0]
                            elif len(sample_id) >= 3:
                                site_id = sample_id[:3]  # First 3 characters
                        
                        # Insert into database
                        cursor.execute('''
                            INSERT INTO sample_tracking 
                            (sample_id, site_id, collection_date, sample_type, processing_date, status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (sample_id, site_id, collection_date, sample_type, processing_date, status, notes))
                        
                        imported += 1
                        
                    except Exception as e:
                        print(f"Error importing row: {e}")
                        continue
                
                print(f"Imported {imported} sample records from {sheet_name}")
                total_imported += imported
                
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                continue
        
        conn.commit()
        print(f"\nTotal sample records imported: {total_imported}")
        
    except Exception as e:
        print(f"Error importing sample dates data: {e}")

def test_sample_import(conn):
    """Test the sample import"""
    print("\nTESTING SAMPLE IMPORT")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    try:
        # Count sample records
        cursor.execute("SELECT COUNT(*) FROM sample_tracking")
        count = cursor.fetchone()[0]
        print(f"Total sample records: {count}")
        
        if count > 0:
            # Show sample data
            df = pd.read_sql_query("SELECT * FROM sample_tracking LIMIT 5", conn)
            print("\nSample tracking data:")
            print(df.to_string(index=False))
            
            # Show sample types
            cursor.execute("SELECT sample_type, COUNT(*) FROM sample_tracking GROUP BY sample_type")
            types = cursor.fetchall()
            print(f"\nSample types:")
            for sample_type, count in types:
                print(f"  {sample_type}: {count} records")
            
            # Show status distribution
            cursor.execute("SELECT status, COUNT(*) FROM sample_tracking GROUP BY status")
            statuses = cursor.fetchall()
            print(f"\nSample statuses:")
            for status, count in statuses:
                print(f"  {status}: {count} records")
        
    except Exception as e:
        print(f"Error testing sample import: {e}")

def main():
    """Main function to import sample dates data"""
    print("IMPORTING SAMPLE DATES DATA (SAFE TEST)")
    print("=" * 60)
    print("File size: 384 KB (next smallest file)")
    print("Purpose: Sample collection and processing tracking")
    print("=" * 60)
    
    # First analyze the file structure
    sheets = analyze_sample_dates_file()
    if not sheets:
        return
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Import the data
        import_sample_dates_data(conn)
        
        # Test the import
        test_sample_import(conn)
        
        print("\n" + "=" * 60)
        print("SAMPLE DATES IMPORT COMPLETE!")
        print("This was another safe test with a small file.")
        print("Ready to proceed to the next file.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
