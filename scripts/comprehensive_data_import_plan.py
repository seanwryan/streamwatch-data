#!/usr/bin/env python3
"""
Comprehensive Data Import Plan for StreamWatch Data
This script analyzes all raw data files and creates a plan to import everything into the database
"""

import os
import pandas as pd
import sqlite3
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def analyze_all_files():
    """Analyze all raw data files to understand what needs to be imported"""
    print("COMPREHENSIVE STREAMWATCH DATA ANALYSIS")
    print("=" * 60)
    
    data_folder = "../data"
    files = [f for f in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, f))]
    
    file_analysis = {
        'excel_files': [],
        'word_files': [],
        'pdf_files': [],
        'access_files': []
    }
    
    for file in files:
        file_path = os.path.join(data_folder, file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        if file.endswith(('.xlsx', '.xlsm')):
            file_analysis['excel_files'].append({
                'name': file,
                'size_mb': file_size,
                'type': 'Excel'
            })
        elif file.endswith('.docx'):
            file_analysis['word_files'].append({
                'name': file,
                'size_mb': file_size,
                'type': 'Word'
            })
        elif file.endswith('.pdf'):
            file_analysis['pdf_files'].append({
                'name': file,
                'size_mb': file_size,
                'type': 'PDF'
            })
        elif file.endswith('.accdb'):
            file_analysis['access_files'].append({
                'name': file,
                'size_mb': file_size,
                'type': 'Access'
            })
    
    return file_analysis

def create_import_plan():
    """Create a comprehensive import plan for all data files"""
    print("\nCOMPREHENSIVE DATA IMPORT PLAN")
    print("=" * 60)
    
    plan = {
        'phase_1_priority': [
            {
                'file': '2025 StreamWatch Locations.xlsx',
                'status': 'COMPLETED',
                'data_type': 'Sites',
                'records': 168,
                'description': 'Monitoring site locations with GPS coordinates'
            },
            {
                'file': '2025 BACT Analysis.xlsx',
                'status': 'COMPLETED',
                'data_type': 'Water Quality',
                'records': 849,
                'description': 'Water quality measurements (Chloride, Nitrate, Phosphate, Turbidity, Phycocyanin)'
            },
            {
                'file': 'BAT Data Consolidation and Recount - Lily Raphael.xlsx',
                'status': 'COMPLETED',
                'data_type': 'Biological',
                'records': 1279,
                'description': 'Macroinvertebrate sampling data'
            }
        ],
        'phase_2_high_priority': [
            {
                'file': 'All StreamWatch Data.xlsx',
                'status': 'NEEDS IMPORT',
                'data_type': 'Historical Water Quality',
                'estimated_records': '16,953+',
                'description': '30+ years of consolidated water quality data',
                'sheets': 30,
                'priority': 'HIGH'
            },
            {
                'file': '30 yr StreamWatch Data Analysis.xlsx',
                'status': 'NEEDS IMPORT',
                'data_type': 'Analysis Results',
                'estimated_records': '12,734+',
                'description': 'Historical analysis and trend data',
                'sheets': 24,
                'priority': 'HIGH'
            },
            {
                'file': 'Volunteer_Tracking.xlsm',
                'status': 'NEEDS IMPORT',
                'data_type': 'Volunteer Management',
                'estimated_records': '431+',
                'description': 'Volunteer information, training, and assignments',
                'sheets': 8,
                'priority': 'HIGH'
            }
        ],
        'phase_3_medium_priority': [
            {
                'file': 'BACT and HAB 2025 Data.xlsx',
                'status': 'NEEDS IMPORT',
                'data_type': 'Bacterial & Algal Bloom',
                'estimated_records': '2,724+',
                'description': 'Bacterial testing and harmful algal bloom data',
                'sheets': 8,
                'priority': 'MEDIUM'
            },
            {
                'file': '2024 TWI WQX Submission.xlsx',
                'status': 'NEEDS IMPORT',
                'data_type': 'Regulatory Submission',
                'estimated_records': '1,644+',
                'description': 'Data prepared for DEP WQX submission',
                'sheets': 13,
                'priority': 'MEDIUM'
            },
            {
                'file': 'BATSITES COLLECTED.xlsx',
                'status': 'NEEDS IMPORT',
                'data_type': 'Biological Sites',
                'estimated_records': '7,339+',
                'description': 'Biological assessment site data and bug counts',
                'sheets': 2,
                'priority': 'MEDIUM'
            },
            {
                'file': 'tblSampleDates.xlsx',
                'status': 'NEEDS IMPORT',
                'data_type': 'Sample Tracking',
                'estimated_records': '1,326+',
                'description': 'Sample date tracking and bug results',
                'sheets': 4,
                'priority': 'MEDIUM'
            }
        ],
        'phase_4_lower_priority': [
            {
                'file': 'CAT Meter Tracking.xlsx',
                'status': 'NEEDS IMPORT',
                'data_type': 'Equipment',
                'estimated_records': '100+',
                'description': 'Chemical Action Team meter tracking and calibration',
                'sheets': 6,
                'priority': 'LOW'
            },
            {
                'file': 'Database Project Plan.xlsx',
                'status': 'DOCUMENTATION',
                'data_type': 'Project Management',
                'estimated_records': 'N/A',
                'description': 'Project planning and timeline documentation',
                'priority': 'LOW'
            }
        ],
        'documentation_files': [
            {
                'file': 'Goals for Data Organization, Reporting, and Visualization.docx',
                'status': 'DOCUMENTATION',
                'description': 'Project goals and requirements'
            },
            {
                'file': '2025 Data Questions.docx',
                'status': 'DOCUMENTATION',
                'description': 'Data quality questions and flagging criteria'
            },
            {
                'file': 'BugCountsInfo.docx',
                'status': 'DOCUMENTATION',
                'description': 'Biological assessment methodology and indices'
            },
            {
                'file': 'DataDictionary.pdf',
                'status': 'DOCUMENTATION',
                'description': 'Data dictionary and field definitions'
            },
            {
                'file': 'ModelingInstructions.pdf',
                'status': 'DOCUMENTATION',
                'description': 'Data modeling and analysis instructions'
            },
            {
                'file': "Jian's Test DB.accdb",
                'status': 'LEGACY',
                'description': 'Legacy Access database (7.7 MB)'
            }
        ]
    }
    
    return plan

def print_import_plan(plan):
    """Print the comprehensive import plan"""
    
    print("\nPHASE 1 - COMPLETED (3 files)")
    print("-" * 40)
    for item in plan['phase_1_priority']:
        print(f"✅ {item['file']}")
        print(f"   Data: {item['data_type']} ({item['records']} records)")
        print(f"   Description: {item['description']}")
        print()
    
    print("PHASE 2 - HIGH PRIORITY (3 files)")
    print("-" * 40)
    for item in plan['phase_2_high_priority']:
        print(f"🔴 {item['file']}")
        print(f"   Data: {item['data_type']} (~{item['estimated_records']} records)")
        print(f"   Sheets: {item['sheets']}")
        print(f"   Description: {item['description']}")
        print()
    
    print("PHASE 3 - MEDIUM PRIORITY (4 files)")
    print("-" * 40)
    for item in plan['phase_3_medium_priority']:
        print(f"🟡 {item['file']}")
        print(f"   Data: {item['data_type']} (~{item['estimated_records']} records)")
        print(f"   Sheets: {item['sheets']}")
        print(f"   Description: {item['description']}")
        print()
    
    print("PHASE 4 - LOWER PRIORITY (2 files)")
    print("-" * 40)
    for item in plan['phase_4_lower_priority']:
        print(f"🟢 {item['file']}")
        print(f"   Data: {item['data_type']} (~{item['estimated_records']} records)")
        print(f"   Description: {item['description']}")
        print()
    
    print("DOCUMENTATION FILES (6 files)")
    print("-" * 40)
    for item in plan['documentation_files']:
        print(f"📄 {item['file']}")
        print(f"   Type: {item['status']}")
        print(f"   Description: {item['description']}")
        print()

def create_database_schema_extension():
    """Create extended database schema for all data types"""
    print("\nEXTENDED DATABASE SCHEMA PLAN")
    print("=" * 60)
    
    schema_plan = {
        'existing_tables': [
            'sites (168 records)',
            'water_quality (849 records)', 
            'biological_data (1,279 records)'
        ],
        'new_tables_needed': [
            {
                'table': 'historical_water_quality',
                'source': 'All StreamWatch Data.xlsx',
                'description': '30+ years of historical water quality data'
            },
            {
                'table': 'analysis_results',
                'source': '30 yr StreamWatch Data Analysis.xlsx',
                'description': 'Statistical analysis and trend data'
            },
            {
                'table': 'volunteers',
                'source': 'Volunteer_Tracking.xlsm',
                'description': 'Volunteer information and training records'
            },
            {
                'table': 'volunteer_assignments',
                'source': 'Volunteer_Tracking.xlsm',
                'description': 'Site assignments and scheduling'
            },
            {
                'table': 'bacterial_data',
                'source': 'BACT and HAB 2025 Data.xlsx',
                'description': 'E. coli and bacterial testing results'
            },
            {
                'table': 'algal_bloom_data',
                'source': 'BACT and HAB 2025 Data.xlsx',
                'description': 'Harmful algal bloom monitoring data'
            },
            {
                'table': 'regulatory_submissions',
                'source': '2024 TWI WQX Submission.xlsx',
                'description': 'Data prepared for regulatory submissions'
            },
            {
                'table': 'equipment_tracking',
                'source': 'CAT Meter Tracking.xlsx',
                'description': 'Equipment calibration and maintenance'
            },
            {
                'table': 'sample_tracking',
                'source': 'tblSampleDates.xlsx',
                'description': 'Sample collection and processing tracking'
            }
        ]
    }
    
    print("EXISTING TABLES:")
    for table in schema_plan['existing_tables']:
        print(f"  ✅ {table}")
    
    print("\nNEW TABLES NEEDED:")
    for table in schema_plan['new_tables_needed']:
        print(f"  📋 {table['table']}")
        print(f"     Source: {table['source']}")
        print(f"     Description: {table['description']}")
        print()

def estimate_total_data_volume():
    """Estimate total data volume after full import"""
    print("\nESTIMATED TOTAL DATA VOLUME")
    print("=" * 60)
    
    estimates = {
        'current_database': {
            'sites': 168,
            'water_quality': 849,
            'biological_data': 1279,
            'total_current': 2296
        },
        'additional_data': {
            'historical_water_quality': 16953,
            'analysis_results': 12734,
            'volunteers': 431,
            'bacterial_data': 2724,
            'regulatory_data': 1644,
            'biological_sites': 7339,
            'sample_tracking': 1326,
            'equipment_data': 100
        }
    }
    
    current_total = estimates['current_database']['total_current']
    additional_total = sum(estimates['additional_data'].values())
    final_total = current_total + additional_total
    
    print(f"Current database: {current_total:,} records")
    print(f"Additional data to import: {additional_total:,} records")
    print(f"Final database size: {final_total:,} records")
    print()
    
    print("Breakdown by data type:")
    for data_type, count in estimates['additional_data'].items():
        print(f"  {data_type}: {count:,} records")

def main():
    """Main function to create comprehensive import plan"""
    file_analysis = analyze_all_files()
    plan = create_import_plan()
    
    print_import_plan(plan)
    create_database_schema_extension()
    estimate_total_data_volume()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS RECOMMENDATION")
    print("=" * 60)
    print("1. Start with Phase 2 (HIGH PRIORITY) files")
    print("2. Import 'All StreamWatch Data.xlsx' first (largest dataset)")
    print("3. Then import '30 yr StreamWatch Data Analysis.xlsx'")
    print("4. Add volunteer tracking data")
    print("5. Continue with Phase 3 files")
    print("6. Update database schema as needed")
    print("7. Create comprehensive data validation")
    print("8. Build visualization dashboard")
    print()
    print("This will give The Watershed Institute access to ALL their data")
    print("in a single, organized, queryable database!")

if __name__ == "__main__":
    main()
