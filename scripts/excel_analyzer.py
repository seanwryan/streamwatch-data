#!/usr/bin/env python3
"""
Excel Data Analyzer for StreamWatch Data
This script focuses on analyzing Excel files and displaying their contents.
"""

import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def analyze_excel_file(file_path):
    """Analyze Excel files and display sheet information and sample data"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    try:
        # Get basic file info
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"File size: {file_size:.2f} MB")
        
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        print(f"Number of sheets: {len(excel_file.sheet_names)}")
        print(f"Sheet names: {excel_file.sheet_names}")
        
        # Analyze each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n{'='*60}")
            print(f"SHEET: {sheet_name}")
            print(f"{'='*60}")
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns")
                print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                
                # Show column information
                print(f"\nColumns ({len(df.columns)}):")
                for i, col in enumerate(df.columns):
                    non_null_count = df[col].count()
                    null_count = df[col].isnull().sum()
                    unique_count = df[col].nunique()
                    print(f"  {i+1:2d}. {col}")
                    print(f"      Type: {df[col].dtype}")
                    print(f"      Non-null: {non_null_count:,}")
                    print(f"      Null: {null_count:,}")
                    print(f"      Unique values: {unique_count:,}")
                    
                    # Show sample values for non-numeric columns
                    if df[col].dtype == 'object' and unique_count < 20:
                        sample_values = df[col].dropna().unique()[:10]
                        print(f"      Sample values: {sample_values}")
                    elif df[col].dtype in ['int64', 'float64']:
                        if not df[col].isna().all():
                            print(f"      Min: {df[col].min()}")
                            print(f"      Max: {df[col].max()}")
                            print(f"      Mean: {df[col].mean():.2f}")
                
                # Show sample data (first 10 rows)
                if not df.empty:
                    print(f"\nFirst 10 rows:")
                    pd.set_option('display.max_columns', None)
                    pd.set_option('display.width', None)
                    print(df.head(10).to_string(index=False))
                else:
                    print("Sheet is empty")
                    
            except Exception as e:
                print(f"Error reading sheet {sheet_name}: {e}")
                
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")

def main():
    """Main function to analyze Excel files in the data folder"""
    data_folder = "data"
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found!")
        return
    
    print("STREAMWATCH EXCEL DATA ANALYSIS")
    print("=" * 80)
    
    # Get Excel files in the data folder
    excel_files = []
    for f in os.listdir(data_folder):
        if f.endswith(('.xlsx', '.xlsm')) and os.path.isfile(os.path.join(data_folder, f)):
            excel_files.append(f)
    
    print(f"\nFound {len(excel_files)} Excel files:")
    for i, file in enumerate(excel_files, 1):
        file_path = os.path.join(data_folder, file)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"  {i}. {file} ({file_size:.2f} MB)")
    
    # Analyze each Excel file
    for file in excel_files:
        file_path = os.path.join(data_folder, file)
        analyze_excel_file(file_path)
    
    print(f"\n{'='*80}")
    print("EXCEL ANALYSIS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
