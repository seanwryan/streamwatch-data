-- ============================================================================
-- ALIGN SITES WITH REQUIREMENTS (Volunteers Pattern)
-- ============================================================================
-- Description:
-- 1. Creates municipalities table (City/State/Zip lookup)
-- 2. Populates it from existing volunteer data
-- 3. Links volunteers to municipalities
-- 4. Links sites to municipalities
-- 5. Cleans site data to match new enums
-- 6. Adds strict status constraints to sites
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Create Municipalities Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS municipalities (
    municipality_id SERIAL PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(2) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    county VARCHAR(50), -- Optional, can comes from WQX
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_municipality UNIQUE (city, state, zip_code)
);

-- ----------------------------------------------------------------------------
-- 2. Populate Municipalities (from Volunteers)
-- ----------------------------------------------------------------------------
INSERT INTO municipalities (city, state, zip_code)
SELECT DISTINCT 
    TRIM(city), 
    TRIM(state), 
    TRIM(zip_code)
FROM volunteers
WHERE city IS NOT NULL 
  AND state IS NOT NULL 
  AND zip_code IS NOT NULL
  AND city != ''
  AND state != ''
  AND zip_code != ''
ON CONFLICT (city, state, zip_code) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 3. Link Volunteers to Municipalities
-- ----------------------------------------------------------------------------
ALTER TABLE volunteers ADD COLUMN IF NOT EXISTS municipality_id INTEGER;

ALTER TABLE volunteers 
DROP CONSTRAINT IF EXISTS fk_volunteers_municipality;

ALTER TABLE volunteers
ADD CONSTRAINT fk_volunteers_municipality
FOREIGN KEY (municipality_id) REFERENCES municipalities(municipality_id);

-- Backfill volunteers
UPDATE volunteers v
SET municipality_id = m.municipality_id
FROM municipalities m
WHERE TRIM(v.city) = m.city 
  AND TRIM(v.state) = m.state 
  AND TRIM(v.zip_code) = m.zip_code;

-- ----------------------------------------------------------------------------
-- 4. Link Sites to Municipalities
-- ----------------------------------------------------------------------------
ALTER TABLE sites ADD COLUMN IF NOT EXISTS municipality_id INTEGER;

ALTER TABLE sites 
DROP CONSTRAINT IF EXISTS fk_sites_municipality;

ALTER TABLE sites
ADD CONSTRAINT fk_sites_municipality
FOREIGN KEY (municipality_id) REFERENCES municipalities(municipality_id);

-- ----------------------------------------------------------------------------
-- 5. Clean Data & Add Constraints to Sites
-- ----------------------------------------------------------------------------

-- Map legacy values to new standardize statuses
UPDATE sites SET cat_status = 'Active' WHERE cat_status = 'Vacant';
UPDATE sites SET cat_status = 'Inactive' WHERE cat_status = 'Retired';
UPDATE sites SET cat_status = 'Proposed' WHERE cat_status = 'Groundtruth';
UPDATE sites SET cat_status = 'Unknown' WHERE cat_status IS NULL;

UPDATE sites SET bat_status = 'Unknown' WHERE bat_status IS NULL;
UPDATE sites SET bact_status = 'Unknown' WHERE bact_status IS NULL;
UPDATE sites SET groundtruthing_status = 'Unknown' WHERE groundtruthing_status IS NULL;

-- Enforce CHECK constraints
ALTER TABLE sites DROP CONSTRAINT IF EXISTS check_site_cat_status;
ALTER TABLE sites ADD CONSTRAINT check_site_cat_status 
CHECK (cat_status IN ('Active', 'Inactive', 'Proposed', 'Unknown'));

ALTER TABLE sites DROP CONSTRAINT IF EXISTS check_site_bat_status;
ALTER TABLE sites ADD CONSTRAINT check_site_bat_status 
CHECK (bat_status IN ('Active', 'Inactive', 'Proposed', 'Unknown'));

ALTER TABLE sites DROP CONSTRAINT IF EXISTS check_site_bact_status;
ALTER TABLE sites ADD CONSTRAINT check_site_bact_status 
CHECK (bact_status IN ('Active', 'Inactive', 'Proposed', 'Unknown'));

-- ----------------------------------------------------------------------------
-- 6. Create Sites View
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW sites_view AS
SELECT 
    s.site_code,
    s.waterbody,
    s.watershed, -- existing column
    m.city,
    m.state,
    m.zip_code,
    m.county,
    s.latitude,
    s.longitude,
    s.cat_status,
    s.bat_status,
    s.bact_status,
    s.is_active
FROM sites s
LEFT JOIN municipalities m ON s.municipality_id = m.municipality_id;
