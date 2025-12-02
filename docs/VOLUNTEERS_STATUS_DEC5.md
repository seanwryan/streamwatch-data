# Volunteers Table Status - December 5, 2025 Meeting

## Current Status Summary

### ✅ Completed Work

#### 1. Table Structure Alignment
- **Volunteers table** now matches Access VOLUNTEERtbl structure:
  - Added `perfect_id` (VARCHAR)
  - Added `int_last_name` (VARCHAR)
  - Added `is_under_17` (BOOLEAN)
  - Added `address` (TEXT)
  - Verified `is_active` (BOOLEAN) exists

#### 2. Relationship Tables Created
- **training** (tblTraining equivalent) - ✅ Created
- **volunteer_assignments** (juncAssignments equivalent) - ✅ Created
- **visit_attendance** (juncAttendance equivalent) - ✅ Created

#### 3. Data Population
- **Training records**: 167 records loaded from TrainingLog sheet
- **Site assignments**: 56 records loaded from Assignments sheet
- **Visit attendance**: 0 records (samples table doesn't have volunteer_id column - needs manual entry or form-based collection)

### 📊 Current Data Statistics

**Volunteers Table:**
- Total volunteers: 403
- Data completeness:
  - ✅ First name: 100%
  - ✅ Last name: 100%
  - ✅ Email: 91.3%
  - ⚠️ Phone: 29.8%
  - ✅ Address: 97.0%
  - ✅ City: 95.8%
  - ✅ State: 97.3%
  - ✅ Zip code: 97.3%

**Training Status:**
- Inactive: 250 (62.0%)
- Active: 98 (24.3%)
- Unknown: 33 (8.2%)
- Parent: 21 (5.2%)

**Program Participation:**
- Active CAT: 66 (16.4%)
- Active BAT: 31 (7.7%)
- Active BACT: 52 (12.9%)

**Relationship Data:**
- Training records: 167
- Site assignments: 56
- Visit attendance: 0 (needs implementation)

### 🔗 Relationship Examples

**Volunteers with Most Training:**
- Alexia Thanapalasingam (ID 6): 6 training records
- Noemi de la Puente (ID 68): 5 training records
- Kristine Wang (ID 31): 5 training records

**Volunteers with Most Site Assignments:**
- Harin Desai (ID 18): 3 assignments
- Rhea Ajmera (ID 45): 3 assignments
- Kristine Wang (ID 31): 3 assignments

### ⚠️ Known Issues

1. **Visit Attendance**: Cannot be automatically populated because `samples` table doesn't have a `volunteer_id` column. This will need to be:
   - Populated manually through data entry forms
   - Or added to samples table if historical data exists elsewhere

2. **Data Quality**:
   - 1 duplicate email address found: `arajo798@gmail.com` (2 occurrences)
   - Phone number completeness is low (29.8%) - may need data collection

3. **Missing Assignments**: 10 assignment records were skipped because:
   - Volunteer ID not found in volunteers table, OR
   - Site code not found in sites table

### 📋 Next Steps

#### Immediate (Before Forms)
1. **Resolve duplicate email** - Determine which volunteer record is correct
2. **Investigate missing assignments** - Verify volunteer IDs and site codes in source data
3. **Plan visit attendance collection** - Determine how to link volunteers to visits/samples

#### For Data Entry Forms
1. **Volunteer Entry Form** - Add/edit volunteer information
   - Fields: perfect_id, int_last_name, is_under_17, address, etc.
   - Subform for training records
   - Subform for site assignments
   - Subform for visit attendance

2. **Training Log Form** - Record training completion
   - Link to volunteer
   - Training type, date, expiration, test score

3. **Assignment Form** - Assign volunteers to sites
   - Many-to-many relationship
   - Start/end dates, sector/role

4. **Visit Attendance Form** - Record who attended each visit
   - Link volunteers to samples/visits
   - Multiple volunteers per visit

### 🔧 Available Scripts

**Data Loading:**
- `scripts/etl/load_volunteer_data.py` - Main volunteer data loader
- `scripts/etl/load_training_data.py` - Load training records
- `scripts/etl/load_volunteer_assignments_data.py` - Load site assignments
- `scripts/etl/load_visit_attendance_data.py` - (Ready for when data source is available)

**Schema Management:**
- `scripts/schema/fix_volunteers_table.py` - Update table structure
- `scripts/schema/fix_volunteers_table.sql` - SQL version for DBeaver

**Tools:**
- `scripts/tools/audit_volunteer_data.py` - Comprehensive data audit
- `scripts/tools/populate_volunteer_assignments.py` - Migrate assignments

### 📝 Questions for Jian

1. **Perfect ID System**: What is the perfect_id field used for? Is there existing data we should populate?

2. **Internal Last Name**: What is int_last_name used for? Should we populate this from existing data?

3. **Visit Attendance**: How should we link volunteers to visits? Is there historical data elsewhere, or will this be form-based going forward?

4. **Training Data**: Are there additional training records beyond what's in the TrainingLog sheet?

5. **Assignment Dates**: Some assignments have end dates in the past - should these be marked as `is_valid = false`?

6. **Data Entry Forms**: What's the priority order for building forms?
   - Volunteer entry/editing?
   - Training log?
   - Assignment management?
   - Visit attendance?

### 📊 Database Schema Reference

**Volunteers Table Columns:**
- volunteer_id (VARCHAR, PK)
- perfect_id (VARCHAR)
- first_name (VARCHAR)
- last_name (VARCHAR)
- int_last_name (VARCHAR)
- is_active (BOOLEAN)
- is_under_17 (BOOLEAN)
- address (TEXT)
- email (VARCHAR)
- phone (VARCHAR)
- city, state, zip_code (VARCHAR)
- start_date (DATE)
- active_cat, active_bat, active_bact (BOOLEAN)
- training_status (VARCHAR)
- notes (TEXT)
- created_date, updated_date (TIMESTAMP)

**Related Tables:**
- training: volunteer_id → training records (one-to-many)
- volunteer_assignments: volunteer_id ↔ site_code (many-to-many)
- visit_attendance: volunteer_id ↔ visit_id (many-to-many)

---

**Prepared by:** Sean Ryan  
**Date:** December 2, 2025  
**For Meeting:** December 5, 2025

