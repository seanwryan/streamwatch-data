# StreamWatch Database Relationships

**Date**: October 2025  
**Purpose**: Understanding how tables connect and data flows through the system

---

## 🏗️ Database Architecture Overview

The StreamWatch database follows a **hierarchical, relational structure** where data flows from core reference tables to detailed measurement tables. Here's how it all connects:

---

## 🔗 Core Relationship Structure

### **1. SITES (Central Hub)**
```
SITES (169 records)
├── site_code (Primary Key)
├── site_name, latitude, longitude
└── watershed, elevation, notes
```

**Connects to:**
- **SAMPLES** (16,910 records) via `site_code`
- **BUGS** (7,339 records) via `site_code` 
- **BACTERIA** (669 records) via `site_code`
- **VOLUNTEERS** (428 records) via `site_code`

---

### **2. SAMPLES (Measurement Hub)**
```
SAMPLES (16,910 records)
├── sample_id (Primary Key)
├── site_code (Foreign Key → SITES)
├── sample_code (Unique identifier)
├── sample_date, water_temperature, pH, etc.
└── volunteer_id (Foreign Key → VOLUNTEERS)
```

**Connects to:**
- **SITES** via `site_code`
- **VOLUNTEERS** via `volunteer_id`
- **BUGS** via `sample_code`
- **BACTERIA** via `sample_code`

---

### **3. BUGS (Biological Data)**
```
BUGS (7,339 records)
├── bug_id (Primary Key)
├── sample_code (Foreign Key → SAMPLES)
├── site_code (Foreign Key → SITES)
├── genus_species (Foreign Key → TAXONOMY)
├── count, percentage, tolerance_value
└── ept, insect, sensitive flags
```

**Connects to:**
- **SITES** via `site_code`
- **SAMPLES** via `sample_code`
- **TAXONOMY** via `genus_species`

---

### **4. BACTERIA (Water Quality)**
```
BACTERIA (669 records)
├── bacteria_record_id (Primary Key)
├── sample_code (Foreign Key → SAMPLES)
├── site_code (Foreign Key → SITES)
├── e_coli, water_temperature, turbidity
└── ph, do_ppm, conductivity
```

**Connects to:**
- **SITES** via `site_code`
- **SAMPLES** via `sample_code`

---

### **5. VOLUNTEERS (People)**
```
VOLUNTEERS (428 records)
├── volunteer_id (Primary Key)
├── site_code (Foreign Key → SITES)
├── first_name, last_name, email
└── phone, start_date, is_active
```

**Connects to:**
- **SITES** via `site_code`
- **SAMPLES** via `volunteer_id`

---

### **6. TAXONOMY (Reference Data)**
```
TAXONOMY (149 records)
├── genus_species (Primary Key)
├── order_name, family_name
├── tolerance_value, ept_flag
└── insect_flag, sensitive_flag
```

**Connects to:**
- **BUGS** via `genus_species`

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│   SITES     │ ←── Central location data
│ (169 recs)  │
└──────┬──────┘
       │
       ├─── site_code ───┐
       │                 │
       │                 ▼
       │         ┌─────────────┐
       │         │  SAMPLES    │ ←── Water quality measurements
       │         │(16,910 recs)│
       │         └──────┬──────┘
       │                │
       │                ├─── sample_code ───┐
       │                │                  │
       │                │                  ▼
       │                │         ┌─────────────┐
       │                │         │    BUGS     │ ←── Biological data
       │                │         │ (7,339 recs)│
       │                │         └──────┬──────┘
       │                │                │
       │                │                ├─── genus_species ───┐
       │                │                │                    │
       │                │                │                    ▼
       │                │                │            ┌─────────────┐
       │                │                │            │  TAXONOMY   │ ←── Reference data
       │                │                │            │ (149 recs)  │
       │                │                │            └─────────────┘
       │                │                │
       │                │                └─── site_code ───┐
       │                │                                 │
       │                │                                 ▼
       │                │                         ┌─────────────┐
       │                │                         │   SITES     │ ←── Back to sites
       │                │                         │ (169 recs)  │
       │                │                         └─────────────┘
       │                │
       │                ├─── sample_code ───┐
       │                │                  │
       │                │                  ▼
       │                │         ┌─────────────┐
       │                │         │  BACTERIA   │ ←── Water quality tests
       │                │         │ (669 recs)  │
       │                │         └──────┬──────┘
       │                │                │
       │                │                └─── site_code ───┐
       │                │                                 │
       │                │                                 ▼
       │                │                         ┌─────────────┐
       │                │                         │   SITES     │ ←── Back to sites
       │                │                         │ (169 recs)  │
       │                │                         └─────────────┘
       │                │
       │                └─── volunteer_id ───┐
       │                                   │
       │                                   ▼
       │                           ┌─────────────┐
       │                           │ VOLUNTEERS  │ ←── People data
       │                           │ (428 recs)  │
       │                           └──────┬──────┘
       │                                  │
       │                                  └─── site_code ───┐
       │                                                   │
       │                                                   ▼
       │                                           ┌─────────────┐
       │                                           │   SITES     │ ←── Back to sites
       │                                           │ (169 recs)  │
       │                                           └─────────────┘
       │
       └─── site_code ───┐
                         │
                         ▼
                 ┌─────────────┐
                 │ VOLUNTEERS  │ ←── People data
                 │ (428 recs)  │
                 └─────────────┘
