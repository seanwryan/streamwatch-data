# Viewing Volunteers Table Changes in DBeaver

**Date**: October 2025  
**Purpose**: Guide to view and verify the volunteers table structure changes

---

## 🚀 Running the Script

The script requires your database password. You can run it in one of two ways:

### **Option 1: Set Environment Variable**
```bash
export DB_PASSWORD="your_password_here"
cd /Users/seanryan/Desktop/Projects/streamwatch-data
PYTHONPATH=. python scripts/schema/fix_volunteers_table.py
```

### **Option 2: Run SQL Directly in DBeaver**
Copy and paste the SQL statements from the script into DBeaver's SQL editor.

---

## 📊 Viewing Changes in DBeaver

### **1. View Updated Volunteers Table Structure**

**In DBeaver:**
1. Navigate to: `Database Navigator` → `neondb` → `Schemas` → `public` → `Tables` → `volunteers`
2. Right-click → **View/Edit Data** → **View Data**
3. Or right-click → **Properties** → **Columns** tab to see all columns

**New columns you should see:**
- `perfect_id` (VARCHAR)
- `int_last_name` (VARCHAR)
- `is_under_17` (BOOLEAN)
- `address` (TEXT)

**SQL Query to Check:**
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'volunteers'
ORDER BY ordinal_position;
```

---

### **2. View New Training Table**

**In DBeaver:**
1. Navigate to: `Database Navigator` → `neondb` → `Schemas` → `public` → `Tables` → `training`
2. Right-click → **View/Edit Data** → **View Data**

**SQL Query to Check:**
```sql
SELECT * FROM training LIMIT 10;
```

**Check table structure:**
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'training'
ORDER BY ordinal_position;
```

---

### **3. View Volunteer Assignments (Many-to-Many with Sites)**

**In DBeaver:**
1. Navigate to: `Database Navigator` → `neondb` → `Schemas` → `public` → `Tables` → `volunteer_assignments`
2. Right-click → **View/Edit Data** → **View Data**

**SQL Query to See All Assignments:**
```sql
SELECT 
    v.volunteer_id,
    v.first_name || ' ' || v.last_name AS volunteer_name,
    va.assignment_id,
    va.site_code,
    s.site_name,
    va.assign_start,
    va.assign_end,
    va.is_valid
FROM volunteers v
JOIN volunteer_assignments va ON v.volunteer_id = va.volunteer_id
LEFT JOIN sites s ON va.site_code = s.site_code
ORDER BY v.last_name, va.site_code;
```

**Check how many volunteers were migrated:**
```sql
SELECT COUNT(*) as total_assignments,
       COUNT(DISTINCT volunteer_id) as unique_volunteers,
       COUNT(DISTINCT site_code) as unique_sites
FROM volunteer_assignments;
```

---

### **4. View Visit Attendance (Many-to-Many with Visits)**

**In DBeaver:**
1. Navigate to: `Database Navigator` → `neondb` → `Schemas` → `public` → `Tables` → `visit_attendance`
2. Right-click → **View/Edit Data** → **View Data`

**SQL Query to See All Attendance:**
```sql
SELECT 
    v.volunteer_id,
    v.first_name || ' ' || v.last_name AS volunteer_name,
    va.attendance_id,
    va.visit_id,
    sm.sample_date,
    sm.sample_code,
    s.site_name,
    va.data_code,
    va.notes
FROM volunteers v
JOIN visit_attendance va ON v.volunteer_id = va.volunteer_id
JOIN samples sm ON va.visit_id = sm.sample_id
JOIN sites s ON sm.site_code = s.site_code
ORDER BY sm.sample_date DESC
LIMIT 50;
```

**Check how many attendance records were migrated:**
```sql
SELECT COUNT(*) as total_attendance,
       COUNT(DISTINCT volunteer_id) as unique_volunteers,
       COUNT(DISTINCT visit_id) as unique_visits
FROM visit_attendance;
```

---

### **5. View Backup Table (Safety Check)**

**In DBeaver:**
1. Navigate to: `Database Navigator` → `neondb` → `Schemas` → `public` → `Tables` → `volunteer_site_assignments_backup`
2. Right-click → **View/Edit Data** → **View Data`

**SQL Query to Compare:**
```sql
-- Original assignments (from backup)
SELECT COUNT(*) as original_count
FROM volunteer_site_assignments_backup;

-- New assignments (migrated)
SELECT COUNT(*) as migrated_count
FROM volunteer_assignments;

-- Should match or be close!
```

---

## 🔍 Relationship Diagram View

**In DBeaver:**
1. Navigate to: `Database Navigator` → `neondb` → `Schemas` → `public` → `Tables`
2. Select multiple tables: `volunteers`, `volunteer_assignments`, `sites`, `training`, `visit_attendance`
3. Right-click → **View Diagram** to see relationships

---

## 📋 Verification Queries

### **Check All New Tables Exist:**
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('training', 'volunteer_assignments', 'visit_attendance', 'volunteer_site_assignments_backup')
ORDER BY table_name;
```

### **Check Foreign Key Relationships:**
```sql
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND (tc.table_name IN ('training', 'volunteer_assignments', 'visit_attendance')
     OR ccu.table_name = 'volunteers')
ORDER BY tc.table_name, kcu.column_name;
```

### **Summary of Changes:**
```sql
-- Volunteers table column count
SELECT COUNT(*) as volunteer_columns
FROM information_schema.columns
WHERE table_name = 'volunteers';

-- Training records count
SELECT COUNT(*) as training_records FROM training;

-- Assignment records count
SELECT COUNT(*) as assignment_records FROM volunteer_assignments;

-- Attendance records count
SELECT COUNT(*) as attendance_records FROM visit_attendance;
```

---

## 🔄 Undoing Changes (If Needed)

If you need to undo the changes, you can:

### **Remove New Columns from Volunteers:**
```sql
ALTER TABLE volunteers DROP COLUMN IF EXISTS perfect_id;
ALTER TABLE volunteers DROP COLUMN IF EXISTS int_last_name;
ALTER TABLE volunteers DROP COLUMN IF EXISTS is_under_17;
ALTER TABLE volunteers DROP COLUMN IF EXISTS address;
```

### **Drop New Tables:**
```sql
DROP TABLE IF EXISTS visit_attendance CASCADE;
DROP TABLE IF EXISTS volunteer_assignments CASCADE;
DROP TABLE IF EXISTS training CASCADE;
```

### **Restore from Backup (if needed):**
The backup table `volunteer_site_assignments_backup` contains the original assignments.

---

## ✅ Expected Results

After running the script, you should see:

- ✅ **volunteers table**: 4 new columns added
- ✅ **training table**: Created (0 records initially, ready for data)
- ✅ **volunteer_assignments table**: Created with ~428 records (migrated from volunteers.site_code)
- ✅ **visit_attendance table**: Created with ~16,910 records (migrated from samples.volunteer_id)
- ✅ **volunteer_site_assignments_backup table**: Backup of original assignments

---

*All changes are reversible and the script preserves all existing data.*



