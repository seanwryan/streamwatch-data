#!/usr/bin/env python3
"""
Test edit user connection for StreamWatch project
"""

import psycopg2
from sqlalchemy import create_engine, text

def test_edit_connection():
    """Test edit user connection to Neon database"""
    try:
        # Test with edit user credentials
        print("Testing edit user connection...")
        conn = psycopg2.connect(
            host='ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech',
            port=5432,
            database='neondb',
            user='streamwatch_edit',
            password='streamwatch_edit_2024',
            sslmode='require'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Edit user connection successful!")
        print(f"Database version: {version[0]}")
        
        # Test write permissions by creating a test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_permissions (
                id SERIAL PRIMARY KEY,
                test_data VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO test_permissions (test_data) VALUES ('Edit access test')")
        
        # Read test data
        cursor.execute("SELECT * FROM test_permissions WHERE test_data = 'Edit access test'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Write permissions confirmed - can create tables and insert data")
            print(f"Test record: {result}")
        
        # Clean up test table
        cursor.execute("DROP TABLE test_permissions")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Edit user connection failed: {e}")
        return False

def test_readonly_connection():
    """Test readonly user connection to Neon database"""
    try:
        # Test with readonly user credentials
        print("\nTesting readonly user connection...")
        conn = psycopg2.connect(
            host='ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech',
            port=5432,
            database='neondb',
            user='streamwatch_readonly',
            password='streamwatch_readonly_2024',
            sslmode='require'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Readonly user connection successful!")
        print(f"Database version: {version[0]}")
        
        # Test read permissions
        cursor.execute("SELECT COUNT(*) FROM sites")
        count = cursor.fetchone()[0]
        print(f"✅ Read permissions confirmed - can access sites table ({count} records)")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Readonly user connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 StreamWatch Database User Access Test")
    print("=" * 50)
    
    # Test edit user
    edit_ok = test_edit_connection()
    
    # Test readonly user
    readonly_ok = test_readonly_connection()
    
    if edit_ok and readonly_ok:
        print("\n🎉 All user access tests passed!")
        print("\n📋 User Credentials Summary:")
        print("=" * 30)
        print("EDIT USER (Full Access):")
        print("  Username: streamwatch_edit")
        print("  Password: streamwatch_edit_2024")
        print("  Permissions: Read, Write, Create, Delete")
        print("\nREADONLY USER (View Only):")
        print("  Username: streamwatch_readonly")
        print("  Password: streamwatch_readonly_2024")
        print("  Permissions: Read only")
    else:
        print("\n❌ Some user access tests failed. Please check the configuration.")

if __name__ == "__main__":
    main()
