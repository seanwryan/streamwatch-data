-- Example SQL Queries for Watershed Team to Test Database Access
-- Copy and paste these into any database client or the web interface

-- ===========================================
-- BASIC DATA EXPLORATION QUERIES
-- ===========================================

-- 1. Count records in each table
SELECT 'sites' as table_name, COUNT(*) as record_count FROM sites
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
ORDER BY table_name;

-- 2. View first 5 sites with GPS coordinates
SELECT site_code, waterbody, latitude, longitude, is_active
FROM sites 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL
ORDER BY site_code
LIMIT 5;

-- 3. View recent bacteria test results
SELECT site_code, collection_date, e_coli, measurement_value
FROM bacteria 
WHERE collection_date IS NOT NULL
ORDER BY collection_date DESC
LIMIT 10;

-- ===========================================
-- DATA QUALITY CHECKING QUERIES
-- ===========================================

-- 4. Sites missing GPS coordinates
SELECT site_code, waterbody, description
FROM sites 
WHERE latitude IS NULL OR longitude IS NULL
ORDER BY site_code;

-- 5. Volunteers by status
SELECT training_status, COUNT(*) as volunteer_count
FROM volunteers 
GROUP BY training_status
ORDER BY volunteer_count DESC;

-- 6. Most common bug families
SELECT family, COUNT(*) as bug_count
FROM bugs 
WHERE family IS NOT NULL
GROUP BY family
ORDER BY bug_count DESC
LIMIT 10;

-- ===========================================
-- ANALYSIS QUERIES
-- ===========================================

-- 7. E.coli levels by site (average)
SELECT site_code, 
       COUNT(*) as test_count,
       AVG(e_coli) as avg_e_coli,
       MAX(e_coli) as max_e_coli
FROM bacteria 
WHERE e_coli IS NOT NULL
GROUP BY site_code
ORDER BY avg_e_coli DESC
LIMIT 10;

-- 8. EPT taxa (sensitive bugs) in taxonomy
SELECT family, genus_species, ept, insect
FROM taxonomy 
WHERE ept = true
ORDER BY family;

-- 9. Sites with most bug diversity
SELECT b.sample_code, 
       COUNT(DISTINCT b.family) as unique_families,
       COUNT(*) as total_bugs
FROM bugs b
WHERE b.family IS NOT NULL
GROUP BY b.sample_code
ORDER BY unique_families DESC
LIMIT 10;

-- ===========================================
-- SEARCH QUERIES
-- ===========================================

-- 10. Search for sites by waterbody name
SELECT site_code, waterbody, latitude, longitude
FROM sites 
WHERE UPPER(waterbody) LIKE '%ASSUNPINK%'
ORDER BY site_code;

-- 11. Find volunteers by name
SELECT volunteer_id, first_name, last_name, email, training_status
FROM volunteers 
WHERE UPPER(first_name) LIKE '%JOHN%' OR UPPER(last_name) LIKE '%SMITH%'
ORDER BY last_name, first_name;

-- 12. Bacteria tests for a specific site
SELECT collection_date, e_coli, measurement_value, water_temperature
FROM bacteria 
WHERE site_code = 'APL1'
ORDER BY collection_date DESC;

-- ===========================================
-- CONNECTION TEST QUERIES
-- ===========================================

-- 13. Test basic connection
SELECT 'Database connection successful!' as status, 
       NOW() as current_time,
       COUNT(*) as total_sites FROM sites;

-- 14. Check user permissions (run with edit user)
SELECT current_user, session_user, current_database();

-- 15. View table schemas
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
ORDER BY table_name, ordinal_position;
