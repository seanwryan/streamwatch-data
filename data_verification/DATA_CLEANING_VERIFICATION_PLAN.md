# StreamWatch Data Cleaning Verification Plan
## How to Check That Data Cleaning Worked Correctly

**Goal:** Make sure all data cleaning was done correctly  
**What to check:** All 14 database tables and their data  
**How to check:** Go through each column in each table systematically  
**Time needed:** 2-3 weeks to check everything

---

## 🎯 **How We'll Check the Data**

### **Two Ways to Check:**

#### **1. Compare Database to Excel**
- **How:** Look at cleaned database data vs original Excel files
- **Good for:** Quick spot-checks of specific changes
- **Use when:** You want to verify specific transformations

#### **2. Check Each Column Systematically**
- **How:** Go through each column in each table one by one
- **Good for:** Thorough checking, catches problems
- **Use when:** You want to be sure everything is right

### **Recommended: Check Each Column Systematically**
**Why:** More thorough, catches data type problems, format issues, and edge cases that comparison might miss.

---

## 📋 **How to Check the Data (4 Steps)**

### **Step 1: Check Data Types**
- Make sure all columns have correct data types
- Check for unexpected empty fields in required columns
- Make sure numbers are in the right ranges
- Check that dates and times are formatted correctly

### **Step 2: Check Data Transformations**
- Make sure Excel column names were changed to database names correctly
- Check that data cleaning rules were applied
- Make sure calculated fields are correct
- Check that standardization rules were applied (uppercase, trimming, etc.)

### **Step 3: Check Data Relationships**
- Make sure table connections work correctly
- Check that all references between tables are valid
- Make sure business rules are followed
- Check that data relationships make sense

### **Step 4: Check Sample Data**
- Look at random samples from each table
- Check edge cases and special values
- Look for data problems or unusual values
- Make sure data is complete

---

## 📊 **How to Check Each Table**

### **Table 1: sites (168 records)**

#### **What to Check:**
- [ ] **site_code:** Text, not empty, unique, all uppercase
- [ ] **is_active:** True/false, not empty
- [ ] **waterbody:** Text, can be empty
- [ ] **latitude:** Number, between -90 and 90
- [ ] **longitude:** Number, between -180 and 180
- [ ] **site_type:** Text, can be empty
- [ ] **description:** Text, can be empty
- [ ] **All other fields:** Check they have correct data types

#### **SQL Queries to Run:**
```sql
-- Check for missing coordinates
SELECT site_code, waterbody, latitude, longitude 
FROM sites 
WHERE latitude IS NULL OR longitude IS NULL;

-- Check coordinate ranges
SELECT site_code, latitude, longitude 
FROM sites 
WHERE latitude < -90 OR latitude > 90 OR longitude < -180 OR longitude > 180;

-- Check site code format
SELECT site_code 
FROM sites 
WHERE site_code != UPPER(site_code) OR LENGTH(site_code) < 2;

-- Look at sample data
SELECT * FROM sites LIMIT 10;
```

#### **Known Issues to Look For:**
- 10 sites missing GPS coordinates
- Site code standardization (PR2A→PR2a, MI4B→MI4b)
- Date format consistency

---

### **Table 2: samples (3,608 records)**

#### **What to Check:**
- [ ] **sample_id:** Text, not empty, unique
- [ ] **site_code:** Text, not empty, must exist in sites table
- [ ] **sample_date:** Date, can be empty
- [ ] **water_temperature:** Number, between -5 and 45
- [ ] **ph:** Number, between 0 and 14
- [ ] **do_ppm:** Number, between 0 and 20
- [ ] **nitrate:** Number, between 0 and 1000
- [ ] **phosphates:** Number, between 0 and 100
- [ ] **turbidity:** Number, between 0 and 1000
- [ ] **All other fields:** Check they have correct data types

#### **SQL Queries to Run:**
```sql
-- Check for invalid temperatures
SELECT sample_id, site_code, water_temperature 
FROM samples 
WHERE water_temperature < -5 OR water_temperature > 45;

-- Check for invalid pH values
SELECT sample_id, site_code, ph 
FROM samples 
WHERE ph < 0 OR ph > 14;

-- Check for missing site references
SELECT DISTINCT s.site_code 
FROM samples s 
LEFT JOIN sites st ON s.site_code = st.site_code 
WHERE st.site_code IS NULL;

-- Check date ranges
SELECT MIN(sample_date) as earliest, MAX(sample_date) as latest 
FROM samples 
WHERE sample_date IS NOT NULL;

-- Look at sample data
SELECT sample_id, site_code, sample_date, water_temperature, ph, do_ppm 
FROM samples 
ORDER BY sample_date DESC 
LIMIT 10;
```

#### **Known Issues to Look For:**
- Site code standardization (PR2A→PR2a, MI4B→MI4b)
- Date format consistency
- Numeric value ranges
- Detection limit handling (gl fields)

---

### **Table 3: bugs (7,274 records)**

