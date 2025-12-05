-- ============================================================================
-- COMPLETE SITES TABLE REQUIREMENTS
-- ============================================================================
-- This script implements all missing pieces from the SITES Table Schema requirements
-- Run with database owner credentials
-- ============================================================================

BEGIN;

-- ============================================================================
-- STEP 1: Add Missing Fields to Sites Table
-- ============================================================================

-- Add notes field (TEXT for general site notes)
ALTER TABLE sites ADD COLUMN IF NOT EXISTS notes TEXT;

-- Add site_flag (BOOLEAN, will be auto-calculated via trigger/VIEW)
ALTER TABLE sites ADD COLUMN IF NOT EXISTS site_flag BOOLEAN DEFAULT false;

-- Add map_link (URL for Google Maps)
ALTER TABLE sites ADD COLUMN IF NOT EXISTS map_link VARCHAR(500);

-- Add last_bact_sample_date (DATE field)
ALTER TABLE sites ADD COLUMN IF NOT EXISTS last_bact_sample_date DATE;

COMMENT ON COLUMN sites.notes IS 'General notes about the site';
COMMENT ON COLUMN sites.site_flag IS 'Auto-calculated flag based on related records in flag table';
COMMENT ON COLUMN sites.map_link IS 'URL link to Google Maps location';
COMMENT ON COLUMN sites.last_bact_sample_date IS 'Date of last BACT sample (can be calculated via VIEW)';

-- ============================================================================
-- STEP 2: Create Lookup Tables
-- ============================================================================

