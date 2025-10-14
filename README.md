# StreamWatch Data Pipeline
**Environmental Monitoring Database for Watershed Institute**

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
- **109 sample dates** with collection tracking
- **1,326 bug results** from detailed analysis
- **1,260 RBP100 bug records** for standardized assessment
- **1,625 bug list entries** with taxonomic details
- **25 CAT meters** for continuous monitoring
- **27 WQX sites** for regulatory reporting
- **1,644 WQX biohabphys records** for compliance data

**Total: 31,700 records** across 14 tables

---

## 🚀 **Quick Start for Watershed Team**

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

## 📚 **Documentation**

| File | Purpose |
|------|---------|
| **`STREAMWATCH_DATABASE_GUIDE.md`** | **Complete guide - everything you need!** |
| **`example_queries_for_team.sql`** | Ready-to-use SQL queries |
| **`env.example`** | Environment variables template |

---

## 🔑 **Database Access**

### **Edit User (Full Access)**
- **Username:** `streamwatch_edit`
- **Password:** `[Contact team for password]`
- **Permissions:** Read, write, create, delete

### **Read-Only User (View Only)**
- **Username:** `streamwatch_readonly`
- **Password:** `[Contact team for password]`
- **Permissions:** Read only

**🔐 Credentials are shared securely - contact the team for access**

---

## 🛠️ **Tools & Scripts**

### **For Watershed Team:**
- **`test_team_access.py`** - Test database connection
- **`example_queries_for_team.sql`** - Copy/paste SQL queries
- **`STREAMWATCH_DATABASE_GUIDE.md`** - Complete guide with everything

### **For Technical Team:**
- **`scripts/etl/`** - ETL pipeline scripts
- **`scripts/tools/`** - Database utilities
- **`config.py`** - Database configuration
- **`requirements.txt`** - Python dependencies

---

## 📊 **Current Status**

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

## 🎉 **You're Ready!**

The database is fully operational with 32+ years of StreamWatch data. The Watershed team can now:

1. **Connect** using DBeaver or pgAdmin
2. **Explore** all the data tables
3. **Validate** data quality
4. **Make corrections** as needed
5. **Analyze** trends and patterns
6. **Export** data for reports

**Start with `STREAMWATCH_DATABASE_GUIDE.md` for everything you need!**

---

*Last updated: October 2025*