#### **What to Check:**
- [ ] **bug_record_id:** Text, not empty, unique
- [ ] **sample_code:** Text, not empty
- [ ] **order:** Text, not empty
- [ ] **family:** Text, not empty
- [ ] **count:** Number, between 0 and 10000
- [ ] **percentage:** Number, between 0 and 100
- [ ] **tolerance:** Number, between 0 and 10
- [ ] **ept:** True/false, can be empty
- [ ] **insect:** True/false, can be empty
- [ ] **sensitive:** True/false, can be empty
- [ ] **All other fields:** Check they have correct data types

#### **SQL Queries to Run:**
```sql
-- Check for invalid counts
SELECT bug_record_id, sample_code, count 
FROM bugs 
WHERE count < 0 OR count > 10000;

-- Check percentage calculations
SELECT bug_record_id, sample_code, count, percentage 
FROM bugs 
WHERE percentage < 0 OR percentage > 100;

-- Check tolerance value ranges
SELECT bug_record_id, sample_code, tolerance 
FROM bugs 
WHERE tolerance < 0 OR tolerance > 10;

-- Check boolean field consistency
SELECT bug_record_id, sample_code, ept, insect, sensitive 
FROM bugs 
WHERE ept IS NULL OR insect IS NULL;

-- Sample data check
SELECT bug_record_id, sample_code, order, family, count, tolerance 
FROM bugs 
ORDER BY count DESC 
LIMIT 10;
```

#### **Expected Issues to Check:**
- Taxonomy data enrichment accuracy
- Calculated field accuracy (percentage, products)
- Boolean field consistency
- Sample code references

---

### **Table 4: bacteria (622 records)**

#### **What to Check:**
- [ ] **bacteria_record_id:** Text, not empty, unique
- [ ] **sample_code:** Text, not empty
- [ ] **site_code:** Text, not empty, must exist in sites table
- [ ] **collection_date:** Date, can be empty
- [ ] **measurement_value:** Text, can be empty
- [ ] **water_temperature:** Number, between -5 and 45
- [ ] **All other fields:** Check they have correct data types

#### **SQL Queries to Run:**
```sql
-- Check for missing site references
SELECT DISTINCT b.site_code 
FROM bacteria b 
LEFT JOIN sites s ON b.site_code = s.site_code 
WHERE s.site_code IS NULL;

-- Check date ranges
SELECT MIN(collection_date) as earliest, MAX(collection_date) as latest 
FROM bacteria 
WHERE collection_date IS NOT NULL;

-- Look at sample data
SELECT bacteria_record_id, sample_code, site_code, collection_date, measurement_value 
FROM bacteria 
ORDER BY collection_date DESC 
LIMIT 10;
```

#### **Known Issues to Look For:**
- Site code filtering accuracy
- Date/time parsing
- Measurement value standardization

---

### **Remaining Tables (5-14): Summary**

#### **Tables to Check:**
- **volunteers (50+ records):** Check volunteer IDs, names, dates, true/false fields
- **taxonomy (1,000+ records):** Check bug IDs, family names, tolerance values
- **batsites (200+ records):** Check site codes, dates, organism counts
- **indices (500+ records):** Check calculated scores and totals
- **habitat (100+ records):** Check site codes, dates, habitat scores
- **equipment (20+ records):** Check equipment IDs, assignments, status
- **trainings (50+ records):** Check training IDs, dates, types
- **volunteer_trainings (200+ records):** Check attendance records
- **volunteer_assignments (100+ records):** Check assignments and dates
- **equipment_maintenance (50+ records):** Check maintenance records

#### **General Things to Check for All Tables:**
- [ ] **Primary keys:** Not empty, unique
- [ ] **Foreign keys:** Reference existing records in other tables
- [ ] **Data types:** Correct types (text, numbers, dates, true/false)
- [ ] **Date fields:** Properly formatted dates
- [ ] **Text fields:** No extra spaces, proper formatting
- [ ] **Number fields:** Within reasonable ranges
- [ ] **Required fields:** Not empty when they shouldn't be

#### **Sample SQL for Any Table:**
```sql
-- Check for empty primary keys
SELECT * FROM [table_name] WHERE [primary_key] IS NULL OR [primary_key] = '';

-- Check data types
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = '[table_name]';

-- Look at sample data
SELECT * FROM [table_name] LIMIT 10;
```

---

## 🔍 **How to Do the Verification (3 Weeks)**

### **Week 1: Check Data Types and Formats**

#### **Days 1-2: Main Tables (sites, samples)**
- Check all data types are correct
- Look for unexpected empty fields
- Make sure numbers are in right ranges
- Check that dates and times are formatted correctly

#### **Days 3-4: Data Tables (bugs, bacteria)**
- Check data types and formats
- Look at calculated fields
- Make sure business logic is correct
- Check that table relationships work

#### **Day 5: Other Tables (volunteers, taxonomy, etc.)**
- Check all remaining tables
- Make sure data is complete
- Check that relationships work
- Make sure business rules are followed

### **Week 2: Check Data Transformations**

#### **Days 1-2: Check Column Mappings**
- Make sure Excel column names were changed to database names correctly
- Check that data cleaning rules were applied
- Make sure standardization worked (uppercase, trimming)
- Check that special cases were handled