-- Create waterbodies table
CREATE TABLE IF NOT EXISTS waterbodies (
    waterbody_id SERIAL PRIMARY KEY,
    waterbody_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_waterbodies_name ON waterbodies(waterbody_name);

COMMENT ON TABLE waterbodies IS 'Lookup table for waterbodies (rivers, streams, etc.)';

-- Create subwatersheds table
CREATE TABLE IF NOT EXISTS subwatersheds (
    subwatershed_id SERIAL PRIMARY KEY,
    subwatershed_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subwatersheds_name ON subwatersheds(subwatershed_name);

COMMENT ON TABLE subwatersheds IS 'Lookup table for subwatersheds (many-to-many with sites)';

-- ============================================================================
-- STEP 3: Populate Lookup Tables from Existing Data
-- ============================================================================

-- Populate waterbodies from existing sites.waterbody values
INSERT INTO waterbodies (waterbody_name)
SELECT DISTINCT TRIM(waterbody)
FROM sites
WHERE waterbody IS NOT NULL 
  AND TRIM(waterbody) != ''
ON CONFLICT (waterbody_name) DO NOTHING;

-- Populate subwatersheds from existing sites.subwatershed values
INSERT INTO subwatersheds (subwatershed_name)
SELECT DISTINCT TRIM(subwatershed)
FROM sites
WHERE subwatershed IS NOT NULL 
  AND TRIM(subwatershed) != ''
ON CONFLICT (subwatershed_name) DO NOTHING;

-- ============================================================================
-- STEP 4: Create Junction Tables for Many-to-Many Relationships
-- ============================================================================

-- Junction table for sites and subwatersheds (many-to-many)
CREATE TABLE IF NOT EXISTS site_subwatersheds (
    site_code VARCHAR(20) NOT NULL REFERENCES sites(site_code) ON DELETE CASCADE,
    subwatershed_id INTEGER NOT NULL REFERENCES subwatersheds(subwatershed_id) ON DELETE CASCADE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (site_code, subwatershed_id)
);

CREATE INDEX IF NOT EXISTS idx_site_subwatersheds_site ON site_subwatersheds(site_code);
CREATE INDEX IF NOT EXISTS idx_site_subwatersheds_subwatershed ON site_subwatersheds(subwatershed_id);

COMMENT ON TABLE site_subwatersheds IS 'Many-to-many relationship between sites and subwatersheds';

-- Junction table for sites and municipalities (many-to-many)
-- Note: Keeping municipality_id in sites table for primary municipality
-- This junction table allows additional municipalities per site
CREATE TABLE IF NOT EXISTS site_municipalities (
    site_code VARCHAR(20) NOT NULL REFERENCES sites(site_code) ON DELETE CASCADE,
    municipality_id INTEGER NOT NULL REFERENCES municipalities(municipality_id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (site_code, municipality_id)
);

CREATE INDEX IF NOT EXISTS idx_site_municipalities_site ON site_municipalities(site_code);
CREATE INDEX IF NOT EXISTS idx_site_municipalities_municipality ON site_municipalities(municipality_id);

COMMENT ON TABLE site_municipalities IS 'Many-to-many relationship between sites and municipalities';

-- ============================================================================
-- STEP 5: Add Foreign Key Columns and Migrate Data
-- ============================================================================

-- Add waterbody_id to sites table
ALTER TABLE sites ADD COLUMN IF NOT EXISTS waterbody_id INTEGER;

ALTER TABLE sites 
DROP CONSTRAINT IF EXISTS fk_sites_waterbody;

ALTER TABLE sites
ADD CONSTRAINT fk_sites_waterbody
FOREIGN KEY (waterbody_id) REFERENCES waterbodies(waterbody_id);

-- Migrate waterbody data to FK
UPDATE sites s
SET waterbody_id = w.waterbody_id
FROM waterbodies w
WHERE TRIM(s.waterbody) = w.waterbody_name
  AND s.waterbody IS NOT NULL
  AND TRIM(s.waterbody) != '';

-- Migrate subwatershed data to junction table
INSERT INTO site_subwatersheds (site_code, subwatershed_id)
SELECT DISTINCT s.site_code, sw.subwatershed_id
FROM sites s
JOIN subwatersheds sw ON TRIM(s.subwatershed) = sw.subwatershed_name
WHERE s.subwatershed IS NOT NULL 
  AND TRIM(s.subwatershed) != ''
ON CONFLICT (site_code, subwatershed_id) DO NOTHING;

-- Migrate municipality data to junction table (from existing municipality_id)
INSERT INTO site_municipalities (site_code, municipality_id, is_primary)
SELECT site_code, municipality_id, true
FROM sites
WHERE municipality_id IS NOT NULL
ON CONFLICT (site_code, municipality_id) DO NOTHING;

-- ============================================================================
-- STEP 6: Create VIEWs for Calculated Fields
-- ============================================================================

-- VIEW for calculated status fields
CREATE OR REPLACE VIEW sites_calculated_status AS
SELECT 
    s.site_code,
    -- CAT Status: Active if recent sample, Inactive if priority is retired, else Unknown
    CASE 
        WHEN s.last_cat_sample_date IS NOT NULL 
             AND s.last_cat_sample_date > CURRENT_DATE - INTERVAL '1 year' 
        THEN 'Active'
        WHEN s.cat_priority = '4 - Retired/Inactive' THEN 'Inactive'
        WHEN s.cat_status IS NOT NULL THEN s.cat_status
        ELSE 'Unknown'
    END AS cat_status_calculated,
    
    -- BAT Status
    CASE 
        WHEN s.last_bat_sample_date IS NOT NULL 
             AND s.last_bat_sample_date > CURRENT_DATE - INTERVAL '1 year' 
        THEN 'Active'
        WHEN s.bat_priority = '4 - Retired/Inactive' THEN 'Inactive'
        WHEN s.bat_status IS NOT NULL THEN s.bat_status
        ELSE 'Unknown'
    END AS bat_status_calculated,
    
    -- BACT Status
    CASE 
        WHEN s.last_bact_sample_date IS NOT NULL 
             AND s.last_bact_sample_date > CURRENT_DATE - INTERVAL '1 year' 
        THEN 'Active'
        WHEN s.bact_priority = '4 - Retired/Inactive' THEN 'Inactive'
        WHEN s.bact_status IS NOT NULL THEN s.bact_status
        ELSE 'Unknown'
    END AS bact_status_calculated
FROM sites s;

COMMENT ON VIEW sites_calculated_status IS 'Calculated status fields for CAT, BAT, and BACT programs';

-- VIEW for calculated last sample dates (from actual sample data)
CREATE OR REPLACE VIEW sites_last_sample_dates_calculated AS
SELECT 
    s.site_code,
    -- Last CAT sample date (from samples table)
    (SELECT MAX(sa.sample_date) 
     FROM samples sa 
     WHERE sa.site_code = s.site_code) AS last_cat_sample_date_calc,
    
    -- Last BAT sample date (from samples table - same for now, may need separate tracking)
    (SELECT MAX(sa.sample_date) 
     FROM samples sa 
     WHERE sa.site_code = s.site_code) AS last_bat_sample_date_calc,
    
    -- Last BACT sample date (from bacteria table)
    (SELECT MAX(ba.collection_date) 
     FROM bacteria ba 
     WHERE ba.site_code = s.site_code) AS last_bact_sample_date_calc
FROM sites s;

COMMENT ON VIEW sites_last_sample_dates_calculated IS 'Calculated last sample dates from actual sample/bacteria records';

-- VIEW for site_flag calculation (based on data_flags table if it exists)
-- Note: This assumes data_flags table structure from SCHEMA_REVIEW_AND_RECOMMENDATIONS.md
CREATE OR REPLACE VIEW sites_flag_calculated AS
SELECT 
    s.site_code,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM data_flags df 
            WHERE df.table_name = 'sites' 
              AND df.record_id::text = s.site_code
              AND df.resolved = false
        ) THEN true
        ELSE false
    END AS site_flag_calculated
FROM sites s;

COMMENT ON VIEW sites_flag_calculated IS 'Calculated site_flag based on related records in flag table';

-- ============================================================================
-- STEP 7: Create Comprehensive Sites View (for forms)
-- ============================================================================

CREATE OR REPLACE VIEW sites_comprehensive AS
SELECT 
    s.site_code,
    s.is_active,
    s.groundtruthing_priority,
    s.groundtruthing_status,
    
    -- Waterbody (from lookup)
    w.waterbody_name,
    w.waterbody_id,
    
    -- Subwatersheds (aggregated from junction table)
    STRING_AGG(DISTINCT sw.subwatershed_name, ', ' ORDER BY sw.subwatershed_name) AS subwatersheds,
    
    -- Description
    s.description,
    
    -- Ownership
    s.property_type,
    s.permission,
    
    -- Municipality (primary from junction table)
    m.city AS municipality_city,
    m.state AS municipality_state,
    m.municipality_id,
    
    -- Access fields
    s.walk_time,
    s.walk_distance,
    s.walk_gradient,
    s.water_access,
    s.additional_comments,
    s.environmental_hazards,
    s.parking_details,
    s.walking_directions,
    
    -- Additional Info
    s.habitat_type,
    s.latitude,
    s.longitude,
    s.site_type,
    s.drainage_area,
    s.notes,
    s.map_link,
    
    -- Status (calculated)
    scs.cat_status_calculated,
    scs.bat_status_calculated,
    scs.bact_status_calculated,
    
    -- Priority
    s.cat_priority,
    s.bat_priority,
    s.bact_priority,
    
    -- Last sample dates (calculated)
    slsd.last_cat_sample_date_calc,
    slsd.last_bat_sample_date_calc,
    slsd.last_bact_sample_date_calc,
    
    -- Flag (calculated)
    sfc.site_flag_calculated AS site_flag
    
FROM sites s
LEFT JOIN waterbodies w ON s.waterbody_id = w.waterbody_id
LEFT JOIN site_subwatersheds ss ON s.site_code = ss.site_code
LEFT JOIN subwatersheds sw ON ss.subwatershed_id = sw.subwatershed_id
LEFT JOIN site_municipalities sm ON s.site_code = sm.site_code AND sm.is_primary = true
LEFT JOIN municipalities m ON sm.municipality_id = m.municipality_id
LEFT JOIN sites_calculated_status scs ON s.site_code = scs.site_code
LEFT JOIN sites_last_sample_dates_calculated slsd ON s.site_code = slsd.site_code
LEFT JOIN sites_flag_calculated sfc ON s.site_code = sfc.site_code
GROUP BY 
    s.site_code, s.is_active, s.groundtruthing_priority, s.groundtruthing_status,
    w.waterbody_name, w.waterbody_id, s.description, s.property_type, s.permission,
    m.city, m.state, m.municipality_id, s.walk_time, s.walk_distance, s.walk_gradient,
    s.water_access, s.additional_comments, s.environmental_hazards, s.parking_details,
    s.walking_directions, s.habitat_type, s.latitude, s.longitude, s.site_type,
    s.drainage_area, s.notes, s.map_link, scs.cat_status_calculated, scs.bat_status_calculated,
    scs.bact_status_calculated, s.cat_priority, s.bat_priority, s.bact_priority,
    slsd.last_cat_sample_date_calc, slsd.last_bat_sample_date_calc, slsd.last_bact_sample_date_calc,
    sfc.site_flag_calculated;

COMMENT ON VIEW sites_comprehensive IS 'Comprehensive view of sites with all lookups and calculated fields for form display';

-- ============================================================================
-- STEP 8: Create Trigger to Auto-Update site_flag
-- ============================================================================

-- Function to update site_flag when flags change
CREATE OR REPLACE FUNCTION update_site_flag()
RETURNS TRIGGER AS $$
BEGIN
    -- Update site_flag based on existence of unresolved flags
    UPDATE sites s
    SET site_flag = EXISTS (
        SELECT 1 FROM data_flags df 
        WHERE df.table_name = 'sites' 
          AND df.record_id::text = s.site_code
          AND df.resolved = false
    )
    WHERE s.site_code = NEW.record_id::text OR s.site_code = OLD.record_id::text;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on data_flags table (if it exists)
-- Note: This will only work if data_flags table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'data_flags') THEN
        DROP TRIGGER IF EXISTS trigger_update_site_flag ON data_flags;
        CREATE TRIGGER trigger_update_site_flag
        AFTER INSERT OR UPDATE OR DELETE ON data_flags
        FOR EACH ROW
        WHEN (NEW.table_name = 'sites' OR OLD.table_name = 'sites')
        EXECUTE FUNCTION update_site_flag();
    END IF;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check new fields exist
SELECT 
    column_name, 
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'sites'
  AND column_name IN ('notes', 'site_flag', 'map_link', 'last_bact_sample_date', 'waterbody_id')
ORDER BY column_name;

-- Check lookup tables populated
SELECT 'waterbodies' as table_name, COUNT(*) as count FROM waterbodies
UNION ALL
SELECT 'subwatersheds', COUNT(*) FROM subwatersheds;

-- Check junction tables
SELECT 'site_subwatersheds' as table_name, COUNT(*) as count FROM site_subwatersheds
UNION ALL
SELECT 'site_municipalities', COUNT(*) FROM site_municipalities;

-- Check VIEWs exist
SELECT table_name 
FROM information_schema.views
WHERE table_schema = 'public'
  AND table_name LIKE 'sites%'
ORDER BY table_name;

COMMIT;

-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. Old VARCHAR columns (waterbody, subwatershed) are kept for now
--    Can be removed after verifying FK relationships work correctly
-- 2. municipality_id in sites table is kept for primary municipality
--    Additional municipalities can be added via site_municipalities junction table
-- 3. Calculated fields are available via VIEWs
--    Stored fields (cat_status, etc.) can be kept for performance or removed
-- 4. site_flag trigger requires data_flags table to exist
--    If it doesn't exist yet, the trigger creation is skipped
-- ============================================================================
