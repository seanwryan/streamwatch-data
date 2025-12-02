# StreamWatch Database Schema Documentation

## Overview

This document provides a complete reference for the StreamWatch database schema, including table structures, column definitions, data types, constraints, and relationships.

**Database**: `neondb` (PostgreSQL on Neon)  
**Last Updated**: October 2025  
**Version**: 1.0

---

## Table of Contents

1. [Core Data Tables](#core-data-tables)
2. [Reference Tables](#reference-tables)
3. [User Management Tables](#user-management-tables)
4. [Data Relationships](#data-relationships)
5. [Data Quality Standards](#data-quality-standards)
6. [Indexes and Performance](#indexes-and-performance)

---

## Core Data Tables

### 1. `sites` - Monitoring Sites

**Purpose**: Stores information about water quality monitoring sites

| Column Name | Data Type | Constraints | Description | Example Values |
|-------------|-----------|-------------|-------------|----------------|
| `site_code` | VARCHAR(20) | PRIMARY KEY | Unique site identifier | "BD1", "SB3", "AC5" |
| `site_name` | VARCHAR(100) | NOT NULL | Human-readable site name | "Bear Creek at Highway 1" |
| `waterbody` | VARCHAR(100) | | Water body name | "Bear Creek", "Missouri River" |
| `description` | TEXT | | Site description | "Upstream of confluence with..." |
| `latitude` | DECIMAL(10,8) | | GPS latitude coordinate | 40.12345678 |
| `longitude` | DECIMAL(11,8) | | GPS longitude coordinate | -94.12345678 |
| `elevation` | DECIMAL(8,2) | | Site elevation in meters | 250.50 |
| `watershed` | VARCHAR(100) | | Watershed name | "Missouri River Basin" |
| `is_active` | BOOLEAN | DEFAULT true | Whether site is currently monitored | true, false |
| `groundtruthing_priority` | VARCHAR(50) | | Priority level for groundtruthing | "High", "Medium", "Low" |
| `created_date` | TIMESTAMP | DEFAULT NOW() | Record creation date | 2024-01-15 10:30:00 |
| `updated_date` | TIMESTAMP | DEFAULT NOW() | Last update date | 2024-01-15 10:30:00 |

**Sample Data**:
```sql
site_code | site_name                    | waterbody    | latitude    | longitude    | is_active
----------|------------------------------|--------------|-------------|--------------|----------
BD1       | Bear Creek at Highway 1     | Bear Creek   | 40.12345678 | -94.12345678 | true
SB3       | Spring Branch at Bridge     | Spring Branch| 40.23456789 | -94.23456789 | true
AC5       | Apple Creek at Dam          | Apple Creek  | 40.34567890 | -94.34567890 | false
```

---

### 2. `samples` - Water Quality Samples

**Purpose**: Stores water quality measurement data

| Column Name | Data Type | Constraints | Description | Example Values |
|-------------|-----------|-------------|-------------|----------------|
| `sample_id` | VARCHAR(50) | PRIMARY KEY | Unique sample identifier | "SAMPLE_000001", "SAMPLE_000002" |
| `site_code` | VARCHAR(20) | FOREIGN KEY → sites.site_code | Site where sample was taken | "BD1", "SB3" |
| `sample_date` | DATE | NOT NULL | Date sample was collected | 2024-01-15 |
| `sample_time` | TIME | | Time sample was collected | 14:30:00 |
| `water_temperature` | DECIMAL(5,2) | | Water temperature in °C | 15.50, 22.30 |
| `ph` | DECIMAL(4,2) | CHECK (ph >= 0 AND ph <= 14) | pH level | 7.20, 8.50 |
| `do_ppm` | DECIMAL(6,3) | | Dissolved oxygen in mg/L | 8.50, 12.30 |
| `do_percent` | DECIMAL(5,2) | | Dissolved oxygen saturation % | 85.50, 95.20 |
| `nitrate` | DECIMAL(8,3) | | Nitrate concentration mg/L | 0.500, 2.300 |
| `phosphates` | DECIMAL(8,3) | | Phosphate concentration mg/L | 0.100, 0.800 |
| `turbidity` | DECIMAL(6,2) | | Turbidity in NTU | 5.20, 15.80 |
| `conductivity` | DECIMAL(8,2) | | Conductivity in µS/cm | 250.50, 450.30 |
| `chloride` | DECIMAL(8,3) | | Chloride concentration mg/L | 10.500, 25.300 |
| `e_coli` | DECIMAL(8,3) | | E. coli concentration MPN/100mL | 50.000, 200.000 |
| `total_coliforms` | DECIMAL(8,3) | | Total coliforms MPN/100mL | 100.000, 500.000 |
| `fecal_coliforms` | DECIMAL(8,3) | | Fecal coliforms MPN/100mL | 25.000, 150.000 |
| `enterococci` | DECIMAL(8,3) | | Enterococci MPN/100mL | 10.000, 75.000 |
| `notes` | TEXT | | Sample notes | "High flow conditions", "Algae present" |
| `created_date` | TIMESTAMP | DEFAULT NOW() | Record creation date | 2024-01-15 10:30:00 |
| `updated_date` | TIMESTAMP | DEFAULT NOW() | Last update date | 2024-01-15 10:30:00 |

**Sample Data**:
```sql
sample_id    | site_code | sample_date | water_temperature | ph    | do_ppm | nitrate | turbidity
-------------|-----------|-------------|-------------------|-------|--------|---------|----------
SAMPLE_000001| BD1       | 2024-01-15  | 15.50            | 7.20  | 8.50   | 0.500   | 5.20
SAMPLE_000002| SB3       | 2024-01-15  | 22.30            | 8.50  | 12.30  | 2.300   | 15.80
SAMPLE_000003| AC5       | 2024-01-16  | 18.75            | 7.80  | 9.20   | 1.100   | 8.50
```

---

### 3. `bugs` - Macroinvertebrate Data

**Purpose**: Stores macroinvertebrate count and analysis data

| Column Name | Data Type | Constraints | Description | Example Values |
|-------------|-----------|-------------|-------------|----------------|
| `bug_record_id` | VARCHAR(50) | PRIMARY KEY | Unique bug record identifier | "BUG_000001", "BUG_000002" |
| `sample_code` | VARCHAR(50) | FOREIGN KEY → samples.sample_id | Sample identifier | "SAMPLE_000001" |
| `order_name` | VARCHAR(50) | | Taxonomic order | "Diptera", "Trichoptera", "Ephemeroptera" |
| `family` | VARCHAR(100) | | Taxonomic family | "Chironomidae", "Simuliidae", "Hydropsychidae" |
| `genus_species` | VARCHAR(100) | | Genus and species | "Chironomus riparius" |
| `count` | INTEGER | NOT NULL, CHECK (count >= 0) | Number of individuals | 15, 0, 1 |
| `percentage` | DECIMAL(5,2) | | Percentage of total sample | 15.50, 0.00, 1.25 |
| `tolerance` | DECIMAL(3,1) | | Pollution tolerance value (1-10) | 6.0, 2.0, 8.0 |
| `ept` | BOOLEAN | | EPT taxon flag | true, false |
| `insect` | BOOLEAN | | Insect flag | true, false |
| `sensitive` | BOOLEAN | | Pollution sensitive flag | true, false |
| `scraper` | BOOLEAN | | Scraper functional group | true, false |
| `clinger` | BOOLEAN | | Clinger functional group | true, false |
| `product_ftv` | DECIMAL(8,2) | | FTV product value | 120.00, 8.00 |
| `product_tolerance` | DECIMAL(8,2) | | Tolerance product value | 90.00, 2.00 |
| `notes` | TEXT | | Bug record notes | "Larval stage", "Damaged specimen" |
| `created_date` | TIMESTAMP | DEFAULT NOW() | Record creation date | 2024-01-15 10:30:00 |
| `updated_date` | TIMESTAMP | DEFAULT NOW() | Last update date | 2024-01-15 10:30:00 |

**Sample Data**:
```sql
bug_record_id | sample_code    | order_name | family        | count | percentage | tolerance | ept   | insect | sensitive
--------------|----------------|------------|---------------|-------|------------|-----------|-------|--------|----------
BUG_000001    | SAMPLE_000001 | Diptera    | Chironomidae  | 15    | 15.50      | 6.0       | false | true   | false
BUG_000002    | SAMPLE_000001 | Trichoptera| Hydropsychidae| 8     | 8.25       | 2.0       | true  | true   | true
BUG_000003    | SAMPLE_000001 | Oligochaeta| Tubificidae   | 25    | 25.75      | 8.0       | false | false  | false
```

---

### 4. `bacteria` - Bacteria Test Results

**Purpose**: Stores bacteria testing data from various methods

| Column Name | Data Type | Constraints | Description | Example Values |
|-------------|-----------|-------------|-------------|----------------|
| `bacteria_record_id` | VARCHAR(50) | PRIMARY KEY | Unique bacteria record identifier | "BACT_000001" |
| `sample_code` | VARCHAR(50) | | Sample identifier | "BD1_2024-01-15" |
| `site_code` | VARCHAR(20) | FOREIGN KEY → sites.site_code | Site identifier | "BD1", "SB3" |
| `collection_date` | DATE | | Date sample was collected | 2024-01-15 |
| `collection_time` | TIME | | Time sample was collected | 14:30:00 |
| `measurement_value` | VARCHAR(100) | | Primary measurement value | "> 2419.6", "150.0" |
| `water_temperature` | DECIMAL(5,2) | | Water temperature in °C | 15.50, 22.30 |
| `turbidity` | DECIMAL(6,2) | | Turbidity in NTU | 5.20, 15.80 |
| `ph` | DECIMAL(4,2) | | pH level | 7.20, 8.50 |
| `do_ppm` | DECIMAL(6,3) | | Dissolved oxygen in mg/L | 8.50, 12.30 |
| `conductivity` | DECIMAL(8,2) | | Conductivity in µS/cm | 250.50, 450.30 |
| `total_coliforms` | DECIMAL(8,3) | | Total coliforms MPN/100mL | 100.000, 500.000 |
| `fecal_coliforms` | DECIMAL(8,3) | | Fecal coliforms MPN/100mL | 25.000, 150.000 |
| `e_coli` | DECIMAL(8,3) | | E. coli MPN/100mL | 50.000, 200.000 |
| `enterococci` | DECIMAL(8,3) | | Enterococci MPN/100mL | 10.000, 75.000 |
| `large_wells` | INTEGER | | Large wells count | 5, 0, 3 |
| `small_wells` | INTEGER | | Small wells count | 8, 2, 6 |
| `color_change_large_wells` | INTEGER | | Color change large wells | 3, 0, 2 |
| `color_change_small_wells` | INTEGER | | Color change small wells | 6, 1, 4 |
| `data_conditions` | VARCHAR(200) | | Data collection conditions | "High flow", "Clear water" |
| `quality_notes` | TEXT | | Quality control notes | "Sample temperature controlled" |
| `created_date` | TIMESTAMP | DEFAULT NOW() | Record creation date | 2024-01-15 10:30:00 |
| `updated_date` | TIMESTAMP | DEFAULT NOW() | Last update date | 2024-01-15 10:30:00 |

**Sample Data**:
```sql
bacteria_record_id | sample_code      | site_code | collection_date | e_coli | total_coliforms | water_temperature | ph
-------------------|------------------|-----------|-----------------|--------|-----------------|-------------------|----
BACT_000001        | BD1_2024-01-15   | BD1       | 2024-01-15      | 50.000 | 100.000         | 15.50            | 7.20
BACT_000002        | SB3_2024-01-15   | SB3       | 2024-01-15      | 200.000| 500.000         | 22.30            | 8.50
BACT_000003        | AC5_2024-01-16   | AC5       | 2024-01-16      | 25.000 | 75.000          | 18.75            | 7.80
```

---

## Reference Tables

### 5. `taxonomy` - Taxonomic Reference Data

**Purpose**: Stores taxonomic information and characteristics

| Column Name | Data Type | Constraints | Description | Example Values |
|-------------|-----------|-------------|-------------|----------------|
| `bug_id` | VARCHAR(50) | PRIMARY KEY | Unique taxonomy identifier | "TAX_000001" |
| `family` | VARCHAR(100) | NOT NULL | Taxonomic family | "Chironomidae", "Simuliidae" |
| `genus_species` | VARCHAR(100) | | Genus and species | "Diptera", "Trichoptera" |
| `tolerance_value` | DECIMAL(3,1) | | Pollution tolerance (1-10) | 6.0, 2.0, 8.0 |
| `ept` | BOOLEAN | | EPT taxon flag | true, false |
| `insect` | BOOLEAN | | Insect flag | true, false |
| `functional_group` | VARCHAR(50) | | Functional feeding group | "Scraper", "Collector", "Predator" |
| `habitat_preference` | VARCHAR(100) | | Preferred habitat | "Riffle", "Pool", "Vegetation" |
| `pollution_tolerance` | VARCHAR(50) | | Tolerance category | "Sensitive", "Moderate", "Tolerant" |
| `notes` | TEXT | | Additional notes | "Common in urban streams" |

**Sample Data**:
```sql
bug_id     | family        | genus_species | tolerance_value | ept   | insect | functional_group | pollution_tolerance
-----------|---------------|---------------|-----------------|-------|--------|-----------------|-------------------
TAX_000001 | Chironomidae  | Diptera       | 6.0             | false | true   | Collector        | Tolerant
TAX_000002 | Hydropsychidae| Trichoptera   | 2.0             | true  | true   | Filterer         | Sensitive
TAX_000003 | Tubificidae   | Oligochaeta   | 8.0             | false | false  | Collector        | Tolerant
```

---

### 6. `volunteers` - Volunteer Information

**Purpose**: Stores volunteer contact and training information

| Column Name | Data Type | Constraints | Description | Example Values |
|-------------|-----------|-------------|-------------|----------------|
| `volunteer_id` | VARCHAR(20) | PRIMARY KEY | Unique volunteer identifier | "VOL_001", "VOL_002" |
| `first_name` | VARCHAR(50) | NOT NULL | Volunteer first name | "John", "Jane" |
| `last_name` | VARCHAR(50) | NOT NULL | Volunteer last name | "Smith", "Doe" |
| `full_name` | VARCHAR(100) | | Full name | "John Smith", "Jane Doe" |
| `email` | VARCHAR(100) | | Email address | "john@email.com" |
| `phone` | VARCHAR(20) | | Phone number | "(555) 123-4567" |
| `city` | VARCHAR(50) | | City | "Kansas City", "St. Louis" |
| `state` | VARCHAR(2) | | State abbreviation | "MO", "KS" |
| `zip_code` | VARCHAR(10) | | ZIP code | "64101", "63101" |
| `start_date` | DATE | | Volunteer start date | 2024-01-15 |
| `training_status` | VARCHAR(20) | | Training completion status | "Certified", "In Progress" |
| `is_active` | BOOLEAN | DEFAULT true | Whether volunteer is active | true, false |
| `notes` | TEXT | | Additional notes | "Specializes in macroinvertebrates" |
| `created_date` | TIMESTAMP | DEFAULT NOW() | Record creation date | 2024-01-15 10:30:00 |
| `updated_date` | TIMESTAMP | DEFAULT NOW() | Last update date | 2024-01-15 10:30:00 |

**Sample Data**:
```sql
volunteer_id | first_name | last_name | email           | phone         | city        | state | is_active
-------------|------------|-----------|-----------------|---------------|-------------|-------|----------
VOL_001      | John       | Smith     | john@email.com  | (555) 123-4567| Kansas City | MO    | true
VOL_002      | Jane       | Doe       | jane@email.com  | (555) 987-6543| St. Louis   | MO    | true
VOL_003      | Bob        | Johnson   | bob@email.com   | (555) 456-7890| Springfield | MO    | false
```

---

## User Management Tables

### 7. `users` - Database Users

**Purpose**: Stores database user information

| Column Name | Data Type | Constraints | Description | Example Values |
|-------------|-----------|-------------|-------------|----------------|
| `user_id` | SERIAL | PRIMARY KEY | Unique user identifier | 1, 2, 3 |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Username | "streamwatch_readonly", "streamwatch_edit" |
| `email` | VARCHAR(100) | | Email address | "admin@streamwatch.org" |
| `role` | VARCHAR(20) | NOT NULL | User role | "readonly", "edit", "admin" |
| `is_active` | BOOLEAN | DEFAULT true | Whether user is active | true, false |
| `created_date` | TIMESTAMP | DEFAULT NOW() | Account creation date | 2024-01-15 10:30:00 |
| `last_login` | TIMESTAMP | | Last login date | 2024-01-15 10:30:00 |

---

## Data Relationships

### Foreign Key Relationships

```sql
-- Primary relationships
samples.site_code → sites.site_code
bugs.sample_code → samples.sample_id
bacteria.site_code → sites.site_code

-- Reference relationships
bugs.family → taxonomy.family (logical, not enforced)
```

### Relationship Diagram

```
sites (1) ←→ (many) samples (1) ←→ (many) bugs
  ↑                                    ↓
  └────────── (many) bacteria ←────────┘
                    ↓
              taxonomy (reference)
```

---

## Data Quality Standards

### Required Fields

**Sites Table**:
- `site_code` (PRIMARY KEY)
- `site_name`
- `is_active`

**Samples Table**:
- `sample_id` (PRIMARY KEY)
- `site_code` (FOREIGN KEY)
- `sample_date`

**Bugs Table**:
- `bug_record_id` (PRIMARY KEY)
- `sample_code` (FOREIGN KEY)
- `order_name`
- `family`
- `count`

### Data Validation Rules

1. **Numeric Ranges**:
   - `ph`: 0.0 to 14.0
   - `water_temperature`: -5.0 to 50.0 °C
   - `tolerance`: 1.0 to 10.0
   - `percentage`: 0.0 to 100.0

2. **String Lengths**:
   - `site_code`: 1-20 characters
   - `sample_id`: 1-50 characters
   - `email`: Valid email format

3. **Date Constraints**:
   - `sample_date`: Not in future
   - `start_date`: Not in future

### Data Completeness Targets

- **Sites**: 100% for required fields, 80% for optional fields
- **Samples**: 100% for required fields, 60% for measurement fields
- **Bugs**: 100% for required fields, 90% for calculated fields
- **Bacteria**: 100% for required fields, 70% for measurement fields

---

## Indexes and Performance

### Primary Indexes
```sql
-- Primary keys (automatically indexed)
sites.site_code
samples.sample_id
bugs.bug_record_id
bacteria.bacteria_record_id
volunteers.volunteer_id
taxonomy.bug_id
```

### Performance Indexes
```sql
-- Foreign key indexes
CREATE INDEX idx_samples_site_code ON samples(site_code);
CREATE INDEX idx_bugs_sample_code ON bugs(sample_code);
CREATE INDEX idx_bacteria_site_code ON bacteria(site_code);

-- Date indexes for time-series queries
CREATE INDEX idx_samples_date ON samples(sample_date);
CREATE INDEX idx_bacteria_date ON bacteria(collection_date);

-- Taxonomic indexes
CREATE INDEX idx_bugs_family ON bugs(family);
CREATE INDEX idx_bugs_order ON bugs(order_name);
```

---

## Data Entry Guidelines

### Site Codes
- Format: 2-4 letters + 1-2 numbers
- Examples: "BD1", "SB3", "AC5"
- Must be unique across all sites

### Sample IDs
- Format: "SAMPLE_" + 6-digit number
- Examples: "SAMPLE_000001", "SAMPLE_000002"
- Must be unique across all samples

### Bug Record IDs
- Format: "BUG_" + 6-digit number
- Examples: "BUG_000001", "BUG_000002"
- Must be unique across all bug records

### Bacteria Record IDs
- Format: "BACT_" + 6-digit number
- Examples: "BACT_000001", "BACT_000002"
- Must be unique across all bacteria records

---

## Common Queries

### Get All Sites
```sql
SELECT site_code, site_name, waterbody, latitude, longitude, is_active
FROM sites
ORDER BY site_code;
```

### Get Recent Samples
```sql
SELECT s.sample_id, s.site_code, st.site_name, s.sample_date, s.water_temperature, s.ph
FROM samples s
JOIN sites st ON s.site_code = st.site_code
WHERE s.sample_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY s.sample_date DESC;
```

### Get Bug Analysis for Sample
```sql
SELECT order_name, family, count, percentage, tolerance, ept, insect, sensitive
FROM bugs
WHERE sample_code = 'SAMPLE_000001'
ORDER BY count DESC;
```

### Calculate Water Quality Index
```sql
SELECT 
    site_code,
    AVG(water_temperature) as avg_temp,
    AVG(ph) as avg_ph,
    AVG(do_ppm) as avg_do,
    COUNT(*) as sample_count
FROM samples
WHERE sample_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY site_code
ORDER BY site_code;
```

---

*This documentation should be updated whenever the database schema changes. Last updated: October 2025*
