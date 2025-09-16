"""
Configuration file for StreamWatch ETL Pipeline
Contains database connection settings and data file paths
"""

import os
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'streamwatch',
    'user': 'streamwatch_user',
    'password': 'password'
}

# Data file paths
DATA_PATHS = {
    'sites': 'data/raw/2025 StreamWatch Locations.xlsx',
    'samples': 'data/raw/30 yr StreamWatch Data Analysis.xlsx',
    'bugs': 'data/raw/All StreamWatch Data.xlsx',
    'bacteria': 'data/raw/BACT and HAB 2025 Data.xlsx',
    'volunteers': 'data/raw/Volunteer_Tracking.xlsm',
    'batsites': 'data/raw/BATSITES COLLECTED.xlsx',
    'cat_meter': 'data/raw/CAT Meter Tracking.xlsx',
    'wqx_submission': 'data/raw/2024 TWI WQX Submission.xlsx',
    'sample_dates': 'data/raw/tblSampleDates.xlsx',
    'database_plan': 'data/raw/Database Project Plan.xlsx'
}

# ETL settings
ETL_SETTINGS = {
    'chunk_size': 1000,
    'log_level': 'INFO',
    'backup_before_load': True
}

# Data cleaning settings
CLEANING_SETTINGS = {
    'remove_duplicates': True,
    'standardize_text': True,
    'validate_ranges': True,
    'handle_missing_values': True
}
