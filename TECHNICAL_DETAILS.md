# StreamWatch Data Pipeline - Technical Details
**Loading and Cleaning Steps Documentation**

---

## 📋 **Overview**

This document details the technical implementation of the StreamWatch data pipeline, including data loading processes, cleaning steps applied, and current technical issues.

---

## 🗄️ **Database Schema**

### **Tables Created (14 total):**

1. **sites** - Monitoring site locations and metadata
2. **samples** - Water quality measurements
3. **bugs** - Macroinvertebrate (bug) data
4. **bacteria** - Bacteria test results
5. **volunteers** - Volunteer information
6. **taxonomy** - Bug identification reference data
7. **batsites** - Bug collection site information
8. **indices** - Calculated water quality scores
9. **habitat** - Habitat assessment data
10. **equipment** - Equipment tracking
11. **trainings** - Training session records
12. **volunteer_trainings** - Training attendance
13. **volunteer_assignments** - Site assignments
14. **equipment_maintenance** - Maintenance records

---

## 📊 **Source Data Files**

### **Primary Data Files:**

#### **1. All StreamWatch Data.xlsx**
- **Content:** Water quality measurements
- **Records:** 3,608 samples
- **Key Fields:** Sample ID, site code, date, temperature, pH, dissolved oxygen
- **Time Period:** 1992-2024
- **Sheets:** Multiple sheets by watershed (Rocky Brook, Pike Run, Moore Creek, Miry Run, Millstone River)

#### **2. 2025 StreamWatch Locations.xlsx**
- **Content:** Site locations and metadata
- **Records:** 168 monitoring sites
- **Key Fields:** Site code, GPS coordinates, waterbody name, site type
- **Status:** Complete with GPS coordinates

#### **3. BATSITES COLLECTED.xlsx**
- **Content:** Macroinvertebrate data
- **Records:** 7,274 bug records
- **Key Fields:** Sample code, bug order, family, count, tolerance values
- **Time Period:** 1992-2024

#### **4. BACT and HAB 2025 Data.xlsx**
- **Content:** Bacteria test results
- **Records:** 622 bacteria tests
- **Key Fields:** Sample code, site code, date, E. coli results, turbidity
- **Time Period:** 2024 (recent data)

#### **5. tblSampleDates.xlsx**
- **Content:** Bug identification reference data
- **Records:** 1,000+ bug types
- **Key Fields:** Bug ID, family, genus, tolerance values, functional groups

#### **6. Volunteer_Tracking.xlsm**
- **Content:** Volunteer information
- **Records:** 50+ volunteers
- **Key Fields:** Volunteer ID, name, contact info, training status

---

## ⚙️ **ETL Pipeline Implementation**

### **Scripts Created:**

#### **1. config.py**
- Database connection configuration
- File path definitions
- Environment variable handling

#### **2. create_database_schema.py**
- Database creation
- Table schema definition
- Index creation
- Permission setup

#### **3. streamwatch_etl.py**
- Main ETL pipeline
- Data cleaning functions
- Data loading processes
- Error handling and logging

#### **4. setup_and_run.py**
- Automated setup and execution
- Dependency installation
- Pipeline orchestration

---

## 🧹 **Data Cleaning Steps Applied**

### **Sites Data Cleaning:**
- **Coordinate Conversion:** Converted text coordinates to numeric values
- **Invalid Coordinate Handling:** Flagged 10 sites with invalid coordinates
- **Site Code Standardization:** Made all site codes uppercase
- **Text Field Cleaning:** Trimmed whitespace and standardized formats
- **Date Parsing:** Converted date fields to proper date format
- **Boolean Conversion:** Converted true/false text to boolean values

### **Samples Data Cleaning:**
- **Date/Time Parsing:** Converted sample dates and times
- **Numeric Conversion:** Converted temperature, pH, dissolved oxygen to numbers
- **Detection Limit Handling:** Processed "gl" (greater than limit) values
- **Site Code Standardization:** Applied same site code rules as sites table
- **Data Type Validation:** Ensured proper data types for all fields

### **Bugs Data Cleaning:**
- **Taxonomy Enrichment:** Added taxonomy information for each bug
- **Calculated Fields:** Generated percentages and derived values
- **Sensitivity Classification:** Determined if bugs are sensitive or tolerant
- **Unique ID Generation:** Created unique bug record IDs
- **Count Validation:** Ensured count values are numeric

### **Bacteria Data Cleaning:**
- **Site Filtering:** Only included sites that exist in sites table
- **Date/Time Parsing:** Converted collection dates and times
- **Measurement Standardization:** Standardized measurement values
- **Missing Data Handling:** Properly handled null values

