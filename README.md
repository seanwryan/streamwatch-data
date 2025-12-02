# StreamWatch Database Project

PostgreSQL database for StreamWatch environmental monitoring data.

## Quick Start

1. **Setup:**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   pip install -r requirements.txt
   ```

2. **Database Connection:**
   - Edit access: `streamwatch_edit` user
   - Read-only access: `streamwatch_readonly` user
   - See `docs/SECURE_CREDENTIALS.md` for connection details

## Project Structure

- `scripts/etl/` - Data loading scripts
- `scripts/schema/` - Schema modification scripts
- `scripts/fixes/` - Data quality fixes
- `scripts/tools/` - Utility scripts
- `docs/` - Documentation
- `data/raw/` - Original Excel files
- `data/processed/` - Cleaned data files

## Key Documentation

- `docs/STREAMWATCH_DATABASE_STATUS.md` - Current schema reference
- `docs/VOLUNTEERS_WATERSHED_REQUIREMENTS_CHECKLIST.md` - Volunteers table status
- `docs/DATABASE_RELATIONSHIPS.md` - Table relationships
- `docs/PROJECT_STRUCTURE.md` - Detailed project organization

## Database Tables

**Core Tables (7):** sites, samples, bugs, bacteria, volunteers, taxonomy, chemical  
**Legacy Tables (8):** sample_dates, bug_results, rbp100_bugs, bug_list, cat_meters, cat_assignments, wqx_sites, wqx_biohabphys  
**System Tables (1):** users  
**Relationship Tables (3):** training, volunteer_assignments, visit_attendance

**Total: 19 tables**

## Current Status

- ✅ All 14 data tables loaded
- ✅ Volunteers table aligned with Watershed requirements
- ✅ Relationship tables populated (training: 167, assignments: 56)
- ✅ Data quality fixes applied

## For AI Context

See `for AI/` folder for complete project context package.
