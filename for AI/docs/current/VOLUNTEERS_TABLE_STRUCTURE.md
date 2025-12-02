# Volunteers Table Structure - Access Alignment

**Date**: October 2025  
**Purpose**: Align PostgreSQL volunteers table with Jian's Access VOLUNTEERtbl structure

---

## 📊 Target Structure (Matching Access)

### **volunteers table** (VOLUNTEERtbl)

| Column | Data Type | Access Field | Notes |
|--------|-----------|--------------|-------|
| **volunteer_id** | INTEGER (SERIAL) | VolunteerID | Primary Key |
| **perfect_id** | VARCHAR(50) | PerfectID | Perfect volunteer ID system |
| **first_name** | VARCHAR(100) | FirstName | |
| **last_name** | VARCHAR(100) | LastName | |
| **int_last_name** | VARCHAR(100) | IntLastName | Internal last name |
| **is_active** | BOOLEAN | isActive | Active status |
| **is_under_17** | BOOLEAN | isUnder17 | Age status |
| **address** | TEXT | Address | Full address |
| **email** | VARCHAR(255) | - | *Not in Access, but useful to keep* |
| **phone** | VARCHAR(20) | - | *Not in Access, but useful to keep* |
| **start_date** | DATE | - | *Not in Access, but useful to keep* |
| **created_date** | TIMESTAMP | - | Audit trail |
| **updated_date** | TIMESTAMP | - | Audit trail |

**Note**: `site_code` column will remain temporarily for backward compatibility but should be removed after migration to `volunteer_assignments` junction table.

---

## 🔗 Related Tables

### **1. training** (tblTraining)

| Column | Data Type | Access Field | Notes |
|--------|-----------|--------------|-------|
| **training_id** | SERIAL | TrainingID | Primary Key |
| **volunteer_id** | INTEGER | VolunteerID | Foreign Key → volunteers |
| **training_type** | VARCHAR(100) | TrainingType | Type of training |
| **training_date** | DATE | TrainingDate | When training occurred |
| **expiration_date** | DATE | ExpirationDate | When training expires |
| **test_score** | DECIMAL(5,2) | TestScore | Test score if applicable |
| **notes** | TEXT | Notes | Additional notes |
| **created_date** | TIMESTAMP | - | Audit trail |
| **updated_date** | TIMESTAMP | - | Audit trail |

**Relationship**: One volunteer can have many training records (One-to-Many)

---

### **2. volunteer_assignments** (juncAssignments)

| Column | Data Type | Access Field | Notes |
|--------|-----------|--------------|-------|
| **assignment_id** | SERIAL | AssignmentID | Primary Key |
| **volunteer_id** | INTEGER | VolunteerID | Foreign Key → volunteers |
| **site_code** | VARCHAR(50) | SiteID | Foreign Key → sites |
| **sector** | VARCHAR(50) | Sector | Assignment sector |
| **assign_start** | DATE | AssignStart | Assignment start date |
| **assign_end** | DATE | AssignEnd | Assignment end date |
| **notes** | TEXT | Notes | Additional notes |
| **is_valid** | BOOLEAN | Valid | Whether assignment is valid |
| **created_date** | TIMESTAMP | - | Audit trail |
| **updated_date** | TIMESTAMP | - | Audit trail |

**Relationship**: Many-to-Many between volunteers and sites
- One volunteer can be assigned to many sites
- One site can have many volunteers assigned

---

### **3. visit_attendance** (juncAttendance)

| Column | Data Type | Access Field | Notes |
|--------|-----------|--------------|-------|
| **attendance_id** | SERIAL | AttendanceID | Primary Key |
| **volunteer_id** | INTEGER | VolunteerID | Foreign Key → volunteers |
| **visit_id** | INTEGER | VisitID | Foreign Key → samples(sample_id) |
| **data_code** | VARCHAR(50) | DataCode | Data collection code |
| **notes** | TEXT | Notes | Additional notes |
| **created_date** | TIMESTAMP | - | Audit trail |
| **updated_date** | TIMESTAMP | - | Audit trail |