```

---

## 🔄 Relationship Types

### **One-to-Many Relationships**
- **SITES → SAMPLES**: One site can have many samples
- **SITES → BUGS**: One site can have many bug records
- **SITES → BACTERIA**: One site can have many bacteria tests
- **SITES → VOLUNTEERS**: One site can have many volunteers
- **SAMPLES → BUGS**: One sample can have many bug records
- **SAMPLES → BACTERIA**: One sample can have many bacteria tests
- **VOLUNTEERS → SAMPLES**: One volunteer can collect many samples
- **TAXONOMY → BUGS**: One species can appear in many bug records

### **Many-to-One Relationships**
- **SAMPLES → SITES**: Many samples belong to one site
- **BUGS → SITES**: Many bug records belong to one site
- **BACTERIA → SITES**: Many bacteria tests belong to one site
- **VOLUNTEERS → SITES**: Many volunteers can work at one site
- **BUGS → SAMPLES**: Many bug records belong to one sample
- **BACTERIA → SAMPLES**: Many bacteria tests belong to one sample
- **SAMPLES → VOLUNTEERS**: Many samples can be collected by one volunteer
- **BUGS → TAXONOMY**: Many bug records can reference one species

---

## 🎯 Key Relationship Patterns

### **1. Site-Centric Design**
- **SITES** is the central hub
- All measurement data (samples, bugs, bacteria) links back to sites
- Volunteers are associated with specific sites
- This enables spatial analysis and site-specific reporting

### **2. Sample-Based Measurements**
- **SAMPLES** represents individual collection events
- Both **BUGS** and **BACTERIA** data link to samples
- This enables temporal analysis and sample-specific reporting

### **3. Reference Data Integration**
- **TAXONOMY** provides standardized species information
- **BUGS** table gets calculated fields from taxonomy
- This ensures consistent biological analysis

### **4. Volunteer Tracking**
- **VOLUNTEERS** are linked to both sites and samples
- This enables volunteer performance tracking
- Supports volunteer management and recognition

---

## 🔍 Query Examples

### **Find All Data for a Site**
```sql
SELECT s.site_name, s.latitude, s.longitude,
       sm.sample_date, sm.water_temperature, sm.ph,
       b.genus_species, b.count, b.percentage,
       bac.e_coli, bac.turbidity
FROM sites s
LEFT JOIN samples sm ON s.site_code = sm.site_code
LEFT JOIN bugs b ON sm.sample_code = b.sample_code
LEFT JOIN bacteria bac ON sm.sample_code = bac.sample_code
WHERE s.site_code = 'SITE001';
```

### **Find Volunteer Performance**
```sql
SELECT v.first_name, v.last_name, s.site_name,
       COUNT(sm.sample_id) as samples_collected,
       COUNT(b.bug_id) as bug_records,
       COUNT(bac.bacteria_record_id) as bacteria_tests
FROM volunteers v
JOIN sites s ON v.site_code = s.site_code
LEFT JOIN samples sm ON v.volunteer_id = sm.volunteer_id
LEFT JOIN bugs b ON sm.sample_code = b.sample_code
LEFT JOIN bacteria bac ON sm.sample_code = bac.sample_code
GROUP BY v.volunteer_id, v.first_name, v.last_name, s.site_name;
```

### **Find Water Quality Trends**
```sql
SELECT s.site_name, 
       DATE_TRUNC('month', sm.sample_date) as month,
       AVG(sm.water_temperature) as avg_temp,
       AVG(sm.ph) as avg_ph,
       AVG(bac.e_coli) as avg_e_coli
FROM sites s
JOIN samples sm ON s.site_code = sm.site_code
LEFT JOIN bacteria bac ON sm.sample_code = bac.sample_code
WHERE sm.sample_date >= '2020-01-01'
GROUP BY s.site_name, DATE_TRUNC('month', sm.sample_date)
ORDER BY s.site_name, month;
```

---

## 🚀 Benefits of This Structure

### **1. Data Integrity**
- Foreign key constraints prevent orphaned records
- Referential integrity ensures data consistency
- Cascade deletes maintain data relationships

### **2. Query Performance**
- Indexes on foreign keys speed up joins
- Normalized structure reduces data redundancy
- Efficient storage and retrieval

### **3. Analytical Capabilities**
- Easy to aggregate data by site, time, or volunteer
- Supports complex analytical queries
- Enables comprehensive reporting

### **4. Data Management**
- Clear data ownership and relationships
- Easy to identify and fix data quality issues
- Supports data validation and constraints

---

## 📋 Legacy Tables

The database also includes **8 legacy tables** that preserve original data structure:

- **tblSampleDates** - Original sample tracking
- **tblBugResults** - Original bug results  
- **tblRBP100Bugs** - RBP100 protocol data
- **BugList** - Bug reference list
- **wqx_sites** - WQX export sites
- **wqx_biohabphys** - WQX biological data
- **cat_assignments** - CAT meter assignments
- **cat_meters** - CAT meter inventory

These tables are **standalone** and don't have foreign key relationships with the core tables, preserving the original data structure for reference and export purposes.

---

## 🎯 Summary

The StreamWatch database uses a **well-designed relational structure** that:

1. **Centers around SITES** as the primary location reference
2. **Links all measurements** through SITES and SAMPLES
3. **Maintains data integrity** through foreign key constraints
4. **Supports complex analysis** through normalized relationships
5. **Preserves legacy data** in separate reference tables

This structure enables comprehensive watershed monitoring, data analysis, and reporting while maintaining data quality and integrity throughout the system.

---

*This relationship structure supports all the analytical capabilities needed for effective watershed monitoring and data management.*


