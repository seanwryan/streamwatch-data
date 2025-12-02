-- FIX FOR TRANSACTION ERROR
-- First, run this to clear the failed transaction:
ROLLBACK;

-- Then check your connection - you need DATABASE OWNER credentials, not streamwatch_edit
-- The streamwatch_edit user doesn't have ALTER TABLE permissions

-- ============================================================================
-- SOLUTION: Run these commands ONE AT A TIME with OWNER credentials
-- ============================================================================

-- Step 1: Clear any failed transaction
ROLLBACK;

-- Step 2: Add columns (run each separately)
ALTER TABLE volunteers ADD COLUMN alt_email VARCHAR(255);
ALTER TABLE volunteers ADD COLUMN alt_phone VARCHAR(20);
ALTER TABLE volunteers ADD COLUMN alternate_partner VARCHAR(20);
ALTER TABLE volunteers ADD COLUMN status VARCHAR(50);
ALTER TABLE volunteers ADD COLUMN vol_flag BOOLEAN DEFAULT false;

-- Step 3: Add constraints (run separately)
ALTER TABLE volunteers 
ADD CONSTRAINT volunteers_alternate_partner_fkey 
FOREIGN KEY (alternate_partner) REFERENCES volunteers(volunteer_id);

ALTER TABLE volunteers 
ADD CONSTRAINT check_status_values 
CHECK (status IS NULL OR status IN ('Active', 'Inactive', 'Parent', 'Unknown'));

-- Step 4: Migrate data
UPDATE volunteers 
SET status = CASE 
    WHEN training_status = 'Active' THEN 'Active'
    WHEN training_status = 'Inactive' THEN 'Inactive'
    WHEN training_status = 'Parent' THEN 'Parent'
    WHEN training_status = 'Unknown' THEN 'Unknown'
    WHEN training_status = 'TEST' THEN 'Active'
    ELSE 'Unknown'
END
WHERE training_status IS NOT NULL;

-- Step 5: Create VIEWs
CREATE OR REPLACE VIEW volunteers_full_name AS
SELECT 
    volunteer_id,
    COALESCE(first_name || ' ' || last_name, first_name, last_name, '') AS full_name
FROM volunteers;

CREATE OR REPLACE VIEW volunteers_int_last_name AS
SELECT 
    volunteer_id,
    UPPER(SUBSTRING(COALESCE(first_name, ''), 1, 1)) || COALESCE(last_name, '') AS int_last_name
FROM volunteers
WHERE first_name IS NOT NULL AND last_name IS NOT NULL;

CREATE OR REPLACE VIEW volunteers_start_date AS
SELECT 
    v.volunteer_id,
    MIN(t.training_date) AS start_date
FROM volunteers v
LEFT JOIN training t ON v.volunteer_id = t.volunteer_id
GROUP BY v.volunteer_id;

