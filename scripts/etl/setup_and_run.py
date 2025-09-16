#!/usr/bin/env python3
"""
Setup and run script for StreamWatch ETL pipeline
Automates the complete setup and data loading process
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        'pandas',
        'psycopg2-binary',
        'sqlalchemy',
        'openpyxl'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        install_command = f"pip install {' '.join(missing_packages)}"
        return run_command(install_command, "Package installation")
    
    return True

def check_data_files():
    """Check if required data files exist"""
    print("\n🔍 Checking data files...")
    
    required_files = [
        'data/raw/2025 StreamWatch Locations.xlsx',
        'data/raw/30 yr StreamWatch Data Analysis.xlsx',
        'data/raw/All StreamWatch Data.xlsx',
        'data/raw/BACT and HAB 2025 Data.xlsx',
        'data/raw/Volunteer_Tracking.xlsm'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} is missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing data files: {', '.join(missing_files)}")
        print("Please ensure all data files are in the data/raw/ directory")
        return False
    
    return True

def setup_database():
    """Set up the database schema"""
    return run_command("python create_database_schema.py", "Database schema creation")

def run_etl():
    """Run the ETL pipeline"""
    return run_command("python streamwatch_etl.py", "ETL pipeline execution")

def test_connection():
    """Test database connection"""
    return run_command("python test_connection.py", "Database connection test")

def main():
    """Main setup and run function"""
    print("🚀 StreamWatch ETL Pipeline Setup and Run")
    print("=" * 50)
    
    # Step 1: Check requirements
    if not check_requirements():
        print("❌ Requirements check failed. Please install missing packages.")
        return False
    
    # Step 2: Check data files
    if not check_data_files():
        print("❌ Data files check failed. Please ensure all data files are present.")
        return False
    
    # Step 3: Set up database
    if not setup_database():
        print("❌ Database setup failed.")
        return False
    
    # Step 4: Run ETL pipeline
    if not run_etl():
        print("❌ ETL pipeline failed.")
        return False
    
    # Step 5: Test connection
    if not test_connection():
        print("❌ Connection test failed.")
        return False
    
    print("\n🎉 StreamWatch ETL pipeline setup and execution completed successfully!")
    print("📊 Your database is ready for data verification and analysis.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

