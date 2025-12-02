# StreamWatch Database Schema

## Tables

### **sites** (169 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| site_code | VARCHAR(50) | Primary Key |
| site_name | VARCHAR(255) | Site name |
| latitude | DECIMAL(10,8) | GPS latitude |
| longitude | DECIMAL(11,8) | GPS longitude |
| elevation | DECIMAL(8,2) | Elevation in feet |
| watershed | VARCHAR(100) | Watershed name |
| notes | TEXT | Site notes |
| created_date | TIMESTAMP | Record creation date |
| updated_date | TIMESTAMP | Last update date |

### **samples** (16,910 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| sample_id | SERIAL | Primary Key |
| site_code | VARCHAR(50) | Foreign Key → sites |
| sample_code | VARCHAR(100) | Unique sample identifier |
| sample_date | DATE | Collection date |
| water_temperature | DECIMAL(5,2) | Temperature in °C |
| ph | DECIMAL(4,2) | pH value |
| dissolved_oxygen | DECIMAL(5,2) | DO in mg/L |
| conductivity | DECIMAL(8,2) | Conductivity in µS/cm |
| turbidity | DECIMAL(6,2) | Turbidity in NTU |
| volunteer_id | INTEGER | Foreign Key → volunteers |
| notes | TEXT | Sample notes |
| created_date | TIMESTAMP | Record creation date |
| updated_date | TIMESTAMP | Last update date |

### **bugs** (7,339 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| bug_id | SERIAL | Primary Key |
| sample_code | VARCHAR(100) | Foreign Key → samples |
| site_code | VARCHAR(50) | Foreign Key → sites |
| genus_species | VARCHAR(100) | Foreign Key → taxonomy |
| count | INTEGER | Number of individuals |
| percentage | DECIMAL(5,2) | Percentage of total |
| tolerance_value | DECIMAL(3,1) | Tolerance value |
| ept | BOOLEAN | EPT flag |
| insect | BOOLEAN | Insect flag |
| sensitive | BOOLEAN | Sensitivity flag |
| created_date | TIMESTAMP | Record creation date |
| updated_date | TIMESTAMP | Last update date |

### **bacteria** (669 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| bacteria_record_id | VARCHAR(50) | Primary Key |
| sample_code | VARCHAR(100) | Foreign Key → samples |
| site_code | VARCHAR(50) | Foreign Key → sites |
| e_coli | INTEGER | E. coli count |
| water_temperature | DECIMAL(5,2) | Temperature in °C |
| turbidity | DECIMAL(6,2) | Turbidity in NTU |
| ph | DECIMAL(4,2) | pH value |
| do_ppm | DECIMAL(5,2) | Dissolved oxygen in ppm |
| conductivity | DECIMAL(8,2) | Conductivity in µS/cm |
| large_wells | INTEGER | Large wells count |
| small_wells | INTEGER | Small wells count |
| color_change_large_wells | INTEGER | Color change large wells |
| color_change_small_wells | INTEGER | Color change small wells |
| data_conditions | TEXT | Data collection conditions |
| quality_notes | TEXT | Quality control notes |
| created_date | TIMESTAMP | Record creation date |
| updated_date | TIMESTAMP | Last update date |

### **volunteers** (428 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| volunteer_id | SERIAL | Primary Key |
| site_code | VARCHAR(50) | Foreign Key → sites |
| first_name | VARCHAR(100) | First name |
| last_name | VARCHAR(100) | Last name |
| email | VARCHAR(255) | Email address |
| phone | VARCHAR(20) | Phone number |
| start_date | DATE | Start date |
| is_active | BOOLEAN | Active status |
| created_date | TIMESTAMP | Record creation date |
| updated_date | TIMESTAMP | Last update date |

### **taxonomy** (149 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| genus_species | VARCHAR(100) | Primary Key |
| order_name | VARCHAR(100) | Taxonomic order |
| family_name | VARCHAR(100) | Taxonomic family |
| tolerance_value | DECIMAL(3,1) | Tolerance value |
| ept_flag | BOOLEAN | EPT flag |
| insect_flag | BOOLEAN | Insect flag |
| sensitive_flag | BOOLEAN | Sensitivity flag |
| created_date | TIMESTAMP | Record creation date |
| updated_date | TIMESTAMP | Last update date |

### **users** (0 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| user_id | SERIAL | Primary Key |
| username | VARCHAR(50) | Username |
| email | VARCHAR(255) | Email address |
| role | VARCHAR(20) | User role |
| is_active | BOOLEAN | Active status |
| created_date | TIMESTAMP | Record creation date |
| updated_date | TIMESTAMP | Last update date |

### **sample_dates** (1,671 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| sample_date_id | SERIAL | Primary Key |
| sample_code | VARCHAR(100) | Sample identifier |
| sample_date | DATE | Collection date |
| site_code | VARCHAR(50) | Site code |
| volunteer_name | VARCHAR(100) | Volunteer name |

### **bug_results** (1,671 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| bug_result_id | SERIAL | Primary Key |
| sample_code | VARCHAR(100) | Sample identifier |
| site_code | VARCHAR(50) | Site code |
| genus_species | VARCHAR(100) | Species name |
| count | INTEGER | Count value |
| notes | TEXT | Notes |

### **rbp100_bugs** (1,671 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| rbp100_id | SERIAL | Primary Key |
| sample_code | VARCHAR(100) | Sample identifier |
| site_code | VARCHAR(50) | Site code |
| genus_species | VARCHAR(100) | Species name |
| rbp100_score | INTEGER | RBP100 score |
| tolerance_value | DECIMAL(3,1) | Tolerance value |

### **bug_list** (149 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| bug_list_id | SERIAL | Primary Key |
| genus_species | VARCHAR(100) | Species name |
| order_name | VARCHAR(100) | Taxonomic order |
| family_name | VARCHAR(100) | Taxonomic family |
| tolerance_value | DECIMAL(3,1) | Tolerance value |

### **wqx_sites** (1,671 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| wqx_site_id | SERIAL | Primary Key |
| site_code | VARCHAR(50) | Site code |
| wqx_identifier | VARCHAR(100) | WQX identifier |
| site_name | VARCHAR(255) | Site name |
| latitude | DECIMAL(10,8) | GPS latitude |
| longitude | DECIMAL(11,8) | GPS longitude |

### **wqx_biohabphys** (1,671 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| wqx_bio_id | SERIAL | Primary Key |
| site_code | VARCHAR(50) | Site code |
| sample_code | VARCHAR(100) | Sample identifier |
| parameter | VARCHAR(100) | Parameter name |
| value | DECIMAL(10,4) | Parameter value |
| unit | VARCHAR(20) | Unit of measurement |

### **cat_assignments** (25 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| assignment_id | SERIAL | Primary Key |
| meter_id | VARCHAR(50) | Meter identifier |
| site_code | VARCHAR(50) | Site code |
| assignment_date | DATE | Assignment date |
| status | VARCHAR(20) | Assignment status |

### **cat_meters** (25 records)
| Column | Data Type | Description |
|--------|-----------|-------------|
| meter_id | VARCHAR(50) | Primary Key |
| meter_name | VARCHAR(100) | Meter name |
| model | VARCHAR(100) | Meter model |
| serial_number | VARCHAR(100) | Serial number |
| status | VARCHAR(20) | Meter status |
| last_calibration | DATE | Last calibration date |

