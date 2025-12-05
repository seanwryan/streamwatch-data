#!/usr/bin/env python3
"""
Generate a report of the current database structure
Lists all tables, columns, data types, and row counts.
"""

import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import DB_CONFIG

def generate_report():
    try:
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        print("# StreamWatch Database Schema Report\n")
        
        with engine.connect() as conn:
            # Get list of tables
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = conn.execute(tables_query).fetchall()
            
            print(f"**Total Tables:** {len(tables)}\n")
            
            for table in tables:
                table_name = table[0]
                print(f"## Table: `{table_name}`")
                
                # Get Row Count
                try:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                    print(f"**Rows:** {count}\n")
                except:
                    print("**Rows:** (Error calculating)\n")
                
                # Get Columns
                columns_query = text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """)
                columns = conn.execute(columns_query).fetchall()
                
                print("| Column | Type | Nullable |")
                print("| :--- | :--- | :--- |")
                for col in columns:
                    print(f"| {col[0]} | {col[1]} | {col[2]} |")
                print("\n")
                
            # Check Views
            views_query = text("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            views = conn.execute(views_query).fetchall()
            
            if views:
                print("# Views\n")
                for view in views:
                    print(f"- `{view[0]}`")
                print("\n")

    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    generate_report()
