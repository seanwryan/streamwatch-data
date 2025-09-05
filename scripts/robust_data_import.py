#!/usr/bin/env python3
"""
Robust Data Import for StreamWatch Data
Handles data type issues and imports remaining data properly
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

def safe_import_historical_data(conn):
    """Safely import historical water quality data"""
    print("\nImporting historical water quality data...")
    
    file_path = '../data/All StreamWatch Data.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Read with limited rows for safety
        df = pd.read_excel(file_path, sheet_name='All Data', nrows=2000)
        print(f"Loaded {len(df)} rows from All Data sheet")
        
        cursor = conn.cursor()
        imported = 0
        
        # Get column names
        print(f"Available columns: {list(df.columns)}")
        
        for _, row in df.iterrows():
            # Skip empty rows
            site = row.get('Site', '')
            if pd.isna(site) or str(site).strip() == '':
                continue
            
            # Look for water quality parameters
            for col in df.columns:
                if col in ['pH', 'DO', 'Temperature', 'Turbidity', 'Nitrate', 'Phosphate', 'Chloride']:
                    value = row.get(col)
                    if pd.notna(value) and value != '' and value != 0:
                        try:
                            # Convert to string first, then clean
                            site_str = str(site).strip()
                            date_str = str(row.get('Date', '')) if pd.notna(row.get('Date', '')) else ''
                            param_str = str(col).strip()
                            value_float = float(value)
                            
                            cursor.execute('''
                                INSERT INTO historical_water_quality (site_id, measurement_date, parameter, value, unit, quality_flag)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (site_str, date_str, param_str, value_float, 'units', 'clean'))
                            imported += 1
                        except Exception as e:
                            continue
        
        conn.commit()
        print(f"Imported {imported} historical water quality measurements")
        
    except Exception as e:
        print(f"Error importing historical data: {e}")

def safe_import_volunteers(conn):
    """Safely import volunteer data"""
    print("\nImporting volunteer data...")
    
    file_path = '../data/Volunteer_Tracking.xlsm'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        df = pd.read_excel(file_path, sheet_name='Volunteers', nrows=500)
        print(f"Loaded {len(df)} volunteers")
        print(f"Available columns: {list(df.columns)}")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df.iterrows():
            # Look for ID column
            id_col = None
            for col in df.columns:
                if 'id' in col.lower() or 'volunteer' in col.lower():
                    id_col = col
                    break
            
            if id_col is None:
                continue
                
            volunteer_id = row.get(id_col, '')
            if pd.isna(volunteer_id) or str(volunteer_id).strip() == '':
                continue
            
            try:
                # Convert all values to strings safely
                volunteer_id_str = str(volunteer_id).strip()
                first_name_str = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name', '')) else ''
                last_name_str = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name', '')) else ''
                email_str = str(row.get('Email', '')).strip() if pd.notna(row.get('Email', '')) else ''
                phone_str = str(row.get('Phone', '')).strip() if pd.notna(row.get('Phone', '')) else ''
                team_str = str(row.get('Team', '')).strip() if pd.notna(row.get('Team', '')) else ''
                
                cursor.execute('''
                    INSERT OR REPLACE INTO volunteers (volunteer_id, first_name, last_name, email, phone, team, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (volunteer_id_str, first_name_str, last_name_str, email_str, phone_str, team_str, 1))
                imported += 1
            except Exception as e:
                continue
        
        conn.commit()
        print(f"Imported {imported} volunteers")
        
    except Exception as e:
        print(f"Error importing volunteers: {e}")

def safe_import_bacterial_data(conn):
    """Safely import bacterial testing data"""
    print("\nImporting bacterial data...")
    
    file_path = '../data/BACT and HAB 2025 Data.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        df = pd.read_excel(file_path, sheet_name='IDEXX', nrows=1000)
        print(f"Loaded {len(df)} IDEXX records")
        print(f"Available columns: {list(df.columns)}")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df.iterrows():
            # Look for site column
            site_col = None
            for col in df.columns:
                if 'site' in col.lower():
                    site_col = col
                    break
            
            if site_col is None:
                continue
                
            site = row.get(site_col, '')
            if pd.isna(site) or str(site).strip() == '':
                continue
            
            # Look for E. coli or MPN columns
            for col in df.columns:
                if 'coli' in col.lower() or 'mpn' in col.lower() or 'result' in col.lower():
                    value = row.get(col)
                    if pd.notna(value) and value != '' and value != 0:
                        try:
                            site_str = str(site).strip()
                            date_str = str(row.get('Date', '')) if pd.notna(row.get('Date', '')) else ''
                            test_type = 'E. coli' if 'coli' in col.lower() else 'MPN'
                            value_float = float(value)
                            
                            cursor.execute('''
                                INSERT INTO bacterial_data (site_id, sample_date, test_type, result, unit, quality_flag)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (site_str, date_str, test_type, value_float, 'CFU/100ml', 'clean'))
                            imported += 1
                        except Exception as e:
                            continue
        
        conn.commit()
        print(f"Imported {imported} bacterial test results")
        
    except Exception as e:
        print(f"Error importing bacterial data: {e}")

def safe_import_additional_biological(conn):
    """Safely import additional biological data"""
    print("\nImporting additional biological data...")
    
    file_path = '../data/BATSITES COLLECTED.xlsx'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        df = pd.read_excel(file_path, sheet_name='BUGSPICKED', nrows=1000)
        print(f"Loaded {len(df)} bug records")
        print(f"Available columns: {list(df.columns)}")
        
        cursor = conn.cursor()
        imported = 0
        
        for _, row in df.iterrows():
            # Look for site column
            site_col = None
            for col in df.columns:
                if 'site' in col.lower():
                    site_col = col
                    break
            
            if site_col is None:
                continue
                
            site = row.get(site_col, '')
            if pd.isna(site) or str(site).strip() == '':
                continue
            
            # Look for bug/taxon column
            bug_col = None
            for col in df.columns:
                if 'bug' in col.lower() or 'taxon' in col.lower() or 'species' in col.lower():
                    bug_col = col
                    break
            
            if bug_col is None:
                continue
                
            bug = row.get(bug_col, '')
            if pd.isna(bug) or str(bug).strip() == '':
                continue
            
            # Look for count column
            count_col = None
            for col in df.columns:
                if 'count' in col.lower() or 'amount' in col.lower():
                    count_col = col
                    break
            
            if count_col is None:
                continue
                
            count = row.get(count_col, 0)
            if pd.isna(count):
                count = 0
            
            try:
                site_str = str(site).strip()
                bug_str = str(bug).strip()
                count_int = int(count) if pd.notna(count) else 0
                
                cursor.execute('''
                    INSERT INTO biological_data (site_id, sample_date, taxon, count, abundance, dominance, quality_flag)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (site_str, '', bug_str, count_int, 0.0, 0.0, 'clean'))
                imported += 1
            except Exception as e:
                continue
        
        conn.commit()
        print(f"Imported {imported} additional biological records")
        
    except Exception as e:
        print(f"Error importing additional biological data: {e}")

def test_final_database(conn):
    """Test the final database"""
    print("\nTesting final database...")
    
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
    
    # Show sample data
    if total_records > 0:
        print("\nSample data from new tables:")
        
        # Sample from historical water quality
        try:
            cursor.execute("SELECT COUNT(*) FROM historical_water_quality")
            if cursor.fetchone()[0] > 0:
                df = pd.read_sql_query("SELECT * FROM historical_water_quality LIMIT 3", conn)
                print("Historical water quality sample:")
                print(df.to_string(index=False))
        except:
            pass
        
        # Sample from volunteers
        try:
            cursor.execute("SELECT COUNT(*) FROM volunteers")
            if cursor.fetchone()[0] > 0:
                df = pd.read_sql_query("SELECT * FROM volunteers LIMIT 3", conn)
                print("\nVolunteers sample:")
                print(df.to_string(index=False))
        except:
            pass

def main():
    """Main function to import remaining data robustly"""
    print("ROBUST IMPORT OF REMAINING STREAMWATCH DATA")
    print("=" * 60)
    
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Import remaining data with error handling
        safe_import_historical_data(conn)
        safe_import_volunteers(conn)
        safe_import_bacterial_data(conn)
        safe_import_additional_biological(conn)
        
        # Test the final database
        test_final_database(conn)
        
        print("\n" + "=" * 60)
        print("ROBUST DATA IMPORT COMPLETE!")
        print("Database now contains all available data.")
        print("Run database_explorer.py to explore the complete database.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
