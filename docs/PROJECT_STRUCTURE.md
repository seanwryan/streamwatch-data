# StreamWatch Data Project Structure

## Project Overview
This project contains cleaned and organized StreamWatch water quality monitoring data from The Watershed Institute, including a SQLite database and analysis tools.

## Directory Structure

```
streamwatch-data/
├── data/                           # Original raw data files
│   ├── 2025 StreamWatch Locations.xlsx
│   ├── 2025 BACT Analysis.xlsx
│   ├── BAT Data Consolidation and Recount - Lily Raphael.xlsx
│   ├── 30 yr StreamWatch Data Analysis.xlsx
│   ├── Volunteer_Tracking.xlsm
│   ├── All StreamWatch Data.xlsx
│   └── ... (other original files)
│
├── cleaned_data/                   # Cleaned Excel files
│   ├── cleaned_2025 StreamWatch Locations.xlsx
│   ├── cleaned_2025 BACT Analysis.xlsx
│   ├── cleaned_BAT Data Consolidation and Recount - Lily Raphael.xlsx
│   └── ... (other cleaned files)
│
├── database/                       # Database files
│   └── streamwatch.db             # Main SQLite database
│
├── scripts/                        # Python analysis scripts
│   ├── database_explorer.py       # Interactive database explorer
│   ├── simple_database_import.py  # Database import script
│   ├── data_quality_assessor.py   # Data quality analysis
│   ├── comprehensive_data_cleaner.py # Data cleaning tools
│   ├── excel_analyzer.py          # Excel file analysis
│   ├── word_analyzer.py           # Word document analysis
│   └── requirements.txt           # Python dependencies
│
├── docs/                          # Documentation
│   ├── README.md                  # Main project documentation
│   ├── DATABASE_SUMMARY.md        # Database overview
│   ├── DATA_CLEANING_REPORT.md    # Cleaning process report
│   ├── CLEANING_CHANGES_SUMMARY.md # Detailed cleaning changes
│   └── PROJECT_STRUCTURE.md       # This file
│
├── exports/                       # Exported analysis files
│   ├── analysis_report_*.txt      # Analysis reports
│   ├── column_mapping_*.xlsx      # Column mapping templates
│   └── column_naming_*.csv        # Column naming suggestions
│
└── backups/                       # Backup files
```

## Database Data Sources

The SQLite database (`database/streamwatch.db`) contains data from **3 main source files**:

### 1. Sites Data (168 records)
- **Source**: `2025 StreamWatch Locations.xlsx`
- **Content**: Monitoring site locations with GPS coordinates
- **Fields**: Site ID, Site Name, Waterbody, Latitude, Longitude, Description

### 2. Water Quality Data (849 records)
- **Source**: `2025 BACT Analysis.xlsx`
- **Content**: Water quality measurements from 2025
- **Parameters**: Chloride (261), Phosphate (250), Nitrate (121), Turbidity (115), Phycocyanin (102)

### 3. Biological Data (1,279 records)
- **Source**: `BAT Data Consolidation and Recount - Lily Raphael.xlsx`
- **Content**: Macroinvertebrate sampling data
- **Coverage**: 78 species, 13,904 total individuals

## How to Use the Project

### 1. Explore the Database
```bash
cd scripts
python database_explorer.py
```

### 2. Access the Database Directly
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('database/streamwatch.db')
df = pd.read_sql_query("SELECT * FROM sites", conn)
```

### 3. Run Data Analysis
```bash
cd scripts
python data_quality_assessor.py
python excel_analyzer.py
```

### 4. Clean New Data
```bash
cd scripts
python comprehensive_data_cleaner.py
```

## Key Files

### Essential Files
- `database/streamwatch.db` - Main database (159 KB)
- `scripts/database_explorer.py` - Interactive data explorer
- `scripts/simple_database_import.py` - Database import script
- `docs/README.md` - Main documentation

### Data Files
- `data/` - Original raw data (41.12 MB total)
- `cleaned_data/` - Cleaned data files (reduced size, standardized format)

### Analysis Tools
- `scripts/data_quality_assessor.py` - Data quality analysis
- `scripts/comprehensive_data_cleaner.py` - Data cleaning tools
- `scripts/excel_analyzer.py` - Excel file analysis

## Project Benefits

### For The Watershed Institute:
1. **Organized Data**: Clean, structured data ready for analysis
2. **Free Database**: SQLite database with no licensing costs
3. **Easy Access**: Interactive tools for data exploration
4. **Scalable**: Can handle additional data as it becomes available
5. **Portable**: Single database file, easy to backup and share

### For Data Analysis:
1. **Standardized Format**: Consistent data types and naming
2. **Quality Flags**: Data quality indicators for monitoring
3. **SQL Queries**: Standard database queries for analysis
4. **Export Capabilities**: Easy export to CSV, Excel, etc.

## Next Steps

### Immediate Use:
1. Run `python scripts/database_explorer.py` to explore data
2. Use SQL queries for custom analysis
3. Export data for external tools

### Future Development:
1. Add visualization dashboard (Streamlit, etc.)
2. Implement automated data import workflows
3. Create reporting templates
4. Add more data validation rules

## File Sizes
- **Original Data**: 41.12 MB (18 files)
- **Cleaned Data**: ~12 MB (10 files)
- **Database**: 159 KB (single file)
- **Scripts**: ~100 KB (15 Python files)
- **Documentation**: ~50 KB (4 markdown files)

The project provides a complete data management solution for StreamWatch water quality monitoring data, from raw files to a clean, queryable database.
