# Sites Table Implementation Review

**Date:** December 2025  
**Branch:** `sites-table`  
**Reviewer:** Sean Ryan  
**Source:** SITES Table Schema Requirements Document

---

## Executive Summary

Angelo has implemented a significant portion of the sites table requirements, including:
- ✅ Municipalities table creation and linking
- ✅ Core site fields
- ✅ Status constraints and data cleaning
- ⚠️ Missing: Waterbodies table, Subwatersheds table, several calculated fields, and some new fields

---

## ✅ COMPLETED REQUIREMENTS

### 1. Core Header Fields
- ✅ `site_code` - VARCHAR(20) PRIMARY KEY, unique and indexed
- ✅ `is_active` - BOOLEAN (Yes/No)

### 2. Groundtruthing Fields
- ✅ `groundtruthing_priority` - VARCHAR(50)
- ✅ `groundtruthing_status` - VARCHAR(50)

### 3. Location Fields
- ✅ `latitude` - DECIMAL(10,8)
- ✅ `longitude` - DECIMAL(11,8)
- ✅ `description` - TEXT
- ✅ `drainage_area` - DECIMAL(10,2)

### 4. Ownership Fields
- ✅ `property_type` - VARCHAR(50) (dropdown: public, private, TWI)
- ✅ `permission` - VARCHAR(50) (short text field)

### 5. Access Fields
- ✅ `walk_time` - VARCHAR(50)
- ✅ `walk_distance` - VARCHAR(50)
- ✅ `walk_gradient` - VARCHAR(50)
- ✅ `water_access` - VARCHAR(50)
- ✅ `additional_comments` - TEXT
- ✅ `environmental_hazards` - TEXT
- ✅ `parking_details` - TEXT
- ✅ `walking_directions` - TEXT

### 6. Additional Info Fields
- ✅ `habitat_type` - VARCHAR(50) (dropdown: High Gradient, Low Gradient, Canal, Lake)
- ✅ `site_type` - VARCHAR(50) (dropdown: HUC, Target, Project, Legacy, MUNI, V.Req)

### 7. Status Fields (Priority)
- ✅ `cat_priority` - VARCHAR(50) (dropdown: 1 - Priority, 2 - Secondary, 3 - Tertiary, 4 - Retired/Inactive)
- ✅ `bat_priority` - VARCHAR(50)
- ✅ `bact_priority` - VARCHAR(50)

### 8. Status Fields (Status - Stored)
- ✅ `cat_status` - VARCHAR(50) with CHECK constraint (Active, Inactive, Proposed, Unknown)
- ✅ `bat_status` - VARCHAR(50) with CHECK constraint
- ✅ `bact_status` - VARCHAR(50) with CHECK constraint

### 9. Status Fields (Last Sample Dates - Stored)
- ✅ `last_cat_sample_date` - DATE
- ✅ `last_bat_sample_date` - DATE
- ⚠️ `last_bact_sample_date` - **MISSING** (not in schema)

### 10. Municipalities Integration
- ✅ `municipalities` table created
- ✅ `municipality_id` column added to sites table
- ✅ Foreign key constraint `fk_sites_municipality` created
- ✅ Data populated from volunteers table

### 11. Data Quality
- ✅ Status value standardization (Vacant → Active, Retired → Inactive, etc.)
- ✅ CHECK constraints on status fields
- ✅ Data cleaning in loader script

### 12. Deleted Fields (As Required)
- ✅ `site_name` - Not in schema (correctly deleted)
- ✅ `elevation` - Not in schema (correctly deleted)
- ✅ `watershed` - Not in schema (correctly deleted) - **BUT** appears in VIEW

---

## ⚠️ PARTIALLY IMPLEMENTED / NEEDS WORK

### 1. Waterbody Lookup
- ⚠️ `waterbody` field exists as VARCHAR(100) - **NOT a lookup**
- ❌ **MISSING**: `waterbodies` table
- ❌ **MISSING**: Foreign key constraint
- **Requirement**: Should be lookup/dropdown connected to waterbodies table
- **Action Needed**: Create `waterbodies` table and convert `waterbody` to FK

