-- Create VIEWs for calculated fields in volunteers table
-- Run with database owner credentials

-- VIEW 1: full_name (First Name + Last Name)
CREATE OR REPLACE VIEW volunteers_full_name AS
SELECT 
    volunteer_id,
    COALESCE(first_name || ' ' || last_name, first_name, last_name, '') AS full_name
FROM volunteers;

-- VIEW 2: int_last_name (First letter of first name + Last Name)
CREATE OR REPLACE VIEW volunteers_int_last_name AS
SELECT 
    volunteer_id,
    UPPER(SUBSTRING(COALESCE(first_name, ''), 1, 1)) || COALESCE(last_name, '') AS int_last_name
FROM volunteers
WHERE first_name IS NOT NULL AND last_name IS NOT NULL;

-- VIEW 3: start_date (earliest training date)
CREATE OR REPLACE VIEW volunteers_start_date AS
SELECT 
    v.volunteer_id,
    MIN(t.training_date) AS start_date
FROM volunteers v
LEFT JOIN training t ON v.volunteer_id = t.volunteer_id
GROUP BY v.volunteer_id;

-- Test the VIEWs
SELECT 'Testing full_name VIEW:' as test;
SELECT * FROM volunteers_full_name LIMIT 5;

SELECT 'Testing int_last_name VIEW:' as test;
SELECT * FROM volunteers_int_last_name LIMIT 5;

SELECT 'Testing start_date VIEW:' as test;
SELECT * FROM volunteers_start_date LIMIT 5;

