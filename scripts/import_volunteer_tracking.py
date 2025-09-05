#!/usr/bin/env python3
"""
Import Volunteer Tracking Data
Safely imports Volunteer_Tracking.xlsm (9.3 MB) - volunteer management data
This is a large file, so we'll process it very carefully in small chunks
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

def analyze_volunteer_file():
    """First, let's analyze the Volunteer Tracking file structure"""
    print("ANALYZING VOLUNTEER TRACKING FILE")
    print("=" * 50)
    
    file_path = '../data/Volunteer_Tracking.xlsm'
    if not os.path.exists(file_path):
        print("File not found!")
        return None
    
    try:
        # Get sheet names first
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        # Analyze each sheet (limit to first 3 sheets for safety)
        for sheet_name in xl_file.sheet_names[:3]:
            print(f"\n--- Sheet: {sheet_name} ---")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)  # Just first 10 rows
                print(f"Columns: {list(df.columns)}")
                print(f"Shape: {df.shape}")
                print("Sample data:")
                print(df.head(3).to_string(index=False))
                print("-" * 40)
            except Exception as e:
                print(f"Error reading sheet {sheet_name}: {e}")
                continue
        
        if len(xl_file.sheet_names) > 3:
            print(f"\n... and {len(xl_file.sheet_names) - 3} more sheets")
        
        return xl_file.sheet_names
        
    except Exception as e:
        print(f"Error analyzing file: {e}")
        return None

def import_volunteer_data_safely(conn):
    """Import volunteer data very safely in small chunks"""
    print("\nIMPORTING VOLUNTEER TRACKING DATA (SAFE MODE)")
    print("=" * 50)
    
    file_path = '../data/Volunteer_Tracking.xlsm'
    if not os.path.exists(file_path):
        print("File not found!")
        return
    
    try:
        # Get sheet names
        xl_file = pd.ExcelFile(file_path)
        print(f"Available sheets: {xl_file.sheet_names}")
        
        cursor = conn.cursor()
        total_volunteers_imported = 0
        total_assignments_imported = 0
        
        # Process only the first 3 sheets for safety
        for sheet_name in xl_file.sheet_names[:3]:
            print(f"\nProcessing sheet: {sheet_name}")
            
            try:
                # Read the sheet with very limited rows for safety
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=500)
                print(f"Loaded {len(df)} rows from {sheet_name}")
                print(f"Columns: {list(df.columns)}")
                
                # Skip empty sheets
                if len(df) == 0:
                    print("Sheet is empty, skipping...")
                    continue
                
                # Determine if this is volunteer or assignment data
                is_volunteer_data = any(keyword in sheet_name.lower() for keyword in ['volunteer', 'contact', 'info'])
                is_assignment_data = any(keyword in sheet_name.lower() for keyword in ['assignment', 'schedule', 'site'])
                
                # Import volunteer data
                if is_volunteer_data:
                    imported = 0
                    for _, row in df.iterrows():
                        # Skip empty rows
                        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                            continue
                        
                        try:
                            # Extract volunteer information
                            volunteer_id = ''
                            first_name = ''
                            last_name = ''
                            email = ''
                            phone = ''
                            team = ''
                            active = 1
                            training_date = ''
                            
                            # Try to extract information from available columns
                            for i, col in enumerate(df.columns):
                                col_str = str(col).lower()
                                if 'id' in col_str and 'volunteer' in col_str:
                                    volunteer_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'first' in col_str and 'name' in col_str:
                                    first_name = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'last' in col_str and 'name' in col_str:
                                    last_name = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'email' in col_str:
                                    email = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'phone' in col_str:
                                    phone = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'team' in col_str:
                                    team = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'training' in col_str and 'date' in col_str:
                                    training_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                                elif 'active' in col_str or 'status' in col_str:
                                    active_val = str(row.iloc[i]).strip().lower() if pd.notna(row.iloc[i]) else 'yes'
                                    active = 1 if active_val in ['yes', 'active', '1', 'true'] else 0
                            
                            # If no volunteer_id found, try to create one from name
                            if not volunteer_id and (first_name or last_name):
                                volunteer_id = f"{first_name}_{last_name}".replace(' ', '_')
                            
                            # Only import if we have meaningful data
                            if volunteer_id and (first_name or last_name or email):
                                # Insert into volunteers table
                                cursor.execute('''
                                    INSERT OR REPLACE INTO volunteers 
                                    (volunteer_id, first_name, last_name, email, phone, team, active, training_date)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (volunteer_id, first_name, last_name, email, phone, team, active, training_date))
                                
                                imported += 1
                            
                        except Exception as e:
                            print(f"Error importing volunteer row: {e}")
                            continue
                    
                    print(f"Imported {imported} volunteers from {sheet_name}")
                    total_volunteers_imported += imported
                
                # Import assignment data
                elif is_assignment_data:
                    imported = 0
                    for _, row in df.iterrows():
                        # Skip empty rows
                        if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                            continue
                        
                        try:
                            # Extract assignment information
                            volunteer_id = ''
                            site_id = ''
                            assignment_date = ''
                            assignment_type = 'Monitoring'
                            status = 'Scheduled'
                            notes = ''
                            
                            # Try to extract information from available columns
                            for i, col in enumerate(df.columns):
                                col_str = str(col).lower()
                                if 'volunteer' in col_str and 'id' in col_str:
                                    volunteer_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'site' in col_str and 'id' in col_str:
                                    site_id = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                                elif 'date' in col_str:
                                    assignment_date = str(row.iloc[i]) if pd.notna(row.iloc[i]) else ''
                                elif 'type' in col_str:
                                    assignment_type = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'Monitoring'
                                elif 'status' in col_str:
                                    status = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else 'Scheduled'
                                elif 'note' in col_str or 'comment' in col_str:
                                    notes = str(row.iloc[i]).strip() if pd.notna(row.iloc[i]) else ''
                            
                            # Only import if we have meaningful data
                            if volunteer_id and site_id:
                                # Insert into volunteer assignments table
                                cursor.execute('''
                                    INSERT INTO volunteer_assignments 
                                    (volunteer_id, site_id, assignment_date, assignment_type, status, notes)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (volunteer_id, site_id, assignment_date, assignment_type, status, notes))
                                
                                imported += 1
                            
                        except Exception as e:
                            print(f"Error importing assignment row: {e}")
                            continue
                    
                    print(f"Imported {imported} assignments from {sheet_name}")
                    total_assignments_imported += imported
                
                # If neither volunteer nor assignment, try to import as general data
                else:
                    print(f"Sheet {sheet_name} doesn't match volunteer or assignment patterns, skipping...")
                
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {e}")
                continue
        
        conn.commit()
        print(f"\nTotal volunteers imported: {total_volunteers_imported}")
        print(f"Total assignments imported: {total_assignments_imported}")
        
    except Exception as e:
        print(f"Error importing volunteer data: {e}")