### 2. Subwatershed Lookup
- ⚠️ `subwatershed` field exists as VARCHAR(100) - **NOT a lookup**
- ❌ **MISSING**: `subwatersheds` table
- ❌ **MISSING**: Foreign key constraint
- ❌ **MISSING**: Many-to-many relationship (requirement says "select more than one")
- **Requirement**: Should be lookup/dropdown with option to select multiple
- **Action Needed**: 
  - Create `subwatersheds` table
  - Create junction table `site_subwatersheds` for many-to-many relationship
  - Remove `subwatershed` column from sites table

### 3. Municipality Lookup
- ✅ `municipality_id` exists with FK constraint
- ⚠️ **ISSUE**: Requirement says "option to select more than one" - currently single FK
- **Action Needed**: 
  - Create junction table `site_municipalities` for many-to-many relationship
  - Remove `municipality_id` column from sites table

### 4. Calculated Status Fields (Should NOT be stored)
- ⚠️ `cat_status`, `bat_status`, `bact_status` are **STORED** in table
- **Requirement**: These should be **calculated fields** that show on form but don't need to be stored
- **Current**: Stored with CHECK constraints
- **Action Needed**: 
  - Create VIEWs for calculated status (based on sample dates, priorities, etc.)
  - Keep stored fields for now OR remove and calculate via VIEWs

### 5. Calculated Last Sample Date Fields
- ⚠️ `last_cat_sample_date`, `last_bat_sample_date` are **STORED** in table
- ❌ `last_bact_sample_date` - **MISSING** entirely
- **Requirement**: These should be **calculated fields** that show on form but don't need to be stored
- **Action Needed**: 
  - Create VIEWs that calculate from samples/bacteria tables
  - Remove stored date columns OR keep for performance

---

## ❌ MISSING REQUIREMENTS

### 1. New Fields Not Yet Added
- ❌ `notes` - TEXT field for general notes about the site
- ❌ `site_flag` - BOOLEAN field automatically calculated based on flag table
- ❌ `map_link` - VARCHAR/URL field for Google Maps link
- ❌ `last_bact_sample_date` - DATE field (missing from schema)

### 2. Missing Tables
- ❌ `waterbodies` table
- ❌ `subwatersheds` table
- ❌ Junction tables for many-to-many relationships:
  - `site_subwatersheds`
  - `site_municipalities` (if multiple municipalities per site)

### 3. Missing Calculated Fields (VIEWs)
- ❌ VIEW for `cat_status` (calculated)
- ❌ VIEW for `bat_status` (calculated)
- ❌ VIEW for `bact_status` (calculated)
- ❌ VIEW for `last_cat_sample_date` (calculated)
- ❌ VIEW for `last_bat_sample_date` (calculated)
- ❌ VIEW for `last_bact_sample_date` (calculated)
- ❌ VIEW/trigger for `site_flag` (calculated from flag table)

### 4. Missing Constraints/Validation
- ⚠️ Required fields (site_code, is_active) - no NOT NULL constraints (intentional for existing data)
- ⚠️ Form-level validation needed for required fields

---

## 📋 DETAILED FIELD COMPARISON

