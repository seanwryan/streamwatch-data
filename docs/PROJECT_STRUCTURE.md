# StreamWatch Database Project Structure

## Directory Organization

```
streamwatch-data/
├── README.md                          # Project overview
├── config.py                          # Database configuration
├── requirements.txt                    # Python dependencies
├── env.example                        # Environment variables template
│
├── data/
│   ├── raw/                           # Original Excel files (10 files)
│   └── processed/                      # Cleaned/processed data files
│
├── scripts/
│   ├── etl/                           # Data loading scripts
│   │   ├── create_schema.py          # Create initial 6 core tables
│   │   ├── create_additional_tables.py  # Create 8 additional tables
│   │   ├── load_*.py                 # Table-specific loaders
│   │   └── clean_bacteria_data.py     # Bacteria data cleaning
│   │
│   ├── schema/                        # Schema modification scripts
│   │   ├── align_database_with_schema.py
│   │   ├── align_volunteers_with_watershed_requirements.sql
│   │   ├── create_volunteer_views.sql
│   │   └── fix_volunteers_table.py/sql  # Original fix (reference)
│   │
│   ├── fixes/                         # Data quality fixes
│   │   ├── fix_bugs_table.py
│   │   ├── fix_sample_code_mismatches.py
│   │   ├── clean_samples_table.py
│   │   ├── run_all_fixes.py
│   │   └── test_fixes.py
│   │
│   ├── tools/                         # Utility scripts
│   │   ├── audit_volunteer_data.py
│   │   ├── populate_volunteer_assignments.py
│   │   ├── view_database.py
│   │   └── test_connection.py
│   │
│   └── visualization/                 # Dashboard/visualization
│       └── database_cleaning_dashboard.py
│
├── docs/                              # Current documentation
│   ├── STREAMWATCH_DATABASE_STATUS.md  # Schema reference
│   ├── STREAMWATCH_DATABASE_GUIDE.md  # Comprehensive guide
│   ├── DATABASE_RELATIONSHIPS.md      # Table relationships
│   ├── SCHEMA_REVIEW_AND_RECOMMENDATIONS.md
│   ├── VOLUNTEERS_STATUS_DEC5.md     # Meeting prep
│   ├── VOLUNTEERS_WATERSHED_REQUIREMENTS_CHECKLIST.md
│   ├── VOLUNTEER_TOOLS_README.md
│   └── SECURE_CREDENTIALS.md
```

## Key Scripts by Purpose

### Schema Creation
- `scripts/etl/create_schema.py` - Initial 6 core tables
- `scripts/etl/create_additional_tables.py` - 8 additional tables
- `scripts/schema/align_volunteers_with_watershed_requirements.sql` - Volunteers table alignment

### Data Loading
- `scripts/etl/load_volunteer_data.py` - Main volunteer loader
- `scripts/etl/load_training_data.py` - Training records
- `scripts/etl/load_volunteer_assignments_data.py` - Site assignments
- `scripts/etl/load_bacteria_data_final.py` - Final bacteria loader
- `scripts/etl/load_*.py` - Other table loaders

### Data Quality
- `scripts/fixes/run_all_fixes.py` - Master fix script
- `scripts/tools/audit_volunteer_data.py` - Data audit

### Database Management
- `scripts/etl/create_edit_user.py` - Create edit user
- `scripts/etl/create_readonly_user.py` - Create readonly user

## Documentation

**Current/Active:**
- `docs/STREAMWATCH_DATABASE_STATUS.md` - Current schema reference
- `docs/VOLUNTEERS_WATERSHED_REQUIREMENTS_CHECKLIST.md` - Volunteers alignment status
- `docs/VOLUNTEERS_STATUS_DEC5.md` - Meeting preparation

## Data Files

**Raw Data (10 Excel files):**
- Volunteer_Tracking.xlsm
- All StreamWatch Data.xlsx
- BACT and HAB 2025 Data.xlsx
- And 7 others...

**Processed:**
- cleaned_bacteria_data.csv