def test_volunteer_import(conn):
    """Test the volunteer import"""
    print("\nTESTING VOLUNTEER IMPORT")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    try:
        # Count volunteer records
        cursor.execute("SELECT COUNT(*) FROM volunteers")
        volunteer_count = cursor.fetchone()[0]
        print(f"Total volunteers: {volunteer_count}")
        
        # Count assignment records
        cursor.execute("SELECT COUNT(*) FROM volunteer_assignments")
        assignment_count = cursor.fetchone()[0]
        print(f"Total assignments: {assignment_count}")
        
        if volunteer_count > 0:
            # Show sample volunteer data
            df = pd.read_sql_query("SELECT * FROM volunteers LIMIT 5", conn)
            print("\nSample volunteer data:")
            print(df.to_string(index=False))
            
            # Show active volunteers
            cursor.execute("SELECT COUNT(*) FROM volunteers WHERE active = 1")
            active_count = cursor.fetchone()[0]
            print(f"\nActive volunteers: {active_count}")
        
        if assignment_count > 0:
            # Show sample assignment data
            df = pd.read_sql_query("SELECT * FROM volunteer_assignments LIMIT 5", conn)
            print("\nSample assignment data:")
            print(df.to_string(index=False))
            
            # Show assignment types
            cursor.execute("SELECT assignment_type, COUNT(*) FROM volunteer_assignments GROUP BY assignment_type")
            types = cursor.fetchall()
            print(f"\nAssignment types:")
            for assign_type, count in types:
                print(f"  {assign_type}: {count} records")
        
    except Exception as e:
        print(f"Error testing volunteer import: {e}")

def main():
    """Main function to import volunteer tracking data"""
    print("IMPORTING VOLUNTEER TRACKING DATA (SAFE MODE)")
    print("=" * 60)
    print("File size: 9.3 MB (largest remaining file)")
    print("Purpose: Volunteer management and site assignments")
    print("Processing in SAFE MODE with limited rows")
    print("=" * 60)
    
    # First analyze the file structure
    sheets = analyze_volunteer_file()
    if not sheets:
        return
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Import the data safely
        import_volunteer_data_safely(conn)
        
        # Test the import
        test_volunteer_import(conn)
        
        print("\n" + "=" * 60)
        print("VOLUNTEER TRACKING IMPORT COMPLETE!")
        print("This was a safe test with the largest file.")
        print("Ready to proceed to the final file.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