**Relationship**: Many-to-Many between volunteers and visits
- One volunteer can attend many visits
- One visit can have many volunteers present

---

## 🔄 Migration Strategy

### **Phase 1: Add Missing Columns**
- Add `perfect_id`, `int_last_name`, `is_under_17`, `address` to volunteers table
- Keep existing `email`, `phone`, `start_date` (useful additions)

### **Phase 2: Create Related Tables**
- Create `training` table
- Create `volunteer_assignments` table (junction)
- Create `visit_attendance` table (junction)

### **Phase 3: Migrate Existing Data**
- Migrate `volunteers.site_code` → `volunteer_assignments` (one-to-many becomes many-to-many)
- Migrate `samples.volunteer_id` → `visit_attendance` (one-to-many becomes many-to-many)

### **Phase 4: Data Population** (Future)
- Populate `perfect_id` from source data (if available)
- Populate `int_last_name` from source data (if available)
- Populate `training` table from source data
- Populate remaining `volunteer_assignments` from source data
- Populate remaining `visit_attendance` from source data

---

## 📋 Query Examples

### **Find All Volunteers and Their Site Assignments**
```sql
SELECT 
    v.volunteer_id,
    v.first_name || ' ' || v.last_name AS volunteer_name,
    s.site_code,
    s.site_name,
    va.assign_start,
    va.assign_end,
    va.is_valid
FROM volunteers v
JOIN volunteer_assignments va ON v.volunteer_id = va.volunteer_id
JOIN sites s ON va.site_code = s.site_code
WHERE va.is_valid = true;
```

### **Find All Volunteers and Their Training Records**
```sql
SELECT 
    v.volunteer_id,
    v.first_name || ' ' || v.last_name AS volunteer_name,
    t.training_type,
    t.training_date,
    t.expiration_date,
    t.test_score,
    CASE 
        WHEN t.expiration_date < CURRENT_DATE THEN 'EXPIRED'
        WHEN t.expiration_date <= CURRENT_DATE + INTERVAL '30 days' THEN 'EXPIRING SOON'
        ELSE 'CURRENT'
    END AS status
FROM volunteers v
LEFT JOIN training t ON v.volunteer_id = t.volunteer_id
ORDER BY v.last_name, t.training_date DESC;
```

### **Find All Volunteers Who Attended a Visit**
```sql
SELECT 
    sm.sample_id AS visit_id,
    sm.sample_date,
    s.site_name,
    v.first_name || ' ' || v.last_name AS volunteer_name,
    va.data_code,
    va.notes
FROM samples sm
JOIN visit_attendance va ON sm.sample_id = va.visit_id
JOIN volunteers v ON va.volunteer_id = v.volunteer_id
JOIN sites s ON sm.site_code = s.site_code
ORDER BY sm.sample_date DESC, s.site_code;
```

### **Find Volunteers with Multiple Site Assignments**
```sql
SELECT 
    v.volunteer_id,
    v.first_name || ' ' || v.last_name AS volunteer_name,
    COUNT(DISTINCT va.site_code) AS site_count,
    STRING_AGG(s.site_name, ', ' ORDER BY s.site_name) AS sites
FROM volunteers v
JOIN volunteer_assignments va ON v.volunteer_id = va.volunteer_id
JOIN sites s ON va.site_code = s.site_code
WHERE va.is_valid = true
GROUP BY v.volunteer_id, v.first_name, v.last_name
HAVING COUNT(DISTINCT va.site_code) > 1
ORDER BY site_count DESC;
```

---

## ✅ Status

- [x] Script created: `scripts/schema/fix_volunteers_table.py`
- [ ] Script executed and tested
- [ ] Data populated from source files
- [ ] Queries updated to use new junction tables
- [ ] Documentation updated

---

*This structure matches Jian's Access database VOLUNTEERtbl and related tables exactly.*



