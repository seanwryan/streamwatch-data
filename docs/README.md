# StreamWatch Data Analysis

This repository contains Python scripts to analyze and explore the StreamWatch water quality monitoring data.

## Overview

The data folder contains **18 files** totaling **41.12 MB** of water quality monitoring data from StreamWatch, including:

- **12 Excel files** (29.21 MB) - Main data files with water quality measurements
- **1 Access Database** (7.70 MB) - Test database file
- **2 PDF files** (4.14 MB) - Data dictionary and modeling instructions
- **3 Word documents** (0.07 MB) - Documentation and planning materials

## Key Data Files

### Major Excel Files
1. **30 yr StreamWatch Data Analysis.xlsx** (11.50 MB, 24 sheets)
   - Contains 12,734 rows of historical water quality data
   - BACT data, standard violations, and comprehensive analysis

2. **Volunteer_Tracking.xlsm** (8.91 MB, 8 sheets)
   - Volunteer management and training records
   - Dashboard and tracking systems

3. **All StreamWatch Data.xlsx** (3.71 MB, 30 sheets)
   - Data dictionary with 363 entries
   - 16,953 rows of consolidated water quality data

### Specialized Data Files
- **BACT and HAB 2025 Data.xlsx** - Bacterial and harmful algal bloom monitoring
- **2025 BACT Analysis.xlsx** - Temperature, E. coli, and turbidity analysis
- **BATSITES COLLECTED.xlsx** - Biological assessment team data (7,339 bug samples)
- **2025 StreamWatch Locations.xlsx** - 168 monitoring site locations

## Analysis Scripts

### 1. `excel_analyzer.py`
Comprehensive analysis of Excel files showing:
- Sheet-by-sheet breakdown
- Row and column counts
- Data types and sample values
- Memory usage statistics

### 2. `word_analyzer.py`
Extracts and analyzes Word document content:
- Paragraph counts
- Character counts
- Full text extraction for smaller documents

### 3. `data_summary.py`
Provides a complete overview of all data files:
- File sizes and types
- Modification dates
- Key insights and statistics

## Data Content Summary

### Water Quality Parameters
- **Chemical**: pH, dissolved oxygen, conductivity, TDS, temperature
- **Biological**: E. coli, bug counts, phycocyanin levels
- **Physical**: Turbidity, temperature, atmospheric pressure

### Geographic Coverage
- **63 waterbodies** including streams, lakes, and ponds
- **160 monitoring sites** with GPS coordinates
- Focus on New Jersey watersheds (Crosswicks Creek, Assunpink Creek, etc.)

### Temporal Scope
- Data spans multiple years (2024-2025)
- Historical analysis covering 30 years
- Regular monitoring with follow-up assessments

### Data Quality
- Multiple measurement replicates (e.g., 3-4 turbidity readings per sample)
- Quality control flags and status indicators
- Metadata tracking for equipment calibration and volunteer training

## Usage

### Prerequisites
```bash
pip install pandas openpyxl xlrd
```

### Running the Scripts
```bash
# Analyze Excel files in detail
python excel_analyzer.py

# Extract Word document content
python word_analyzer.py

# Get comprehensive data summary
python data_summary.py
```

## Key Insights

1. **Rich Data Structure**: 131 total Excel sheets across all files
2. **Comprehensive Monitoring**: Covers chemical, biological, and physical parameters
3. **Quality Assurance**: Multiple replicates and quality control measures
4. **Volunteer-Driven**: Extensive volunteer tracking and training systems
5. **Geographic Breadth**: Covers multiple watersheds and waterbody types

## Data Challenges

- **File Formats**: Mix of Excel, Word, PDF, and Access formats
- **Large Files**: Some Excel files exceed 10MB with complex structures
- **Unnamed Columns**: Some data sheets have unnamed columns that need cleaning
- **Missing Values**: Significant null values in some datasets

## Recommendations

1. **Data Consolidation**: Consider exporting key data to CSV format for easier analysis
2. **Standardization**: Implement consistent column naming across all sheets
3. **Quality Control**: Review and clean missing data patterns
4. **Database Migration**: Consider migrating from Excel to a proper database system

## File Structure
```
data/
├── Excel Files (12 files, 29.21 MB)
│   ├── 30 yr StreamWatch Data Analysis.xlsx (11.50 MB)
│   ├── Volunteer_Tracking.xlsm (8.91 MB)
│   ├── All StreamWatch Data.xlsx (3.71 MB)
│   └── ... (9 more files)
├── Access Database (1 file, 7.70 MB)
│   └── Jian's Test DB.accdb
├── PDF Files (2 files, 4.14 MB)
│   ├── DataDictionary.pdf (2.58 MB)
│   └── ModelingInstructions.pdf (1.55 MB)
└── Word Documents (3 files, 0.07 MB)
    ├── BugCountsInfo.docx (33.54 KB)
    ├── 2025 Data Questions.docx (24.79 KB)
    └── Goals for Data Organization.docx (17.57 KB)
```

## Contact

For questions about the data or analysis scripts, please refer to the StreamWatch team documentation or contact the data management team.
