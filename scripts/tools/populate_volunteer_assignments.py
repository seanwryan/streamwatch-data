#!/usr/bin/env python3
"""
Populate volunteer_assignments table from existing volunteer data
Migrates the old volunteers.site_code field to the new junction table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine, text
from datetime import datetime

# Using edit credentials
DATABASE_URL = "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"

def populate_volunteer_assignments():
    """Populate volunteer_assignments from existing data"""
    print("🔄 Populating Volunteer Assignments Table")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if volunteers table has site_code column
        print("\n1. Checking for site_code column in volunteers table...")
        
        try:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'volunteers' 
                AND column_name = 'site_code'
            """))
            
            if not result.fetchone():
                print("   ⚠️  No site_code column found in volunteers table")
                print("   ℹ️  This is expected if volunteers aren't assigned to specific sites")
                print("   ℹ️  You may need to import assignment data from another source")
                return
            
            print("   ✅ site_code column found")
            
        except Exception as e:
            print(f"   ❌ Error checking column: {e}")
            return
        
        # Get volunteers with site assignments
        print("\n2. Finding volunteers with site assignments...")
        
        result = conn.execute(text("""
            SELECT volunteer_id, site_code
            FROM volunteers
            WHERE site_code IS NOT NULL 
            AND site_code != ''
            AND site_code != 'nan'
        """))
        
        assignments = result.fetchall()
        print(f"   Found {len(assignments)} volunteer-site assignments")
        
        if len(assignments) == 0:
            print("   ⚠️  No site assignments found in volunteers table")
            print("   ℹ️  You may need to import assignment data from another source")
            return
        
        # Insert into volunteer_assignments
        print("\n3. Creating assignment records...")
        
        inserted = 0
        errors = 0
        
        for vol_id, site_code in assignments:
            try:
                conn.execute(text("""
                    INSERT INTO volunteer_assignments 
                    (volunteer_id, site_code, is_valid, assign_start, notes)
                    VALUES (:vol_id, :site_code, true, :start_date, 'Migrated from volunteers.site_code')
                """), {
                    'vol_id': vol_id,
                    'site_code': site_code,
                    'start_date': datetime.now().date()
                })
                inserted += 1
                
                if inserted % 50 == 0:
                    print(f"   Inserted {inserted} assignments...")
                    
            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"   ⚠️  Error inserting {vol_id} -> {site_code}: {e}")
        
        conn.commit()
        
        print(f"\n✅ Migration complete!")
        print(f"   Inserted: {inserted}")
        print(f"   Errors:   {errors}")
        
        # Verify
        print("\n4. Verifying results...")
        
        count = conn.execute(text("SELECT COUNT(*) FROM volunteer_assignments")).scalar()
        print(f"   Total assignments in table: {count}")
        
        # Show sample
        print("\n5. Sample assignments:")
        result = conn.execute(text("""
            SELECT va.volunteer_id, v.first_name, v.last_name, va.site_code, s.waterbody
            FROM volunteer_assignments va
            JOIN volunteers v ON va.volunteer_id = v.volunteer_id
            LEFT JOIN sites s ON va.site_code = s.site_code
            LIMIT 5
        """))
        
        for row in result:
            waterbody = row[4] if row[4] else "Unknown"
            print(f"   {row[0]:4s}: {row[1]} {row[2]:15s} -> {row[3]:10s} ({waterbody})")

if __name__ == "__main__":
    populate_volunteer_assignments()
