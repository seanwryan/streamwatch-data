# Sites Table Requirements Completion Scripts

## Overview

These scripts complete the implementation of the SITES Table Schema requirements by adding all missing pieces identified in the review.

## Files

- `complete_sites_requirements.sql` - SQL script (run in DBeaver or psql)
- `complete_sites_requirements.py` - Python script (run from command line)

## What These Scripts Do

### 1. Add Missing Fields
- `notes` - TEXT field for general site notes
- `site_flag` - BOOLEAN field (auto-calculated from flag table)
- `map_link` - VARCHAR(500) for Google Maps URL
- `last_bact_sample_date` - DATE field

### 2. Create Lookup Tables
- `waterbodies` - Lookup table for waterbodies
- `subwatersheds` - Lookup table for subwatersheds

### 3. Create Junction Tables
- `site_subwatersheds` - Many-to-many relationship (sites ↔ subwatersheds)
- `site_municipalities` - Many-to-many relationship (sites ↔ municipalities)

### 4. Migrate Data
- Populates lookup tables from existing VARCHAR data
- Converts `waterbody` VARCHAR to `waterbody_id` FK
- Converts `subwatershed` VARCHAR to junction table entries
- Migrates existing `municipality_id` to junction table

### 5. Create VIEWs
- `sites_calculated_status` - Calculated CAT/BAT/BACT status
- `sites_last_sample_dates_calculated` - Calculated last sample dates
- `sites_flag_calculated` - Calculated site_flag
- `sites_comprehensive` - Complete view for forms

### 6. Create Triggers
- Auto-update `site_flag` when flags change (if data_flags table exists)

## How to Run

### Option 1: SQL Script (DBeaver)

1. Open DBeaver
2. Connect with **database owner credentials** (not streamwatch_edit)
3. Open `complete_sites_requirements.sql`
4. Run the entire script (or step by step)
5. Check verification queries at the end

### Option 2: Python Script

```bash
# Make sure you're in the project root
cd /path/to/streamwatch-data

# Run the script
python3 scripts/schema/complete_sites_requirements.py
```

**Note:** Requires database owner credentials in `.env` file.

## Prerequisites

- Database owner credentials (needed for ALTER TABLE, CREATE TABLE, etc.)
- Existing `sites` table with data
- Existing `municipalities` table (created by Angelo's script)
- `samples` and `bacteria` tables (for calculated date VIEWs)

## What Gets Changed

### Tables Modified
- `sites` - Adds 4 new columns, adds `waterbody_id` FK

### Tables Created
- `waterbodies`
- `subwatersheds`
- `site_subwatersheds`
- `site_municipalities`

### VIEWs Created
- `sites_calculated_status`
- `sites_last_sample_dates_calculated`
- `sites_flag_calculated`
- `sites_comprehensive`

### What's Preserved
- Old VARCHAR columns (`waterbody`, `subwatershed`) are **kept** for now
- Can be removed later after verifying FK relationships work
- Existing `municipality_id` in sites table is kept (for primary municipality)

## Verification

After running, check:

```sql
-- New fields exist
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'sites' 
  AND column_name IN ('notes', 'site_flag', 'map_link', 'last_bact_sample_date');

-- Lookup tables populated
SELECT COUNT(*) FROM waterbodies;
SELECT COUNT(*) FROM subwatersheds;

-- Junction tables have data
SELECT COUNT(*) FROM site_subwatersheds;
SELECT COUNT(*) FROM site_municipalities;

-- VIEWs work
SELECT * FROM sites_comprehensive LIMIT 5;
```

## Rollback

If you need to rollback:

```sql
-- Drop VIEWs
DROP VIEW IF EXISTS sites_comprehensive;
DROP VIEW IF EXISTS sites_flag_calculated;
DROP VIEW IF EXISTS sites_last_sample_dates_calculated;
DROP VIEW IF EXISTS sites_calculated_status;

-- Drop junction tables
DROP TABLE IF EXISTS site_municipalities;
DROP TABLE IF EXISTS site_subwatersheds;

-- Drop lookup tables (only if no other references)
DROP TABLE IF EXISTS subwatersheds;
DROP TABLE IF EXISTS waterbodies;

-- Remove columns from sites
ALTER TABLE sites DROP COLUMN IF EXISTS waterbody_id;
ALTER TABLE sites DROP COLUMN IF EXISTS last_bact_sample_date;
ALTER TABLE sites DROP COLUMN IF EXISTS map_link;
ALTER TABLE sites DROP COLUMN IF EXISTS site_flag;
ALTER TABLE sites DROP COLUMN IF EXISTS notes;
```

## Next Steps

1. **Test the VIEWs** - Make sure calculated fields work correctly
2. **Populate map_link** - Add Google Maps URLs for sites
3. **Verify junction tables** - Check many-to-many relationships
4. **Consider removing old columns** - After verifying FK relationships work
5. **Update forms** - Use `sites_comprehensive` VIEW for form display

## Related Documentation

- `docs/SITES_TABLE_REVIEW.md` - Complete review of requirements vs implementation
- `docs/GIT_WORKFLOW_GUIDE.md` - How to merge branches
