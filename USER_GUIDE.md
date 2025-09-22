# StreamWatch Database - User Guide
**For: Watershed Institute Team and Interns**

---

## 🎯 **What This Guide Covers**

User Guide:
- Access the StreamWatch database
- Run basic queries to explore data
- Check data quality and completeness
- Validate data accuracy
- Use the database for analysis

---

## 🚀 **Getting Started**

### **Database Connection Info:**
- **Host:** localhost:5432
- **Database:** streamwatch
- **Username:** streamwatch_user
- **Password:** password

---

## 📱 **How to Access the Database**

### **Method 1: pgAdmin**

#### **Step 1: Download and Install pgAdmin**
1. Go to https://www.pgadmin.org/download/
2. Download pgAdmin for your operating system
3. Install the application
4. **Important:** Use the desktop app, not the web version

#### **Step 2: Connect to the Database**
1. Open pgAdmin
2. Right-click "Servers" in the left panel
3. Select "Create" → "Server"
4. Fill in the connection details:
   - **Name:** StreamWatch (or any name you prefer)
   - **Host:** localhost
   - **Port:** 5432
   - **Database:** streamwatch
   - **Username:** streamwatch_user
   - **Password:** password
5. Click "Save"

#### **Step 3: Explore the Database**
1. Expand your server connection
2. Expand "Databases" → "streamwatch" → "Schemas" → "public" → "Tables"
3. You'll see all 14 tables listed

### **Method 2: Command Line (For Advanced Users)**

#### **Windows:**
1. Open Command Prompt
2. Type: `psql -h localhost -U streamwatch_user -d streamwatch`
3. Enter password when prompted

#### **Mac/Linux:**
1. Open Terminal
2. Type: `psql -h localhost -U streamwatch_user -d streamwatch`
3. Enter password when prompted

---

## 📊 **Understanding the Database Tables**

### **Main Data Tables:**

#### **1. sites**
- **What it contains:** All monitoring locations
- **Key fields:** site_code, waterbody, latitude, longitude
- **Example:** Site "AC7" on Assunpink Creek at coordinates 40.218, -74.560

#### **2. samples**
- **What it contains:** Water quality measurements
- **Key fields:** sample_id, site_code, sample_date, water_temperature, ph, do_ppm
- **Example:** Sample from site "AC7" on 2023-05-15 with temperature 18.5°C

#### **3. bugs**
- **What it contains:** Macroinvertebrate (bug) counts
- **Key fields:** bug_record_id, sample_code, order, family, count
- **Example:** 5 mayflies (Ephemeroptera) found in sample "AC7_20230515"

#### **4. bacteria**
- **What it contains:** Bacteria test results
- **Key fields:** bacteria_record_id, sample_code, site_code, measurement_value
- **Example:** E. coli test result for site "AC7" on 2023-05-15

#### **5. volunteers**
- **What it contains:** Volunteer information
- **Key fields:** volunteer_id, first_name, last_name, email, active_cat, active_bat
- **Example:** Volunteer "John Smith" who is active for CAT sampling

---

## 🔍 **Basic Database Queries**

### **How to Run Queries in pgAdmin:**

1. **Open Query Tool:**
   - Right-click on the "streamwatch" database
   - Select "Query Tool"

2. **Type Your Query:**
   - Enter SQL code in the query window
   - Click the "Execute" button (or press F5)

3. **View Results:**
   - Results appear in the bottom panel
   - You can export results to CSV if needed

### **Example Queries:**

#### **1. See All Tables and Record Counts**
```sql
SELECT 
    'sites' as table_name, COUNT(*) as record_count FROM sites
UNION ALL
SELECT 'samples', COUNT(*) FROM samples
UNION ALL
SELECT 'bugs', COUNT(*) FROM bugs
UNION ALL
SELECT 'bacteria', COUNT(*) FROM bacteria
UNION ALL
SELECT 'volunteers', COUNT(*) FROM volunteers
ORDER BY table_name;
```

#### **2. Look at Sample Data from Sites Table**
```sql
SELECT site_code, waterbody, latitude, longitude, site_type
FROM sites
LIMIT 10;
```

#### **3. Find Sites by Waterbody**
```sql
SELECT site_code, waterbody, latitude, longitude
FROM sites
WHERE waterbody LIKE '%Assunpink%'
ORDER BY site_code;
```

#### **4. Check Recent Water Quality Samples**
```sql
SELECT sample_id, site_code, sample_date, water_temperature, ph, do_ppm
FROM samples
WHERE sample_date >= '2023-01-01'
ORDER BY sample_date DESC
LIMIT 20;
```