### **Volunteers Data Cleaning:**
- **Date Parsing:** Converted start dates to proper format
- **Boolean Conversion:** Converted true/false fields
- **Name Standardization:** Created full names from first/last
- **ID Generation:** Handled missing volunteer IDs

---

## ⚠️ **Current Technical Issues**

### **ETL Pipeline Errors:**

#### **1. Column Name Mismatches:**
- **Bugs Table:** Excel uses "BUGID#" but database expects "bug_id"
- **Samples Table:** Excel has "source_sheet" column not in database schema
- **Taxonomy Table:** Excel uses "BugID" but database expects "bug_id"

#### **2. Duplicate Data Issues:**
- **Sites Table:** Duplicate key violations when trying to reload data
- **Data Already Exists:** Some tables have data, causing insertion conflicts

#### **3. Schema Mismatches:**
- **Column Count:** Excel files have more columns than database tables
- **Data Types:** Some Excel columns don't match expected database types
- **Required Fields:** Some database fields are required but missing from Excel

### **Error Log Examples:**
```
ERROR - column "BUGID#" of relation "bugs" does not exist
ERROR - duplicate key value violates unique constraint "sites_site_code_key"
ERROR - column "source_sheet" of relation "samples" does not exist
```

---

## 📈 **Data Loading Status**

### **Successfully Loaded:**
- **Sites:** 168 records (with duplicate key warnings)
- **Partial Samples:** Some data loaded before errors occurred

### **Failed to Load:**
- **Bugs:** Column name mismatches
- **Bacteria:** Column name mismatches
- **Volunteers:** Column name mismatches
- **Taxonomy:** Column name mismatches
- **Other Tables:** Not attempted due to initial failures

### **Loading Process:**
- **Chunked Loading:** 10 records at a time to avoid memory issues
- **Error Handling:** Logged all errors to etl_pipeline.log
- **Transaction Management:** Used database transactions for data integrity
- **Recovery:** Can restart from any point in the process

---

## 🔧 **Technical Architecture**

### **Technology Stack:**
- **Database:** PostgreSQL 15.14
- **ETL:** Python 3.9.6 with pandas, psycopg2, sqlalchemy
- **Data Access:** pgAdmin 9.8 (desktop app)
- **Environment:** macOS with Docker support

### **Python Dependencies:**
```
pandas
openpyxl
psycopg2-binary
sqlalchemy
python-dotenv
```

### **Performance Optimizations:**
- **Chunked Loading:** 10 records at a time
- **Batch Processing:** Multiple records per transaction
- **Memory Management:** Clear data after processing
- **Index Creation:** Automatic index creation for foreign keys

---

## 🛠️ **Fixing the Issues**

### **Required Actions:**

#### **1. Fix Column Name Mappings:**
- Update ETL scripts to map Excel column names to database column names
- Ensure all required columns are present
- Handle optional columns gracefully

#### **2. Handle Duplicate Data:**
- Implement "upsert" logic (update if exists, insert if new)
- Clear existing data before reloading
- Use proper conflict resolution

#### **3. Complete Data Loading:**
- Fix all column name issues
- Load all remaining tables
- Verify data integrity
- Run data quality checks

### **Recommended Approach:**
1. **Backup current database** before making changes
2. **Fix column name mappings** in ETL scripts
3. **Implement proper duplicate handling**
4. **Test with small data samples** before full reload
5. **Complete full data loading**
6. **Verify all data is loaded correctly**

---

## 📊 **Data Quality Metrics**

### **Expected Record Counts:**
- **Sites:** 168 records
- **Samples:** 3,608 records
- **Bugs:** 7,274 records
- **Bacteria:** 622 records
- **Volunteers:** 50+ records
- **Taxonomy:** 1,000+ records

### **Data Quality Checks:**
- **Referential Integrity:** All foreign keys reference existing records
- **Data Type Validation:** All fields have correct data types
- **Range Validation:** Numeric values within expected ranges
- **Completeness:** Required fields not empty
- **Consistency:** Data format consistent across records

---

## 📝 **Next Steps**

1. **Fix ETL Pipeline Issues:**
   - Resolve column name mismatches
   - Implement proper duplicate handling
   - Complete data loading for all tables

2. **Data Validation:**
   - Verify all data is loaded correctly
   - Run data quality checks
   - Document any remaining issues

3. **Performance Optimization:**
   - Add database indexes for common queries
   - Optimize query performance
   - Set up monitoring and logging

4. **Documentation Updates:**
   - Update technical documentation
   - Create user guides
   - Document data validation procedures

---

**For questions about technical implementation, refer to the ETL scripts in the `scripts/` folder or check the error logs in `logs/etl_pipeline.log`.**
