#!/usr/bin/env python3
"""
Import 2024 TWI WQX Submission Data
Safely imports 2024 TWI WQX Submission.xlsx (1.5 MB) - regulatory submission data
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

def analyze_wqx_file():
    """First, let's analyze the WQX Submission file structure"""
    print("ANALYZING WQX SUBMISSION FILE")
    print("=" * 50)
    
    file_path = '../data/2024 TWI WQX Submission.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return None
    
    try:
        # Get sheet names first
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Analyze each sheet (limit to first 5 sheets for safety)
        for sheet_name in xl_file.sheet_names[:5]:
            print(f"\n--- Sheet: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)  # Just first 10 rows
            print(f"Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
            print("Sample data:")
            print(df.head(3).to_string(index=False))
            print("-" * 40)
        
        if len(xl_file.sheet_names) > 5:
            print(f"\n... and {len(xl_file.sheet_names) - 5} more sheets")
        
        return xl_file.sheet_names
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return None

def import_wqx_data(conn):
    """Import WQX submission data"""
    print("\nIMPORTING WQX SUBMISSION DATA")
    print("=" * 50)
    
    file_path = '../data/2024 TWI WQX Submission.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Get sheet names
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        cursor = conn.cursor()
        total_imported = 0
        
        # Import from each sheet (limit to first 5 sheets for safety)
        for sheet_name in xl_file.sheet_names[:5]:
            print(f"\nProcessing sheet: {sheet_name}")
            
            try:
                # Read the sheet with limited rows for safety
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1000)
                print(f"Loaded {len(df)} rows from {sheet_name}")
                print(f"Columns: {list(df.columns)}")
                
                # Skip empty sheets
                if len(df) == 0:
                    print("Sheet is empty, skipping...")
                    continue
                
                # Import regulatory data
                imported = 0
                for _, row in df.iterrows():
                    # Skip empty rows
                    if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                        continue
                    
                    try:
                        # Extract regulatory information
                        site_id = ''
                        measurement_date = ''
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
                                measurement_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                            elif 'parameter' in col_str or 'analyte' in col_str or 'constituent' in col_str:
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
                        
                        # If no parameter found, try to use column names
                        if not parameter:
                            for i, col in enumerate(df.columns):
                                if pd.notna(row.iloc[i]) and str(row.iloc[i]).strip() != '':
                                    # Check if column name looks like a parameter
                                    col_str = str(col).lower()
                                    if any(keyword in col_str for keyword in ['ph', 'do', 'temp', 'turb', 'nitrate', 'phosphate', 'chloride']):
                                        parameter = str(col).strip()
                                        try:
                                            value = float(row.iloc[i]) if pd.notna(row.iloc[i]) else 0.0
                                        except (ValueError, TypeError):
                                            value = 0.0
                                        break
                        
                        # Only import if we have meaningful data
                        if site_id and (parameter or value > 0):
                            # Insert into historical water quality table
                            cursor.execute('''
                                INSERT INTO historical_water_quality 
                                (site_id, measurement_date, parameter, value, unit, method, quality_flag, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (site_id, measurement_date, parameter, value, unit, method, quality_flag, notes))
                            
                            imported += 1
                        
                    except Exception as e:
                        print(f"Error importing row: {e}")
                        continue
                
                print(f"Imported {imported} regulatory records from {sheet_name}")
                total_imported += imported
                
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                continue
        
        conn.commit()
        print(f"\nTotal regulatory records imported: {total_imported}")
        
    except Exception as e:
        print(f"Error importing WQX data: {e}")

def test_wqx_import(conn):
    """Test the WQX import"""
    print("\nTESTING WQX IMPORT")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    try:
        # Count historical water quality records
        cursor.execute("SELECT COUNT(*) FROM historical_water_quality")
        count = cursor.fetchone()[0]
        print(f"Total historical water quality records: {count}")
        
        if count > 0:
            # Show sample data
            df = pd.read_sql_query("SELECT * FROM historical_water_quality ORDER BY id DESC LIMIT 5", conn)
            print("\nLatest historical water quality data:")
            print(df.to_string(index=False))
            
            # Show parameter distribution
            cursor.execute("SELECT parameter, COUNT(*) FROM historical_water_quality WHERE parameter != '' GROUP BY parameter ORDER BY COUNT(*) DESC LIMIT 10")
            params = cursor.fetchall()
            print(f"\nTop parameters:")
            for param, count in params:
                print(f"  {param}: {count} records")
        
    except Exception as e:
        print(f"Error testing WQX import: {e}")

def main():
    """Main function to import WQX submission data"""
    print("IMPORTING WQX SUBMISSION DATA (SAFE TEST)")
    print("=" * 60)
    print("File size: 1.5 MB (next smallest file)")
    print("Purpose: Regulatory submission data for DEP WQX")
    print("=" * 60)
    
    # First analyze the file structure
    sheets = analyze_wqx_file()
    if not sheets:
        return
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Import the data
        import_wqx_data(conn)
        
        # Test the import
        test_wqx_import(conn)
        
        print("\n" + "=" * 60)
        print("WQX SUBMISSION IMPORT COMPLETE!")
        print("This was another safe test with a medium-sized file.")
        print("Ready to proceed to the next file.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
