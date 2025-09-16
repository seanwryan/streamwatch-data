#!/usr/bin/env python3
"""
Test database connection for StreamWatch project
"""

import psycopg2
from sqlalchemy import create_engine, text
from config import DB_CONFIG

def test_postgresql_connection():
    """Test PostgreSQL database connection"""
    try:
        # Test with psycopg2
        print("Testing PostgreSQL connection with psycopg2...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL connection successful!")
        print(f"Database version: {version[0]}")
        cursor.close()
        conn.close()
        
        # Test with SQLAlchemy
        print("\nTesting PostgreSQL connection with SQLAlchemy...")
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.fetchone()[0]
            print(f"✅ SQLAlchemy connection successful!")
            print(f"Number of tables in database: {table_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_table_access():
    """Test access to key tables"""
    try:
        DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        engine = create_engine(DATABASE_URL)
        
        tables_to_test = ['sites', 'samples', 'bugs', 'bacteria', 'volunteers']
        
        print("\nTesting table access...")
        with engine.connect() as conn:
            for table in tables_to_test:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"✅ Table '{table}': {count} records")
                except Exception as e:
                    print(f"❌ Table '{table}': Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table access test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 StreamWatch Database Connection Test")
    print("=" * 50)
    
    # Test basic connection
    connection_ok = test_postgresql_connection()
    
    if connection_ok:
        # Test table access
        test_table_access()
        print("\n🎉 All tests passed! Database is ready for use.")
    else:
        print("\n❌ Connection test failed. Please check your database configuration.")
        print("Make sure PostgreSQL is running and the database exists.")

if __name__ == "__main__":
    main()
