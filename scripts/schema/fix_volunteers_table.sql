-- Fix volunteers table to match Jian's Access database structure (VOLUNTEERtbl)
-- Run this script in DBeaver SQL Editor

BEGIN;

-- Step 1: Create backup of existing site_code assignments
CREATE TABLE IF NOT EXISTS volunteer_site_assignments_backup AS
SELECT volunteer_id, site_code, start_date as assignment_date
FROM volunteers
WHERE site_code IS NOT NULL;

-- Step 2: Add missing columns to volunteers table
ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS perfect_id VARCHAR(50);
ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS int_last_name VARCHAR(100);
ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS is_under_17 BOOLEAN DEFAULT false;
ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Step 3: Create training table (tblTraining)
CREATE TABLE IF NOT EXISTS training (
    training_id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
    training_type VARCHAR(100),
    training_date DATE,
    expiration_date DATE,
    test_score DECIMAL(5,2),
    notes TEXT,
    created_date TIMESTAMP DEFAULT NOW(),
    updated_date TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_training_volunteer_id ON training(volunteer_id);

-- Step 4: Create volunteer_assignments table (juncAssignments)
CREATE TABLE IF NOT EXISTS volunteer_assignments (
    assignment_id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
    site_code VARCHAR(50) NOT NULL REFERENCES sites(site_code) ON DELETE CASCADE,
    sector VARCHAR(50),
    assign_start DATE,
    assign_end DATE,
    notes TEXT,
    is_valid BOOLEAN DEFAULT true,
    created_date TIMESTAMP DEFAULT NOW(),
    updated_date TIMESTAMP DEFAULT NOW(),
    UNIQUE(volunteer_id, site_code, assign_start)
);

CREATE INDEX IF NOT EXISTS idx_assignments_volunteer_id ON volunteer_assignments(volunteer_id);
CREATE INDEX IF NOT EXISTS idx_assignments_site_code ON volunteer_assignments(site_code);

-- Step 5: Migrate existing site_code assignments to volunteer_assignments
INSERT INTO volunteer_assignments (volunteer_id, site_code, assign_start, is_valid)
SELECT 
    volunteer_id,
    site_code,
    COALESCE(start_date, CURRENT_DATE) as assign_start,
    COALESCE(is_active, true) as is_valid
FROM volunteers
WHERE site_code IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM volunteer_assignments va
    WHERE va.volunteer_id = volunteers.volunteer_id
    AND va.site_code = volunteers.site_code
);

-- Step 6: Create visit_attendance table (juncAttendance)
CREATE TABLE IF NOT EXISTS visit_attendance (
    attendance_id SERIAL PRIMARY KEY,
    volunteer_id INTEGER NOT NULL REFERENCES volunteers(volunteer_id) ON DELETE CASCADE,
    visit_id INTEGER REFERENCES samples(sample_id) ON DELETE CASCADE,
    data_code VARCHAR(50),
    notes TEXT,
    created_date TIMESTAMP DEFAULT NOW(),
    updated_date TIMESTAMP DEFAULT NOW(),
    UNIQUE(volunteer_id, visit_id)
);

CREATE INDEX IF NOT EXISTS idx_attendance_volunteer_id ON visit_attendance(volunteer_id);
CREATE INDEX IF NOT EXISTS idx_attendance_visit_id ON visit_attendance(visit_id);

-- Step 7: Migrate existing volunteer_id from samples to visit_attendance
INSERT INTO visit_attendance (volunteer_id, visit_id)
SELECT 
    volunteer_id,
    sample_id
FROM samples
WHERE volunteer_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM visit_attendance va
    WHERE va.volunteer_id = samples.volunteer_id
    AND va.visit_id = samples.sample_id
);

-- Step 8: Show summary
SELECT 
    'Volunteers table updated' as status,
    (SELECT COUNT(*) FROM volunteers) as volunteer_count,
    (SELECT COUNT(*) FROM volunteer_assignments) as assignment_count,
    (SELECT COUNT(*) FROM visit_attendance) as attendance_count,
    (SELECT COUNT(*) FROM training) as training_count;

COMMIT;

-- Verification queries (run separately to check results):

-- Check volunteers table structure
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'volunteers'
-- ORDER BY ordinal_position;

-- Check new tables were created
-- SELECT table_name
-- FROM information_schema.tables
-- WHERE table_schema = 'public'
-- AND table_name IN ('training', 'volunteer_assignments', 'visit_attendance')
-- ORDER BY table_name;