| Requirement | Field Name | Status | Notes |
|------------|------------|--------|-------|
| **Header** | | | |
| Site_code | `site_code` | ✅ | VARCHAR(20) PK, unique, indexed |
| Is_active | `is_active` | ✅ | BOOLEAN |
| **Groundtruthing** | | | |
| Groundtruthing_priority | `groundtruthing_priority` | ✅ | VARCHAR(50) |
| Groundtruthing_status | `groundtruthing_status` | ✅ | VARCHAR(50) |
| **Location** | | | |
| Waterbody | `waterbody` | ⚠️ | VARCHAR(100) - should be FK lookup |
| Subwatershed | `subwatershed` | ⚠️ | VARCHAR(100) - should be FK lookup (many-to-many) |
| Description | `description` | ✅ | TEXT |
| Latitude | `latitude` | ✅ | DECIMAL(10,8) |
| Longitude | `longitude` | ✅ | DECIMAL(11,8) |
| **Ownership** | | | |
| Property_type | `property_type` | ✅ | VARCHAR(50) |
| Permission | `permission` | ✅ | VARCHAR(50) |
| Municipality | `municipality_id` | ⚠️ | FK - should support multiple |
| **Access** | | | |
| Walk_time | `walk_time` | ✅ | VARCHAR(50) |
| Walk_distance | `walk_distance` | ✅ | VARCHAR(50) |
| Walk_gradient | `walk_gradient` | ✅ | VARCHAR(50) |
| Water_access | `water_access` | ✅ | VARCHAR(50) |
| Additional_comments | `additional_comments` | ✅ | TEXT |
| Environmental_hazards | `environmental_hazards` | ✅ | TEXT |
| Parking_details | `parking_details` | ✅ | TEXT |
| Walking_directions | `walking_directions` | ✅ | TEXT |
| **Additional Info** | | | |
| Habitat_type | `habitat_type` | ✅ | VARCHAR(50) |
| Site_type | `site_type` | ✅ | VARCHAR(50) |
| Drainage-area | `drainage_area` | ✅ | DECIMAL(10,2) |
| Notes | `notes` | ❌ | **MISSING** - TEXT field needed |
| **Status** | | | |
| CAT_priority | `cat_priority` | ✅ | VARCHAR(50) |
| CAT_status | `cat_status` | ⚠️ | Stored - should be calculated |
| Last_CAT_sample_date | `last_cat_sample_date` | ⚠️ | Stored - should be calculated |
| BAT_priority | `bat_priority` | ✅ | VARCHAR(50) |
| BAT_status | `bat_status` | ⚠️ | Stored - should be calculated |
| Last_BAT_sample_date | `last_bat_sample_date` | ⚠️ | Stored - should be calculated |
| BACT_priority | `bact_priority` | ✅ | VARCHAR(50) |
| BACT_status | `bact_status` | ⚠️ | Stored - should be calculated |
| Last_BACT_sample_date | `last_bact_sample_date` | ❌ | **MISSING** |
| **Header + Additional Info** | | | |
| Site_flag | `site_flag` | ❌ | **MISSING** - BOOLEAN, auto-calculated |
| Map_link | `map_link` | ❌ | **MISSING** - URL field |
| **Delete** | | | |
| Site_name | - | ✅ | Correctly deleted |
| Elevation | - | ✅ | Correctly deleted |
| Watershed | - | ✅ | Deleted (but in VIEW) |

---

## 🔧 RECOMMENDED ACTIONS

### Priority 1: Critical Missing Fields
1. **Add `notes` field** - TEXT column for general site notes
2. **Add `last_bact_sample_date`** - DATE field (or calculate via VIEW)
3. **Add `site_flag`** - BOOLEAN field with auto-calculation logic
4. **Add `map_link`** - VARCHAR(500) or TEXT for Google Maps URL

### Priority 2: Lookup Tables
1. **Create `waterbodies` table**
   ```sql
   CREATE TABLE waterbodies (
       waterbody_id SERIAL PRIMARY KEY,
       waterbody_name VARCHAR(100) NOT NULL UNIQUE,
       created_date TIMESTAMP DEFAULT NOW()
   );
   ```
2. **Create `subwatersheds` table**
   ```sql
   CREATE TABLE subwatersheds (
       subwatershed_id SERIAL PRIMARY KEY,
       subwatershed_name VARCHAR(100) NOT NULL UNIQUE,
       created_date TIMESTAMP DEFAULT NOW()
   );
   ```
3. **Create junction tables for many-to-many**
   ```sql
   CREATE TABLE site_subwatersheds (
       site_code VARCHAR(20) REFERENCES sites(site_code),
       subwatershed_id INTEGER REFERENCES subwatersheds(subwatershed_id),
       PRIMARY KEY (site_code, subwatershed_id)
   );
   
   CREATE TABLE site_municipalities (
       site_code VARCHAR(20) REFERENCES sites(site_code),
       municipality_id INTEGER REFERENCES municipalities(municipality_id),
       PRIMARY KEY (site_code, municipality_id)
   );
   ```

### Priority 3: Convert to Lookups
1. **Convert `waterbody` to FK**
   - Populate `waterbodies` table from existing data
   - Add `waterbody_id` column to sites
   - Migrate data
   - Remove `waterbody` VARCHAR column

2. **Convert `subwatershed` to many-to-many**
   - Populate `subwatersheds` table
   - Create junction table entries
   - Remove `subwatershed` VARCHAR column

