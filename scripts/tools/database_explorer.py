#!/usr/bin/env python3
"""
Database Explorer for StreamWatch Data
Simple script to explore and query the SQLite database
"""

import sqlite3
import pandas as pd
import os

def connect_to_database():
    """Connect to the StreamWatch database"""
    db_path = '../database/streamwatch.db'
    if not os.path.exists(db_path):
        print("Database not found! Please run simple_database_import.py first.")
        return None
    
    conn = sqlite3.connect(db_path)
    return conn

def show_database_info(conn):
    """Show basic information about the database"""
    print("STREAMWATCH DATABASE INFORMATION")
    print("=" * 50)
    
    cursor = conn.cursor()
    
    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Tables in database: {len(tables)}")
    for table in tables:
        table_name = table[0]
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n{table_name}:")
        print(f"  Rows: {row_count:,}")
        print(f"  Columns: {len(columns)}")
        print("  Column names:", [col[1] for col in columns])

def explore_sites(conn):
    """Explore sites data"""
    print("\n" + "=" * 50)
    print("SITES DATA")
    print("=" * 50)
    
    # Show all sites
    query = "SELECT * FROM sites LIMIT 10"
    df = pd.read_sql_query(query, conn)
    print(f"First 10 sites:")
    print(df.to_string(index=False))
    
    # Show sites by waterbody
    query = """
    SELECT waterbody, COUNT(*) as site_count 
    FROM sites 
    GROUP BY waterbody 
    ORDER BY site_count DESC
    """
    df = pd.read_sql_query(query, conn)
    print(f"\nSites by waterbody:")
    print(df.to_string(index=False))

def explore_water_quality(conn):
    """Explore water quality data"""
    print("\n" + "=" * 50)
    print("WATER QUALITY DATA")
    print("=" * 50)
    
    # Show parameter summary
    query = """
    SELECT 
        parameter,
        COUNT(*) as measurement_count,
        AVG(value) as avg_value,
        MIN(value) as min_value,
        MAX(value) as max_value,
        unit
    FROM water_quality 
    GROUP BY parameter, unit
    ORDER BY measurement_count DESC
    """
    df = pd.read_sql_query(query, conn)
    print("Parameter summary:")
    print(df.to_string(index=False))
    
    # Show recent measurements
    query = """
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
    LIMIT 20
    """
    df = pd.read_sql_query(query, conn)
    print(f"\nRecent measurements (last 20):")
    print(df.to_string(index=False))

def explore_biological_data(conn):
    """Explore biological data"""
    print("\n" + "=" * 50)
    print("BIOLOGICAL DATA")
    print("=" * 50)
    
    # Show species summary
    query = """
    SELECT 
        taxon,
        COUNT(*) as record_count,
        SUM(count) as total_individuals,
        AVG(dominance) as avg_dominance
    FROM biological_data 
    GROUP BY taxon
    ORDER BY total_individuals DESC
    LIMIT 20
    """
    df = pd.read_sql_query(query, conn)
    print("Top 20 species by total individuals:")
    print(df.to_string(index=False))
    
    # Show diversity by site
    query = """
    SELECT 
        s.site_name,
        s.waterbody,
        COUNT(DISTINCT bd.taxon) as species_count,
        SUM(bd.count) as total_individuals
    FROM biological_data bd
    JOIN sites s ON bd.site_id = s.site_id
    GROUP BY s.site_name, s.waterbody
    ORDER BY species_count DESC
    LIMIT 15
    """
    df = pd.read_sql_query(query, conn)
    print(f"\nBiological diversity by site (top 15):")
    print(df.to_string(index=False))

def run_custom_query(conn):
    """Allow user to run custom queries"""
    print("\n" + "=" * 50)
    print("CUSTOM QUERY")
    print("=" * 50)
    
    print("Available tables: sites, water_quality, biological_data, volunteers, equipment, data_quality_flags")
    print("Example queries:")
    print("- SELECT * FROM sites WHERE waterbody = 'Assunpink Creek'")
    print("- SELECT * FROM water_quality WHERE parameter = 'pH'")
    print("- SELECT * FROM biological_data WHERE taxon LIKE '%mayfly%'")
    
    query = input("\nEnter your SQL query (or 'quit' to exit): ")
    
    if query.lower() == 'quit':
        return
    
    try:
        df = pd.read_sql_query(query, conn)
        print(f"\nQuery results ({len(df)} rows):")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error executing query: {e}")

def export_data(conn):
    """Export data to CSV files"""
    print("\n" + "=" * 50)
    print("EXPORT DATA")
    print("=" * 50)
    
    # Create exports folder
    os.makedirs('../exports/database_exports', exist_ok=True)
    
    # Export main tables
    tables = ['sites', 'water_quality', 'biological_data']
    
    for table in tables:
        try:
            query = f"SELECT * FROM {table}"
            df = pd.read_sql_query(query, conn)
            filename = f'../exports/database_exports/{table}.csv'
            df.to_csv(filename, index=False)
            print(f"Exported {table}: {len(df)} rows to {filename}")
        except Exception as e:
            print(f"Error exporting {table}: {e}")

def main():
    """Main function to explore the database"""
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        while True:
            print("\n" + "=" * 60)
            print("STREAMWATCH DATABASE EXPLORER")
            print("=" * 60)
            print("1. Show database information")
            print("2. Explore sites data")
            print("3. Explore water quality data")
            print("4. Explore biological data")
            print("5. Run custom query")
            print("6. Export data to CSV")
            print("7. Exit")
            
            choice = input("\nSelect an option (1-7): ")
            
            if choice == '1':
                show_database_info(conn)
            elif choice == '2':
                explore_sites(conn)
            elif choice == '3':
                explore_water_quality(conn)
            elif choice == '4':
                explore_biological_data(conn)
            elif choice == '5':
                run_custom_query(conn)
            elif choice == '6':
                export_data(conn)
            elif choice == '7':
                break
            else:
                print("Invalid choice. Please select 1-7.")
    
    finally:
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()