#### **5. Count Samples by Site**
```sql
SELECT site_code, COUNT(*) as sample_count
FROM samples
GROUP BY site_code
ORDER BY sample_count DESC
LIMIT 10;
```

---

## 🔍 **Data Quality Checking**

### **1. Check for Missing Data**

#### **Sites with Missing Coordinates**
```sql
SELECT site_code, waterbody, latitude, longitude
FROM sites
WHERE latitude IS NULL OR longitude IS NULL;
```

#### **Samples with Missing Temperature**
```sql
SELECT sample_id, site_code, sample_date, water_temperature
FROM samples
WHERE water_temperature IS NULL
LIMIT 10;
```

### **2. Check for Invalid Data**

#### **Invalid Temperature Values**
```sql
SELECT sample_id, site_code, water_temperature
FROM samples
WHERE water_temperature < 0 OR water_temperature > 40;
```

#### **Invalid pH Values**
```sql
SELECT sample_id, site_code, ph
FROM samples
WHERE ph < 0 OR ph > 14;
```

### **3. Check Data Relationships**

#### **Samples with Invalid Site Codes**
```sql
SELECT DISTINCT s.site_code
FROM samples s
LEFT JOIN sites st ON s.site_code = st.site_code
WHERE st.site_code IS NULL;
```

#### **Bugs with Invalid Sample Codes**
```sql
SELECT DISTINCT b.sample_code
FROM bugs b
LEFT JOIN samples s ON b.sample_code = s.sample_id
WHERE s.sample_id IS NULL
LIMIT 10;
```

---

## 📊 **Data Analysis Queries**

### **1. Water Quality Trends**

#### **Average Temperature by Year**
```sql
SELECT 
    EXTRACT(YEAR FROM sample_date) as year,
    AVG(water_temperature) as avg_temp,
    COUNT(*) as sample_count
FROM samples
WHERE water_temperature IS NOT NULL
GROUP BY EXTRACT(YEAR FROM sample_date)
ORDER BY year;
```

#### **Temperature by Site**
```sql
SELECT 
    s.site_code,
    s.waterbody,
    AVG(sa.water_temperature) as avg_temp,
    COUNT(*) as sample_count
FROM sites s
JOIN samples sa ON s.site_code = sa.site_code
WHERE sa.water_temperature IS NOT NULL
GROUP BY s.site_code, s.waterbody
ORDER BY avg_temp DESC;
```

### **2. Bug Analysis**

#### **Most Common Bug Families**
```sql
SELECT family, COUNT(*) as total_count
FROM bugs
GROUP BY family
ORDER BY total_count DESC
LIMIT 10;
```

#### **Bug Diversity by Site**
```sql
SELECT 
    s.site_code,
    s.waterbody,
    COUNT(DISTINCT b.family) as unique_families,
    SUM(b.count) as total_bugs
FROM sites s
JOIN samples sa ON s.site_code = sa.site_code
JOIN bugs b ON sa.sample_id = b.sample_code
GROUP BY s.site_code, s.waterbody
ORDER BY unique_families DESC;
```

### **3. Volunteer Activity**

#### **Active Volunteers**
```sql
SELECT first_name, last_name, email, active_cat, active_bat
FROM volunteers
WHERE active_cat = true OR active_bat = true
ORDER BY last_name;
```

---

## 🚨 **Common Issues and Solutions**

### **Problem: "Table doesn't exist" Error**
**Solution:** Check that you're connected to the "streamwatch" database, not "postgres"

### **Problem: "Permission denied" Error**
**Solution:** Make sure you're using the correct username (streamwatch_user) and password

---

### **Sample Validation Queries:**

#### **Check for Duplicates**
```sql
SELECT site_code, COUNT(*)
FROM sites
GROUP BY site_code
HAVING COUNT(*) > 1;
```

#### **Check Date Ranges**
```sql
SELECT 
    MIN(sample_date) as earliest_date,
    MAX(sample_date) as latest_date,
    COUNT(*) as total_samples
FROM samples;
```

#### **Check Data Completeness**
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(water_temperature) as temp_records,
    COUNT(ph) as ph_records,
    COUNT(do_ppm) as do_records
FROM samples;
```

---

## 📚 **Resources**

### **pgAdmin Help:**
- **pgAdmin Documentation:** https://www.pgadmin.org/docs/
- **PostgreSQL Tutorial:** https://www.postgresqltutorial.com/

### **Project Specific:**
- **Technical Details:** See `TECHNICAL_DETAILS.md`
- **Status Report:** See `DATA_STATUS_REPORT.md`

---