3. **Convert `municipality_id` to many-to-many** (if needed)
   - Create junction table entries
   - Keep `municipality_id` for primary municipality OR remove if truly many-to-many

### Priority 4: Calculated Fields (VIEWs)
1. **Create VIEWs for calculated status fields**
   ```sql
   CREATE VIEW sites_calculated_status AS
   SELECT 
       site_code,
       -- Calculate CAT status based on last sample date, priority, etc.
       CASE 
           WHEN last_cat_sample_date > CURRENT_DATE - INTERVAL '1 year' THEN 'Active'
           WHEN cat_priority = '4 - Retired/Inactive' THEN 'Inactive'
           ELSE 'Unknown'
       END AS cat_status_calculated,
       -- Similar for BAT and BACT
   FROM sites;
   ```

2. **Create VIEWs for last sample dates**
   ```sql
   CREATE VIEW sites_last_sample_dates AS
   SELECT 
       s.site_code,
       MAX(CASE WHEN sa.sample_date IS NOT NULL THEN sa.sample_date END) AS last_cat_sample_date,
       MAX(CASE WHEN ba.collection_date IS NOT NULL THEN ba.collection_date END) AS last_bact_sample_date
   FROM sites s
   LEFT JOIN samples sa ON s.site_code = sa.site_code
   LEFT JOIN bacteria ba ON s.site_code = ba.site_code
   GROUP BY s.site_code;
   ```

3. **Create trigger/VIEW for `site_flag`**
   - Need to clarify what "flag table" is
   - Create trigger or computed column based on related records

### Priority 5: Form Requirements
1. **Related data display** - Ensure queries available for:
   - Related visits (samples)
   - Site assignments (volunteer_assignments)
   - Map/images (need to determine storage location)

---

## 📝 QUESTIONS FOR CLARIFICATION

1. **Flag Table**: What is the "flag table" that `site_flag` should reference? Is it:
   - The `data_flags` table (currently for samples/bacteria/bugs)?
   - A new `site_flags` table?
   - Something else?

2. **Many-to-Many Municipalities**: Do sites really need multiple municipalities, or is one primary municipality sufficient?

3. **Stored vs Calculated**: Should status and last sample date fields be:
   - **Option A**: Stored in table (current approach) - faster queries, but data can get stale
   - **Option B**: Calculated via VIEWs - always accurate, but slower queries
   - **Option C**: Hybrid - stored with triggers to keep updated

4. **Waterbodies Data**: Is there existing data to populate the `waterbodies` table, or should it be populated from current `waterbody` values?

5. **Subwatersheds Data**: Same question - populate from current `subwatershed` values?

6. **Map/Images Storage**: Where should map links and site images be stored?
   - In database as URLs?
   - In file system with paths in database?
   - External service (e.g., Google Drive, S3)?

---

## 📊 IMPLEMENTATION STATUS SUMMARY

| Category | Complete | Partial | Missing | Total |
|----------|----------|---------|---------|-------|
| Core Fields | 2 | 0 | 0 | 2 |
| Groundtruthing | 2 | 0 | 0 | 2 |
| Location Fields | 4 | 2 | 0 | 6 |
| Ownership Fields | 2 | 1 | 0 | 3 |
| Access Fields | 8 | 0 | 0 | 8 |
| Additional Info | 3 | 0 | 1 | 4 |
| Status Fields | 6 | 3 | 1 | 10 |
| New Fields | 0 | 0 | 3 | 3 |
| Lookup Tables | 1 | 0 | 2 | 3 |
| **TOTAL** | **28** | **6** | **7** | **41** |

**Completion Rate: ~68% (28/41 fully complete, 6/41 partial)**

---

## ✅ NEXT STEPS

1. **Review with Angelo** - Discuss missing fields and lookup table approach
2. **Clarify requirements** - Answer questions above
3. **Create missing tables** - waterbodies, subwatersheds, junction tables
4. **Add missing fields** - notes, site_flag, map_link, last_bact_sample_date
5. **Implement calculated fields** - VIEWs or triggers for status and dates
6. **Test data migration** - Convert existing VARCHAR fields to FK relationships
7. **Update documentation** - Schema status, relationships, form requirements

---

**Review completed by:** Sean Ryan  
**Date:** December 2025
