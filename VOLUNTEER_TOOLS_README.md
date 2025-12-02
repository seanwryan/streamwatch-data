# Volunteer Management Tools

Quick reference for managing volunteer data in the StreamWatch database.

## Available Tools

### 1. Audit Volunteer Data
**Purpose:** Get a comprehensive report on volunteer data quality and completeness

**Run:**
```bash
python3 scripts/tools/audit_volunteer_data.py
```

**What it shows:**
- Total volunteer count
- Data completeness for each field
- Training status breakdown
- Active program participation (CAT/BAT/BACT)
- Geographic distribution
- Data quality issues (duplicates, invalid data)
- Relationship table status

---

### 2. Populate Volunteer Assignments
**Purpose:** Migrate volunteer-site assignments to the new junction table

**Run:**
```bash
python3 scripts/tools/populate_volunteer_assignments.py
```

**What it does:**
- Checks for site_code column in volunteers table
- Creates assignment records in volunteer_assignments table
- Verifies results and shows sample data

**Note:** Only needs to be run once to migrate existing data

---

### 3. Create Relationship Tables
**Purpose:** Create the three new volunteer relationship tables

**Run:**
```bash
python3 scripts/schema/create_volunteer_relationships.py
```

**What it creates:**
- `training` - Volunteer training records
- `volunteer_assignments` - Volunteer ↔ Site assignments
- `visit_attendance` - Volunteer ↔ Visit/Sample attendance

**Note:** Already executed, tables exist in database

---

## Current Database Status

**Volunteers Table:**
- 428 total volunteers
- 91.6% have email addresses
- 30.1% have phone numbers
- 62.1% are inactive
- 25.0% are active

**Relationship Tables:**
- `training`: 0 records (needs data)
- `volunteer_assignments`: 0 records (run populate script)
- `visit_attendance`: 0 records (needs data)

---

## Common Queries

### Find all active volunteers:
```sql
SELECT volunteer_id, first_name, last_name, email, training_status
FROM volunteers
WHERE training_status = 'Active'
ORDER BY last_name;
```

### Find volunteers by program:
```sql
-- Active BAT volunteers
SELECT volunteer_id, first_name, last_name, email
FROM volunteers
WHERE active_bat = true;

-- Active BACT volunteers
SELECT volunteer_id, first_name, last_name, email
FROM volunteers
WHERE active_bact = true;
```

### Find volunteers by city:
```sql
SELECT city, COUNT(*) as volunteer_count
FROM volunteers
WHERE city IS NOT NULL AND city != '' AND city != 'nan'
GROUP BY city
ORDER BY volunteer_count DESC;
```

### Find volunteers with missing data:
```sql
-- Missing phone numbers
SELECT volunteer_id, first_name, last_name, email
FROM volunteers
WHERE phone IS NULL OR phone = '' OR phone = 'nan';

-- Missing email addresses
SELECT volunteer_id, first_name, last_name
FROM volunteers
WHERE email IS NULL OR email = '' OR email = 'nan';
```

---

## Next Steps

1. **Run populate_volunteer_assignments.py** to migrate site assignments
2. **Find training data source** to populate training table
3. **Link volunteers to visits** to populate visit_attendance table
4. **Set up digital forms** for ongoing data collection

---

## Database Connection

**Edit Access (for modifications):**
```
Host: ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech
Port: 5432
Database: neondb
User: streamwatch_edit
Password: streamwatch_edit_2024
SSL: Required
```

**Read-Only Access (for viewing):**
```
Host: ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech
Port: 5432
Database: neondb
User: streamwatch_readonly
Password: streamwatch_readonly_2024
SSL: Required
```

---

## Questions?

See the full documentation:
- `docs/VOLUNTEERS_TABLE_STRUCTURE.md` - Table structure details
- `docs/DATABASE_RELATIONSHIPS.md` - How tables connect
- `implementation_plan.md` - Complete plan and next steps
- `walkthrough.md` - Summary of work completed
