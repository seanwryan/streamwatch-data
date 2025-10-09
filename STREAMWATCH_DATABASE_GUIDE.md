# StreamWatch Database - Complete Guide
**For: Watershed Institute Team**

---

## 🎯 **Project Overview**

This project transforms 32+ years of StreamWatch environmental monitoring data from Excel files into a PostgreSQL database hosted on Neon cloud. The database is fully loaded and ready for data validation, analysis, and reporting.

**Data includes:**
- **168 monitoring sites** with GPS coordinates and metadata
- **16,909 water quality samples** (1992-2024) with pH, temperature, dissolved oxygen, etc.
- **691 bacteria test results** (E.coli data from 2025)
- **7,339 macroinvertebrate records** (bug collection data)
- **149 taxonomy records** (bug identification reference)
- **428 volunteer records** with training status

**Total: 25,684 records** across 6 tables

---

## 🚀 **Quick Start**

### **1. Download DBeaver (Recommended)**
- Go to https://dbeaver.io/
- Download free Community Edition
- Install and open

### **2. Connect to Database**
- Click "New Database Connection" → "PostgreSQL"
- **Host:** `ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech`
- **Port:** `5432`
- **Database:** `neondb`
- **Username:** `streamwatch_edit` (for full access)
- **Password:** `streamwatch_edit_2024`
- **SSL:** Check "Use SSL"
- Test connection → Finish

### **3. Start Exploring**
- Expand connection → `neondb` → `Schemas` → `public` → `Tables`
- Right-click any table → "View Data"
- Use the SQL editor to run queries

---

## 🔑 **Database Access**

### **Edit User (Full Access)**
- **Username:** `streamwatch_edit`
- **Password:** `streamwatch_edit_2024`
- **Permissions:** Read, write, create, delete

### **Read-Only User (View Only)**
- **Username:** `streamwatch_readonly`
- **Password:** `streamwatch_readonly_2024`
- **Permissions:** Read only

### **Connection String:**
```
postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require
```

---

## 📊 **Database Contents**

| Table | Records | Description |
|-------|---------|-------------|
| **sites** | 168 | Monitoring site locations and metadata |
| **samples** | 16,909 | Water quality measurements |
| **bacteria** | 691 | E.coli and bacteria test results |
| **bugs** | 7,339 | Macroinvertebrate (bug) collection data |
| **taxonomy** | 149 | Bug identification reference data |
| **volunteers** | 428 | Volunteer information and training status |

**Total Records:** 25,684

---

## 🛠️ **Alternative Access Methods**

### **Method 1: pgAdmin**
- Download from https://www.pgadmin.org/
- Create new server with same connection details
- Use desktop app, not web version

### **Method 2: Command Line (psql)**
```bash
psql "postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"
```

### **Method 3: Python Scripts**
```python
import pandas as pd
from sqlalchemy import create_engine

# Connect to database
engine = create_engine("postgresql://streamwatch_edit:streamwatch_edit_2024@ep-wild-rice-ad71vs5v-pooler.c-2.us-east-1.aws.neon.tech:5432/neondb?sslmode=require")

# Run a query
df = pd.read_sql("SELECT * FROM sites LIMIT 5", engine)
print(df)
```

---

## 🔍 **Understanding the Database Tables**

### **1. sites**
- **What it contains:** All monitoring locations
- **Key fields:** site_code, waterbody, latitude, longitude, is_active
- **Example:** Site "AC7" on Assunpink Creek at coordinates 40.218, -74.560

### **2. samples**
- **What it contains:** Water quality measurements
- **Key fields:** sample_id, site_code, sample_date, water_temperature, ph, do_ppm
- **Example:** Sample from site "AC7" on 2023-05-15 with temperature 18.5°C

### **3. bugs**
- **What it contains:** Macroinvertebrate (bug) counts
- **Key fields:** bug_record_id, sample_code, order_name, family, count
- **Example:** 5 mayflies (Ephemeroptera) found in sample "AC7_20230515"

### **4. bacteria**
- **What it contains:** Bacteria test results
- **Key fields:** bacteria_record_id, sample_code, site_code, e_coli
- **Example:** E. coli test result for site "AC7" on 2023-05-15

### **5. volunteers**
- **What it contains:** Volunteer information
- **Key fields:** volunteer_id, first_name, last_name, email, active_cat, active_bat
- **Example:** Volunteer "John Smith" who is active for CAT sampling

### **6. taxonomy**
- **What it contains:** Bug identification reference
- **Key fields:** family, genus_species, ept, tolerance
- **Example:** Reference data for identifying bug families

---

## 📋 **Essential SQL Queries**

### **Basic Data Exploration:**

```sql
-- Count records in each table
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
```

```sql
-- View first 5 sites with GPS coordinates
SELECT site_code, waterbody, latitude, longitude, is_active
FROM sites 
WHERE latitude IS NOT NULL AND longitude IS NOT NULL
ORDER BY site_code
LIMIT 5;
```

```sql
-- Recent bacteria test results
SELECT site_code, collection_date, e_coli, measurement_value
FROM bacteria 
WHERE collection_date IS NOT NULL
ORDER BY collection_date DESC
LIMIT 10;
```

