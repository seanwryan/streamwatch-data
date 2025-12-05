
import psycopg2
from sqlalchemy import create_engine, text
import sys
import os

# Add parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import DB_CONFIG

def verify():
    try:
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}?sslmode={DB_CONFIG['sslmode']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("--- Verification Results ---")
            
            # 1. Sites Count
            count = conn.execute(text("SELECT COUNT(*) FROM sites")).scalar()
            print(f"Sites Count: {count}")
            
            # 2. Municipalities Count
            m_count = conn.execute(text("SELECT COUNT(*) FROM municipalities")).scalar()
            print(f"Municipalities Count: {m_count}")
            
            # 3. Volunteers linked
            v_linked = conn.execute(text("SELECT COUNT(*) FROM volunteers WHERE municipality_id IS NOT NULL")).scalar()
            print(f"Volunteers Linked to Municipality: {v_linked}")
            
            # 4. Check Status Constraints (should be no Unknown/Invalid if loader worked well, or at least standardized)
            print("\nStatus Distribution:")
            statuses = conn.execute(text("SELECT cat_status, COUNT(*) FROM sites GROUP BY cat_status")).fetchall()
            for s in statuses:
                print(f" - {s[0]}: {s[1]}")
                
            # 5. Check View
            print("\nChecking sites_view...")
            view_row = conn.execute(text("SELECT * FROM sites_view LIMIT 1")).fetchone()
            if view_row:
                print(" - View is queryable. Sample row returned.")
            else:
                print(" - View is empty.")
                
            return True
            
    except Exception as e:
        print(f"Verification Failed: {e}")
        return False

if __name__ == "__main__":
    verify()
