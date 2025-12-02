# StreamWatch Database Project - AI Context Package

This folder contains all relevant files for understanding the StreamWatch database project, including scripts, documentation, raw data, and configuration files.

## Project Overview

The StreamWatch database is a PostgreSQL database that stores environmental monitoring data collected by volunteers. The project involved:
- Migrating data from Excel files to PostgreSQL
- Creating a schema with 15 tables (14 data tables + 1 users table)
- Cleaning and validating data
- Aligning the database structure with the original Access database design

## Folder Structure

### `/scripts/`
All Python scripts organized by purpose:
- **`etl/`** - Extract, Transform, Load scripts for initial data migration
  - `create_schema.py` - Creates initial 6 core tables
  - `create_additional_tables.py` - Creates 8 additional tables
  - `load_*.py` - Scripts to load data into specific tables
  - `clean_bacteria_data.py` - Special cleaning script for messy bacteria data
- **`fixes/`** - Scripts to fix data quality issues
  - `fix_bugs_table.py` - Populates calculated fields in bugs table
  - `fix_sample_code_mismatches.py` - Resolves foreign key violations
  - `clean_samples_table.py` - Cleans invalid data in samples table
  - `run_all_fixes.py` - Master script to run all fixes
- **`schema/`** - Scripts to modify database structure
  - `align_database_with_schema.py` - Adds missing columns and constraints
  - `fix_volunteers_table.py` - Aligns volunteers table with Access design
- **`tools/`** - Utility scripts for testing and exploration
- **`visualization/`** - Dashboard and visualization scripts

### `/docs/`
Documentation files:
- **`current/`** - Active documentation files
  - `STREAMWATCH_DATABASE_STATUS.md` - Current schema reference (table names, columns, data types)
  - `STREAMWATCH_DATABASE_GUIDE.md` - Comprehensive database guide
  - `DATABASE_RELATIONSHIPS.md` - Explanation of table relationships
  - `SCHEMA_REVIEW_AND_RECOMMENDATIONS.md` - Comparison with Access database plan
  - `VOLUNTEERS_TABLE_STRUCTURE.md` - Target structure for volunteers table
- **`archive/`** - Historical documentation (for reference)

### `/data/`
Data files:
- **`raw/`** - Original Excel files from Jian
  - `All StreamWatch Data.xlsx` - Main chemical data
  - `BACT and HAB 2025 Data.xlsx` - Bacteria and habitat data
  - `2025 BACT Analysis.xlsx` - Additional bacteria analysis
  - `BAT Data Consolidation and Recount - Lily Raphael.xlsx` - Bug count data
  - `BATSITES COLLECTED.xlsx` - Bug collection sites
  - `tblSampleDates.xlsx` - Sample date records
  - `CAT Meter Tracking.xlsx` - Equipment tracking
  - `Volunteer_Tracking.xlsm` - Volunteer information
  - `2025 StreamWatch Locations.xlsx` - Site locations
  - `2024 TWI WQX Submission.xlsx` - WQX submission data
  - `30 yr StreamWatch Data Analysis.xlsx` - Historical analysis
- **`processed/`** - Cleaned/processed data files
  - `cleaned_bacteria_data.csv` - Cleaned bacteria data

### `/config/`
Configuration and setup files:
- `config.py` - Database connection configuration
- `requirements.txt` - Python dependencies
- `env.example` - Environment variable template

### `/sql/`
SQL scripts:
- `fix_volunteers_table.sql` - SQL version of volunteers table fix
- `example_queries_for_team.sql` - Example queries for team use

## Database Structure

### Core Tables (7)
1. `sites` - Sampling site information
2. `samples` - Sample records (links sites to visits)
3. `bugs` - Macroinvertebrate count data
4. `bacteria` - E.coli bacteria test results
5. `volunteers` - Volunteer information
6. `taxonomy` - Bug taxonomy reference data
7. `chemical` - Water chemistry measurements

### Legacy/Supporting Tables (8)
8. `sample_dates` - Historical sample date records
9. `bug_results` - Bug analysis results
10. `rbp100_bugs` - RBP100 bug data
11. `bug_list` - Bug reference list
12. `cat_meters` - Equipment (CAT meters) tracking
13. `cat_assignments` - Meter assignments to volunteers
14. `wqx_sites` - WQX site information
15. `wqx_biohabphys` - WQX biological/habitat/physical data

### System Tables (1)
16. `users` - Database user management

## Key Features

- **Data Migration**: All data successfully migrated from Excel to PostgreSQL
- **Data Cleaning**: Comprehensive cleaning scripts for data quality issues
- **Schema Alignment**: Database structure aligned with Access database design
- **Foreign Key Relationships**: Referential integrity maintained across tables
- **Data Validation**: Check constraints and validation rules implemented

## Current Status

- All 14 data tables loaded with data
- Data quality fixes applied
- Schema aligned with documented structure
- Volunteers table structure being updated to match Access design
- Database ready for team review and further development

## Important Notes

- Database credentials are stored in `.env` file (not included for security)
- Use `env.example` as a template for environment variables
- All scripts use `config.py` for database connection
- Database is hosted on Neon PostgreSQL (cloud-hosted)
