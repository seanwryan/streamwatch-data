#!/usr/bin/env python3
"""
Audit volunteer data in the database
Provides a comprehensive report on data quality and completeness
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text
import pandas as pd

# Using edit credentials to access new tables
DATABASE_URL = "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"

def audit_volunteers():
    """Audit volunteer data and generate report"""
    print("🔍 StreamWatch Volunteer Data Audit")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # 1. Basic counts
        print("\n📊 BASIC STATISTICS")
        print("-" * 60)
        
        total = conn.execute(text("SELECT COUNT(*) FROM volunteers")).scalar()
        print(f"Total volunteers: {total}")
        
        # 2. Data completeness
        print("\n📋 DATA COMPLETENESS")
        print("-" * 60)
        
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                  'city', 'state', 'zip_code', 'training_status']
        
        for field in fields:
            null_count = conn.execute(text(f"""
                SELECT COUNT(*) FROM volunteers 
                WHERE {field} IS NULL OR {field} = '' OR {field} = 'nan'
            """)).scalar()
            completeness = ((total - null_count) / total * 100) if total > 0 else 0
            status = "✅" if completeness > 90 else "⚠️" if completeness > 50 else "❌"
            print(f"{status} {field:20s}: {completeness:5.1f}% complete ({total - null_count}/{total})")
        
        # 3. Training status breakdown
        print("\n🎓 TRAINING STATUS BREAKDOWN")
        print("-" * 60)
        
        result = conn.execute(text("""
            SELECT training_status, COUNT(*) as count
            FROM volunteers
            GROUP BY training_status
            ORDER BY count DESC
        """))
        
        for row in result:
            status = row[0] if row[0] else "Unknown"
            count = row[1]
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {status:20s}: {count:4d} ({pct:5.1f}%)")
        
        # 4. Active status
        print("\n✅ ACTIVE STATUS")
        print("-" * 60)
        
        active_cat = conn.execute(text("SELECT COUNT(*) FROM volunteers WHERE active_cat = true")).scalar()
        active_bat = conn.execute(text("SELECT COUNT(*) FROM volunteers WHERE active_bat = true")).scalar()
        active_bact = conn.execute(text("SELECT COUNT(*) FROM volunteers WHERE active_bact = true")).scalar()
        
        print(f"  Active CAT:  {active_cat:4d} ({active_cat/total*100:5.1f}%)")
        print(f"  Active BAT:  {active_bat:4d} ({active_bat/total*100:5.1f}%)")
        print(f"  Active BACT: {active_bact:4d} ({active_bact/total*100:5.1f}%)")
        
        # 5. Geographic distribution
        print("\n🗺️  GEOGRAPHIC DISTRIBUTION")
        print("-" * 60)
        
        result = conn.execute(text("""
            SELECT city, COUNT(*) as count
            FROM volunteers
            WHERE city IS NOT NULL AND city != '' AND city != 'nan'
            GROUP BY city
            ORDER BY count DESC
            LIMIT 10
        """))
        
        print("  Top 10 cities:")
        for row in result:
            print(f"    {row[0]:30s}: {row[1]:3d}")
        
        # 6. Data quality issues
        print("\n⚠️  DATA QUALITY ISSUES")
        print("-" * 60)
        
        # Check for duplicate emails
        duplicates = conn.execute(text("""
            SELECT email, COUNT(*) as count
            FROM volunteers
            WHERE email IS NOT NULL AND email != '' AND email != 'nan'
            GROUP BY email
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        if duplicates:
            print(f"  ❌ Found {len(duplicates)} duplicate email addresses:")
            for dup in duplicates[:5]:
                print(f"     {dup[0]}: {dup[1]} occurrences")
        else:
            print("  ✅ No duplicate email addresses found")
        
        # Check for invalid phone numbers
        invalid_phones = conn.execute(text("""
            SELECT COUNT(*) FROM volunteers
            WHERE phone IS NOT NULL 
            AND phone != '' 
            AND phone != 'nan'
            AND LENGTH(phone) < 10
        """)).scalar()
        
        if invalid_phones > 0:
            print(f"  ⚠️  {invalid_phones} potentially invalid phone numbers (too short)")
        else:
            print("  ✅ All phone numbers appear valid")
        
        # 7. Relationship table status
        print("\n🔗 RELATIONSHIP TABLES")
        print("-" * 60)
        
        training_count = conn.execute(text("SELECT COUNT(*) FROM training")).scalar()
        assignments_count = conn.execute(text("SELECT COUNT(*) FROM volunteer_assignments")).scalar()
        attendance_count = conn.execute(text("SELECT COUNT(*) FROM visit_attendance")).scalar()
        
        print(f"  Training records:        {training_count:4d}")
        print(f"  Site assignments:        {assignments_count:4d}")
        print(f"  Visit attendance:        {attendance_count:4d}")
        
        if training_count == 0 and assignments_count == 0 and attendance_count == 0:
            print("\n  ⚠️  All relationship tables are empty - need to populate!")
        
        # 8. Sample volunteers
        print("\n👥 SAMPLE VOLUNTEER RECORDS")
        print("-" * 60)
        
        result = conn.execute(text("""
            SELECT volunteer_id, first_name, last_name, email, training_status
            FROM volunteers
            ORDER BY volunteer_id
            LIMIT 5
        """))
        
        for row in result:
            print(f"  ID {row[0]:4s}: {row[1]} {row[2]:15s} | {row[3]:30s} | {row[4]}")
    
    print("\n" + "=" * 60)
    print("✅ Audit complete!")

if __name__ == "__main__":
    audit_volunteers()