### **Data Quality Checks:**

```sql
-- Sites missing GPS coordinates
SELECT site_code, waterbody, description
FROM sites 
WHERE latitude IS NULL OR longitude IS NULL
ORDER BY site_code;
```

```sql
-- Invalid temperature values
SELECT sample_id, site_code, water_temperature
FROM samples
WHERE water_temperature < 0 OR water_temperature > 40;
```

```sql
-- Invalid pH values
SELECT sample_id, site_code, ph
FROM samples
WHERE ph < 0 OR ph > 14;
```

### **Analysis Queries:**

```sql
-- E.coli levels by site (average)
SELECT site_code, 
       COUNT(*) as test_count,
       AVG(e_coli) as avg_e_coli,
       MAX(e_coli) as max_e_coli
FROM bacteria 
WHERE e_coli IS NOT NULL
GROUP BY site_code
ORDER BY avg_e_coli DESC
LIMIT 10;
```

```sql
-- Most common bug families
SELECT family, COUNT(*) as bug_count
FROM bugs 
WHERE family IS NOT NULL
GROUP BY family
ORDER BY bug_count DESC
LIMIT 10;
```

```sql
-- Water quality trends by year
SELECT 
    EXTRACT(YEAR FROM sample_date) as year,
    AVG(water_temperature) as avg_temp,
    COUNT(*) as sample_count
FROM samples
WHERE water_temperature IS NOT NULL
GROUP BY EXTRACT(YEAR FROM sample_date)
ORDER BY year;
```

### **Search Queries:**

```sql
-- Search for sites by waterbody name
SELECT site_code, waterbody, latitude, longitude
FROM sites 
WHERE UPPER(waterbody) LIKE '%ASSUNPINK%'
ORDER BY site_code;
```

```sql
-- Find volunteers by name
SELECT volunteer_id, first_name, last_name, email, active_cat, active_bat
FROM volunteers 
WHERE UPPER(first_name) LIKE '%JOHN%' OR UPPER(last_name) LIKE '%SMITH%'
ORDER BY last_name, first_name;
```

---

## 🛠️ **How to Edit Data**

### **Visual/Grid Editing (Easiest)**
**In DBeaver:**
- Right-click any table → "View Data"
- Click on any cell to edit directly
- Press Enter to save changes
- Very Excel-like experience!

**In pgAdmin:**
- Right-click table → "View/Edit Data" → "All Rows"
- Click on cells to edit
- Use the "Save" button to commit changes

### **SQL Queries (Most Powerful)**
```sql
-- Update specific records
UPDATE sites 
SET waterbody = 'UPDATED RIVER NAME' 
WHERE site_code = 'SB2';

-- Insert new records
INSERT INTO sites (site_code, waterbody, is_active) 
VALUES ('NEW1', 'NEW RIVER', true);

-- Delete records
DELETE FROM samples 
WHERE sample_date < '2020-01-01';
```

### **Import/Export (Bulk Operations)**
**Export to Excel:**
- Right-click table → "Export Data"
- Choose Excel format
- Edit in Excel, then re-import

**Import from Excel:**
- Right-click table → "Import Data"
- Choose your Excel file
- Map columns and import

---

## 🛡️ **Security & Best Practices**

### **User Permissions:**
- **Use read-only user** for data exploration and analysis
- **Use edit user** only when you need to modify data
- **Never share passwords** in emails or documents

### **Data Validation:**
- Always verify data quality before making corrections
- Test queries on small datasets first
- Keep backups of important changes

### **Connection Security:**
- All connections use SSL encryption
- Database is hosted on secure cloud infrastructure
- Access is logged and monitored

---

## 🆘 **Troubleshooting**

### **Common Issues:**

#### **Connection Failed:**
- Check internet connection
- Verify credentials are correct
- Ensure SSL mode is set to "require"

#### **Permission Denied:**
- Make sure you're using the correct user account
- Read-only user cannot modify data (this is expected)

#### **Query Errors:**
- Check table and column names are correct
- Use the example queries as templates
- Start with simple queries and build complexity

### **Getting Help:**
- Check the example queries file (`example_queries_for_team.sql`)
- Test with the connection test script (`test_team_access.py`)
- Contact the technical team for advanced issues

---

## 📈 **Current Status**

### **✅ Completed:**
- ✅ Neon PostgreSQL database created and configured
- ✅ All 6 tables created with proper schema
- ✅ 25,684 records loaded successfully
- ✅ Read-only and edit users created
- ✅ Connection tested and verified
- ✅ Documentation created

### **🎯 Ready for:**
- Data validation by the Watershed team
- Data quality checks and corrections
- Analysis and reporting
- Dashboard development

---

## The database is fully operational with 32+ years of StreamWatch data. The Watershed team can now:

1. **Connect** using DBeaver or pgAdmin
2. **Explore** all the data tables
3. **Validate** data quality
4. **Make corrections** as needed
5. **Analyze** trends and patterns
6. **Export** data for reports

---

*Last updated: October 2025*
