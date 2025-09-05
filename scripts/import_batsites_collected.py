#!/usr/bin/env python3
"""
Import BATSITES COLLECTED Data
Safely imports BATSITES COLLECTED.xlsx (348 KB) - biological assessment data
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

def analyze_batsites_file():
    """First, let's analyze the BATSITES COLLECTED file structure"""
    print("ANALYZING BATSITES COLLECTED FILE")
    print("=" * 50)
    
    file_path = '../data/BATSITES COLLECTED.xlsx'
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

def import_batsites_data(conn):
    """Import BATSITES collected data"""
    print("\nIMPORTING BATSITES COLLECTED DATA")
    print("=" * 50)
    
    file_path = '../data/BATSITES COLLECTED.xlsx'
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
                
                # Import biological data
                imported = 0
                for _, row in df.iterrows():
                    # Skip empty rows
                    if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                        continue
                    
                    try:
                        # Extract biological information
                        site_id = ''
                        sample_date = ''
                        taxon = ''
                        count = 0
                        abundance = 0.0
                        dominance = 0.0
                        quality_flag = 'clean'
                        
                        # Try to extract information from available columns
                        for i, col in enumerate(df.columns):
                            col_str = str(col).lower()
                            if 'site' in col_str or 'station' in col_str:
                                site_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            elif 'date' in col_str:
                                sample_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                            elif 'bug' in col_str or 'taxon' in col_str or 'species' in col_str or 'family' in col_str:
                                taxon = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            elif 'count' in col_str or 'amount' in col_str or 'number' in col_str:
                                try:
                                    count = int(row.iloc[i]) if pd.notna(row.iloc[i]) else 0
                                except (ValueError, TypeError):
                                    count = 0
                            elif 'abundance' in col_str:
                                try:
                                    abundance = float(row.iloc[i]) if pd.notna(row.iloc[i]) else 0.0
                                except (ValueError, TypeError):
                                    abundance = 0.0
                            elif 'dominance' in col_str:
                                try:
                                    dominance = float(row.iloc[i]) if pd.notna(row.iloc[i]) else 0.0
                                except (ValueError, TypeError):
                                    dominance = 0.0
                        
                        # If no taxon found, try to use the first non-empty column
                        if not taxon:
                            for i, col in enumerate(df.columns):
                                if pd.notna(row.iloc[i]) and str(row.iloc[i]).strip() != '':
                                    taxon = str(row.iloc[i]).strip()
                                    break
                        
                        # If no site_id found, try to extract from other columns
                        if not site_id:
                            for i, col in enumerate(df.columns):
                                if pd.notna(row.iloc[i]) and str(row.iloc[i]).strip() != '':
                                    potential_site = str(row.iloc[i]).strip()
                                    # Check if it looks like a site code (2-4 characters, alphanumeric)
                                    if len(potential_site) <= 4 and potential_site.isalnum():
                                        site_id = potential_site
                                        break
                        
                        # Only import if we have meaningful data
                        if site_id or taxon or count > 0:
                            # Insert into database
                            cursor.execute('''
                                INSERT INTO biological_data 
                                (site_id, sample_date, taxon, count, abundance, dominance, quality_flag)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            ''', (site_id, sample_date, taxon, count, abundance, dominance, quality_flag))
                            
                            imported += 1
                        
                    except Exception as e:
                        print(f"Error importing row: {e}")
                        continue
                
                print(f"Imported {imported} biological records from {sheet_name}")
                total_imported += imported
                
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                continue
        
        conn.commit()
        print(f"\nTotal biological records imported: {total_imported}")
        
    except Exception as e:
        print(f"Error importing BATSITES data: {e}")

def test_batsites_import(conn):
    """Test the BATSITES import"""
    print("\nTESTING BATSITES IMPORT")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    try:
        # Count biological records
        cursor.execute("SELECT COUNT(*) FROM biological_data")
        count = cursor.fetchone()[0]
        print(f"Total biological records: {count}")
        
        if count > 0:
            # Show sample data
            df = pd.read_sql_query("SELECT * FROM biological_data ORDER BY id DESC LIMIT 5", conn)
            print("\nLatest biological data:")
            print(df.to_string(index=False))
            
            # Show unique taxa
            cursor.execute("SELECT COUNT(DISTINCT taxon) FROM biological_data WHERE taxon != ''")
            unique_taxa = cursor.fetchone()[0]
            print(f"\nUnique taxa: {unique_taxa}")
            
            # Show site distribution
            cursor.execute("SELECT site_id, COUNT(*) FROM biological_data WHERE site_id != '' GROUP BY site_id ORDER BY COUNT(*) DESC LIMIT 10")
            sites = cursor.fetchall()
            print(f"\nTop sites by biological records:")
            for site, count in sites:
                print(f"  {site}: {count} records")
        
    except Exception as e:
        print(f"Error testing BATSITES import: {e}")

def main():
    """Main function to import BATSITES collected data"""
    print("IMPORTING BATSITES COLLECTED DATA (SAFE TEST)")
    print("=" * 60)
    print("File size: 348 KB (next smallest file)")
    print("Purpose: Biological assessment and bug collection data")
    print("=" * 60)
    
    # First analyze the file structure
    sheets = analyze_batsites_file()
    if not sheets:
        return
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Import the data
        import_batsites_data(conn)
        
        # Test the import
        test_batsites_import(conn)
        
        print("\n" + "=" * 60)
        print("BATSITES COLLECTED IMPORT COMPLETE!")
        print("This was another safe test with a small file.")
        print("Ready to proceed to the next file.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