#### **Days 3-4: Check Business Logic**
- Make sure table connections work correctly
- Check that all references between tables are valid
- Make sure calculated fields are correct
- Check that data is consistent

#### **Day 5: Check Edge Cases**
- Look at special values and edge cases
- Make sure error handling worked
- Check that data is complete
- Make sure data quality is good

### **Week 3: Check Sample Data**

#### **Days 1-2: Random Sample Checks**
- Pick random samples from each table
- Make sure data is accurate
- Look for problems or unusual values
- Check that data relationships work

#### **Days 3-4: Check Specific Issues**
- Check specific known problems
- Look at critical data points
- Check environmental data
- Make sure data integrity is good

#### **Day 5: Final Check**
- Run data quality queries
- Make sure all transformations worked
- Check that data is complete
- Write down any remaining problems

---

## 📊 **Useful SQL Queries**

### **Check Data Types**
```sql
-- Check data types for all columns
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'sites' 
ORDER BY ordinal_position;

-- Check for unexpected empty fields
SELECT COUNT(*) as null_count 
FROM sites 
WHERE site_code IS NULL;
```

### **Check Number Ranges**
```sql
-- Check temperature ranges
SELECT 
    MIN(water_temperature) as min_temp,
    MAX(water_temperature) as max_temp,
    COUNT(*) as total_records
FROM samples 
WHERE water_temperature IS NOT NULL;

-- Check date ranges
SELECT 
    MIN(sample_date) as earliest_date,
    MAX(sample_date) as latest_date,
    COUNT(*) as total_records
FROM samples 
WHERE sample_date IS NOT NULL;
```

### **Check Table Relationships**
```sql
-- Check foreign key relationships
SELECT COUNT(*) as orphaned_records
FROM samples s
LEFT JOIN sites st ON s.site_code = st.site_code
WHERE st.site_code IS NULL;

-- Check referential integrity
SELECT DISTINCT site_code 
FROM samples 
WHERE site_code NOT IN (SELECT site_code FROM sites);
```

### **Check Data Quality**
```sql
-- Check data completeness
SELECT 
    COUNT(*) as total_records,
    COUNT(water_temperature) as temp_records,
    COUNT(ph) as ph_records,
    COUNT(do_ppm) as do_records
FROM samples;

-- Check for data problems
SELECT site_code, COUNT(*) as sample_count
FROM samples
GROUP BY site_code
HAVING COUNT(*) > 100
ORDER BY sample_count DESC;
```

---

## 📋 **Checklist for Each Table**

### **For Each Table:**
- [ ] **Data Types:** All columns have correct data types
- [ ] **Empty Fields:** No unexpected empty fields in required columns
- [ ] **Number Ranges:** Numbers are within expected ranges
- [ ] **Date Formats:** Dates and times are formatted correctly
- [ ] **Table Connections:** Foreign key relationships work
- [ ] **Calculated Fields:** Calculated fields are accurate
- [ ] **Text Formatting:** Text fields are properly formatted
- [ ] **Data Completeness:** Data completeness is acceptable
- [ ] **Data Consistency:** Data is consistent across records
- [ ] **Data Quality:** No obvious data quality problems

### **For Each Column:**
- [ ] **Data Type:** Correct data type assigned
- [ ] **Empty Handling:** Proper empty value handling
- [ ] **Range Validation:** Values within expected ranges
- [ ] **Format Validation:** Proper format (dates, text, etc.)
- [ ] **Transformation:** Cleaning rules applied correctly
- [ ] **Standardization:** Consistent format across records
- [ ] **Business Rules:** Follows business logic
- [ ] **Sample Check:** Spot-check sample values
- [ ] **Edge Cases:** Special values handled correctly
- [ ] **Documentation:** Column purpose documented

---
### **Documentation Requirements:**
- **Issues Found:** All documented with severity
- **Fixes Applied:** All documented with rationale
- **Remaining Issues:** All documented with recommendations
- **Verification Results:** Complete summary provided

---

## 🎯 **Success Criteria**

### **Data Quality Targets:**
- **Completeness:** >95% for critical parameters
- **Accuracy:** <5% error rate
- **Consistency:** 100% format standardization
- **Integrity:** 100% referential integrity

### **Verification Completion:**
- **All Tables:** 100% verified
- **All Columns:** 100% checked
- **All Relationships:** 100% validated
- **All Issues:** 100% documented

### **What to Document:**
- **Problems Found:** All documented with how serious they are
- **Fixes Applied:** All documented with why they were needed
- **Remaining Problems:** All documented with recommendations
- **Verification Results:** Complete summary provided

---

## 📞 **Next Steps**

1. **Review this plan** with the team
2. **Assign verification tasks** to team members
3. **Set up verification environment** (database access, tools)
4. **Begin systematic verification** following the plan
5. **Document all findings** and issues
6. **Apply fixes** as needed
7. **Re-verify** after fixes
8. **Complete final validation** and documentation

**Estimated Timeline:** 2-3 weeks for complete verification  
**Team Requirements:** Database access, SQL knowledge, attention to detail  
**Deliverable:** Comprehensive verification report with findings and recommendations
