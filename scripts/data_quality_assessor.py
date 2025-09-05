#!/usr/bin/env python3
"""
Data Quality Assessor for StreamWatch Data
This script analyzes data quality issues in Excel files, focusing on large files.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def assess_data_quality(file_path, max_rows_per_sheet=1000):
    """Assess data quality issues in an Excel file"""
    print(f"\n{'='*80}")
    print(f"ASSESSING DATA QUALITY: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    try:
        # Get basic file info
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"File size: {file_size:.2f} MB")
        
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        print(f"Number of sheets: {len(excel_file.sheet_names)}")
        
        quality_issues = {
            'file': os.path.basename(file_path),
            'sheets': [],
            'total_issues': 0
        }
        
        # Analyze each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- Analyzing Sheet: {sheet_name} ---")
            
            try:
                # For large files, read only a sample of rows to assess quality
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=max_rows_per_sheet)
                
                sheet_issues = {
                    'sheet_name': sheet_name,
                    'dimensions': f"{df.shape[0]:,} rows × {df.shape[1]} columns",
                    'issues': []
                }
                
                # Check for common data quality issues
                
                # 1. Unnamed columns
                unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
                if unnamed_cols:
                    sheet_issues['issues'].append(f"Unnamed columns: {len(unnamed_cols)} ({unnamed_cols[:5]})")
                    quality_issues['total_issues'] += len(unnamed_cols)
                
                # 2. Completely empty columns
                empty_cols = [col for col in df.columns if df[col].isna().all()]
                if empty_cols:
                    sheet_issues['issues'].append(f"Completely empty columns: {len(empty_cols)}")
                    quality_issues['total_issues'] += len(empty_cols)
                
                # 3. High percentage of missing values
                high_missing = []
                for col in df.columns:
                    if df[col].dtype == 'object':  # Only check text columns
                        missing_pct = (df[col].isna().sum() / len(df)) * 100
                        if missing_pct > 50:
                            high_missing.append(f"{col} ({missing_pct:.1f}% missing)")
                
                if high_missing:
                    sheet_issues['issues'].append(f"High missing values: {len(high_missing)} columns")
                    quality_issues['total_issues'] += len(high_missing)
                
                # 4. Duplicate rows
                duplicates = df.duplicated().sum()
                if duplicates > 0:
                    sheet_issues['issues'].append(f"Duplicate rows: {duplicates}")
                    quality_issues['total_issues'] += duplicates
                
                # 5. Inconsistent data types
                type_issues = []
                for col in df.columns:
                    if df[col].dtype == 'object':
                        # Check if column should be numeric but has text
                        non_null_values = df[col].dropna()
                        if len(non_null_values) > 0:
                            try:
                                pd.to_numeric(non_null_values, errors='raise')
                            except:
                                # Check if it's mostly numeric with some text
                                numeric_count = 0
                                for val in non_null_values:
                                    try:
                                        float(str(val))
                                        numeric_count += 1
                                    except:
                                        pass
                                
                                if numeric_count > len(non_null_values) * 0.8:
                                    type_issues.append(f"{col} (mixed numeric/text)")
                
                if type_issues:
                    sheet_issues['issues'].append(f"Data type issues: {len(type_issues)} columns")
                    quality_issues['total_issues'] += len(type_issues)
                
                # 6. Potential outliers in numeric columns
                outlier_issues = []
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        non_null_values = df[col].dropna()
                        if len(non_null_values) > 10:
                            Q1 = non_null_values.quantile(0.25)
                            Q3 = non_null_values.quantile(0.75)
                            IQR = Q3 - Q1
                            outliers = non_null_values[(non_null_values < Q1 - 1.5*IQR) | 
                                                     (non_null_values > Q3 + 1.5*IQR)]
                            if len(outliers) > 0:
                                outlier_issues.append(f"{col} ({len(outliers)} outliers)")
                
                if outlier_issues:
                    sheet_issues['issues'].append(f"Potential outliers: {len(outlier_issues)} columns")
                    quality_issues['total_issues'] += len(outlier_issues)
                
                # 7. Column naming issues
                naming_issues = []
                for col in df.columns:
                    col_str = str(col)
                    if col_str.startswith('Unnamed'):
                        naming_issues.append(f"Unnamed column: {col}")
                    elif ' ' in col_str and not col_str.replace(' ', '').replace('_', '').isalnum():
                        naming_issues.append(f"Special characters in column name: {col}")
                
                if naming_issues:
                    sheet_issues['issues'].append(f"Column naming issues: {len(naming_issues)}")
                    quality_issues['total_issues'] += len(naming_issues)
                
                # Store sheet issues
                quality_issues['sheets'].append(sheet_issues)
                
                # Print summary for this sheet
                if sheet_issues['issues']:
                    print(f"  Issues found: {len(sheet_issues['issues'])}")
                    for issue in sheet_issues['issues']:
                        print(f"    - {issue}")
                else:
                    print("  No major quality issues detected")
                
            except Exception as e:
                print(f"  Error analyzing sheet: {e}")
                quality_issues['sheets'].append({
                    'sheet_name': sheet_name,
                    'error': str(e)
                })
        
        return quality_issues
        
    except Exception as e:
        print(f"Error assessing file: {e}")
        return None

def generate_cleaning_recommendations(quality_issues):
    """Generate specific cleaning recommendations based on quality assessment"""
    print(f"\n{'='*80}")
    print("DATA CLEANING RECOMMENDATIONS")
    print(f"{'='*80}")
    
    if not quality_issues:
        return
    
    print(f"Total quality issues found: {quality_issues['total_issues']}")
    
    # Group issues by type
    issue_types = {
        'unnamed_columns': 0,
        'empty_columns': 0,
        'missing_values': 0,
        'duplicates': 0,
        'type_issues': 0,
        'outliers': 0,
        'naming_issues': 0
    }
    
    for sheet in quality_issues['sheets']:
        if 'issues' in sheet:
            for issue in sheet['issues']:
                if 'Unnamed columns' in issue:
                    issue_types['unnamed_columns'] += 1
                elif 'empty columns' in issue:
                    issue_types['empty_columns'] += 1
                elif 'missing values' in issue:
                    issue_types['missing_values'] += 1
                elif 'Duplicate rows' in issue:
                    issue_types['duplicates'] += 1
                elif 'Data type issues' in issue:
                    issue_types['type_issues'] += 1
                elif 'outliers' in issue:
                    issue_types['outliers'] += 1
                elif 'naming issues' in issue:
                    issue_types['naming_issues'] += 1
    
    print(f"\nIssue Summary:")
    for issue_type, count in issue_types.items():
        if count > 0:
            print(f"  {issue_type.replace('_', ' ').title()}: {count} sheets affected")
    
    print(f"\nRecommended Cleaning Steps:")
    print("1. Remove or rename unnamed columns")
    print("2. Delete completely empty columns")
    print("3. Standardize column names (remove spaces, special characters)")
    print("4. Handle missing values (flag or impute)")
    print("5. Remove duplicate rows")
    print("6. Fix data type inconsistencies")
    print("7. Review and flag potential outliers")

def main():
    """Main function to assess data quality"""
    data_folder = "data"
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found!")
        return
    
    print("STREAMWATCH DATA QUALITY ASSESSMENT")
    print("=" * 80)
    
    # Start with the largest file
    largest_file = "30 yr StreamWatch Data Analysis.xlsx"
    file_path = os.path.join(data_folder, largest_file)
    
    if os.path.exists(file_path):
        quality_issues = assess_data_quality(file_path)
        generate_cleaning_recommendations(quality_issues)
    else:
        print(f"File {largest_file} not found!")
    
    print(f"\n{'='*80}")
    print("QUALITY ASSESSMENT COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
