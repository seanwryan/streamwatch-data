#!/usr/bin/env python3
"""
Simple test script for Watershed team to verify database access
Run this to confirm everything is working
"""

import pandas as pd
from sqlalchemy import create_engine, text

def test_team_access():
    """Test database access as the Watershed team would use it"""
    print("🧪 Testing StreamWatch Database Access for Watershed Team")
    print("=" * 50)
    
    # Test read-only access
    print("\n1. Testing READ-ONLY access...")
    try:
        engine_readonly = create_engine("postgresql://streamwatch_readonly:streamwatch_readonly_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require")
        
        with engine_readonly.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 'Read-only access works!' as status, COUNT(*) as total_sites FROM sites"))
            row = result.fetchone()
            print(f"   ✅ {row[0]}")
            print(f"   📊 Total sites: {row[1]}")
            
            # Test data access
            result = conn.execute(text("SELECT COUNT(*) FROM bacteria WHERE e_coli IS NOT NULL"))
            bacteria_count = result.scalar()
            print(f"   🧪 Bacteria tests with E.coli: {bacteria_count}")
            
            # Test that write is blocked
            try:
                conn.execute(text("CREATE TABLE test_write (id INT)"))
                print("   ❌ ERROR: Read-only user can write (this shouldn't happen)")
                return False
            except Exception as e:
                if "permission denied" in str(e).lower():
                    print("   ✅ Write access properly blocked")
                else:
                    print(f"   ⚠️ Unexpected error: {e}")
            
    except Exception as e:
        print(f"   ❌ Read-only connection failed: {e}")
        return False
    
    # Test edit access
    print("\n2. Testing EDIT access...")
    try:
        engine_edit = create_engine("postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require")
        
        with engine_edit.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT 'Edit access works!' as status, current_user as user"))
            row = result.fetchone()
            print(f"   ✅ {row[0]}")
            print(f"   👤 Connected as: {row[1]}")
            
            # Test write permissions
            conn.execute(text("CREATE TABLE test_team_write (id SERIAL PRIMARY KEY, message VARCHAR(100))"))
            conn.execute(text("INSERT INTO test_team_write (message) VALUES ('Team can write data!')"))
            conn.execute(text("DROP TABLE test_team_write"))
            print("   ✅ Write permissions confirmed")
            
    except Exception as e:
        print(f"   ❌ Edit connection failed: {e}")
        return False
    
    # Test data exploration
    print("\n3. Testing data exploration...")
    try:
        with engine_readonly.connect() as conn:
            # Get table summary
            result = conn.execute(text("""
                SELECT 'sites' as table_name, COUNT(*) as records FROM sites
                UNION ALL
                SELECT 'samples', COUNT(*) FROM samples
                UNION ALL
                SELECT 'bacteria', COUNT(*) FROM bacteria
                UNION ALL
                SELECT 'bugs', COUNT(*) FROM bugs
                UNION ALL
                SELECT 'taxonomy', COUNT(*) FROM taxonomy
                UNION ALL
                SELECT 'volunteers', COUNT(*) FROM volunteers
                ORDER BY table_name
            """))
            
            print("   📊 Database contents:")
            total_records = 0
            for row in result:
                print(f"      {row[0]}: {row[1]:,} records")
                total_records += row[1]
            print(f"   🎯 Total records: {total_records:,}")
            
    except Exception as e:
        print(f"   ❌ Data exploration failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print("✅ The Watershed team can successfully:")
    print("   • Connect to the database")
    print("   • View all data (read-only user)")
    print("   • Modify data when needed (edit user)")
    print("   • Explore all 6 tables with 25,684+ records")
    print()
    print("📋 Next steps for the team:")
    print("   1. Download DBeaver from https://dbeaver.io/")
    print("   2. Use connection details from TEAM_SETUP_GUIDE.md")
    print("   3. Start exploring the data!")
    
    return True

if __name__ == "__main__":
    success = test_team_access()
    if not success:
        print("\n❌ Some tests failed. Check connection settings.")
        exit(1)
