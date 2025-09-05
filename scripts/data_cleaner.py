#!/usr/bin/env python3
"""
Data Cleaner for StreamWatch Data
This script systematically cleans data quality issues in Excel files.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def clean_sheet_data(df, sheet_name, verbose=True):
    """Clean a single sheet's data"""
    if verbose:
        print(f"  Cleaning sheet: {sheet_name}")
        print(f"    Original shape: {df.shape}")
    
    original_shape = df.shape
    cleaning_log = []
    
    # 1. Remove completely empty columns
    empty_cols = [col for col in df.columns if df[col].isna().all()]
    if empty_cols:
        df = df.drop(columns=empty_cols)
        cleaning_log.append(f"Removed {len(empty_cols)} empty columns")
    
    # 2. Handle unnamed columns
    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
    if unnamed_cols:
        # Try to infer column names from context or remove if truly empty
        for col in unnamed_cols:
            if df[col].isna().all():
                df = df.drop(columns=[col])
                cleaning_log.append(f"Removed empty unnamed column: {col}")
            else:
                # Try to rename based on position or content
                col_index = df.columns.get_loc(col)
                if col_index == 0:
                    df = df.rename(columns={col: 'Site_ID'})
                elif col_index == 1:
                    df = df.rename(columns={col: 'Date'})
                else:
                    df = df.rename(columns={col: f'Column_{col_index}'})
                cleaning_log.append(f"Renamed unnamed column {col} to {df.columns[col_index]}")
    
    # 3. Standardize column names
    new_columns = []
    for col in df.columns:
        # Remove special characters, replace spaces with underscores
        clean_name = str(col).strip()
        clean_name = clean_name.replace(' ', '_').replace('(', '').replace(')', '')
        clean_name = clean_name.replace('[', '').replace(']', '').replace('%', 'pct')
        clean_name = clean_name.replace('°', 'deg').replace('µ', 'u')
        clean_name = clean_name.replace('/', '_per_').replace('-', '_')
        
        # Handle duplicate names
        if clean_name in new_columns:
            clean_name = f"{clean_name}_2"
        
        new_columns.append(clean_name)
    
    df.columns = new_columns
    if len(new_columns) != len(set(new_columns)):
        cleaning_log.append("Standardized column names")
    
    # 4. Remove duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates()
        cleaning_log.append(f"Removed {duplicates} duplicate rows")
    
    # 5. Fix data type issues for common water quality parameters
    water_quality_params = {
        'pH': 'float64',
        'DO': 'float64',
        'Dissolved_Oxygen': 'float64',
        'Temperature': 'float64',
        'Temp': 'float64',
        'Turbidity': 'float64',
        'Nitrate': 'float64',
        'Phosphate': 'float64',
        'Conductivity': 'float64',
        'TDS': 'float64'
    }
    
    for col in df.columns:
        for param, dtype in water_quality_params.items():
            if param.lower() in col.lower():
                try:
                    # Convert to numeric, coercing errors to NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    cleaning_log.append(f"Converted {col} to numeric")
                except:
                    pass
                break
    
    # 6. Handle missing values - flag them but don't remove
    missing_before = df.isna().sum().sum()
    
    # For water quality data, missing values are meaningful - flag them
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            # Create a flag column for missing values
            flag_col = f"{col}_missing_flag"
            if flag_col not in df.columns:
                df[flag_col] = df[col].isna()
    
    # 7. Add data quality flags
    df['data_quality_flag'] = 'clean'
    
    # Flag rows with too many missing values
    missing_threshold = 0.5  # 50% missing
    for idx, row in df.iterrows():
        missing_pct = row.isna().sum() / len(row)
        if missing_pct > missing_threshold:
            df.at[idx, 'data_quality_flag'] = 'high_missing'
    
    if verbose:
        print(f"    Final shape: {df.shape}")
        print(f"    Rows removed: {original_shape[0] - df.shape[0]}")
        print(f"    Columns removed: {original_shape[1] - df.shape[1]}")
        if cleaning_log:
            print(f"    Cleaning actions: {len(cleaning_log)}")
    
    return df, cleaning_log

def clean_excel_file(file_path, output_path=None, max_sheets=None):
    """Clean an entire Excel file"""
    print(f"\n{'='*80}")
    print(f"CLEANING FILE: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        print(f"Number of sheets: {len(excel_file.sheet_names)}")
        
        # Limit sheets for large files
        sheets_to_process = excel_file.sheet_names
        if max_sheets:
            sheets_to_process = sheets_to_process[:max_sheets]
            print(f"Processing first {max_sheets} sheets only")
        
        cleaned_sheets = {}
        total_cleaning_log = []
        
        for sheet_name in sheets_to_process:
            try:
                print(f"\n--- Processing Sheet: {sheet_name} ---")
                
                # Read sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Clean the sheet
                cleaned_df, cleaning_log = clean_sheet_data(df, sheet_name)
                
                # Store cleaned sheet
                cleaned_sheets[sheet_name] = cleaned_df
                total_cleaning_log.extend([f"{sheet_name}: {log}" for log in cleaning_log])
                
            except Exception as e:
                print(f"  Error processing sheet {sheet_name}: {e}")
                continue
        
        # Save cleaned data
        if output_path:
            print(f"\nSaving cleaned data to: {output_path}")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save to Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df in cleaned_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"Cleaned data saved successfully!")
        
        # Print summary
        print(f"\n{'='*60}")
        print("CLEANING SUMMARY")
        print(f"{'='*60}")
        print(f"Total sheets processed: {len(cleaned_sheets)}")
        print(f"Total cleaning actions: {len(total_cleaning_log)}")
        
        if total_cleaning_log:
            print(f"\nTop cleaning actions:")
            action_counts = {}
            for log in total_cleaning_log:
                action = log.split(': ')[1] if ': ' in log else log
                action_counts[action] = action_counts.get(action, 0) + 1
            
            for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {action}: {count} times")
        
        return cleaned_sheets, total_cleaning_log
        
    except Exception as e:
        print(f"Error cleaning file: {e}")
        return None, None

def create_data_quality_report(cleaned_sheets, output_path):
    """Create a data quality report"""
    print(f"\nCreating data quality report...")
    
    report_data = []
    
    for sheet_name, df in cleaned_sheets.items():
        report_data.append({
            'Sheet': sheet_name,
            'Rows': df.shape[0],
            'Columns': df.shape[1],
            'Missing_Values': df.isna().sum().sum(),
            'Missing_Percentage': (df.isna().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
            'Clean_Flag_Count': (df['data_quality_flag'] == 'clean').sum() if 'data_quality_flag' in df.columns else 0,
            'High_Missing_Flag_Count': (df['data_quality_flag'] == 'high_missing').sum() if 'data_quality_flag' in df.columns else 0
        })
    
    report_df = pd.DataFrame(report_data)
    
    # Save report
    report_path = output_path.replace('.xlsx', '_quality_report.xlsx')
    report_df.to_excel(report_path, index=False)
    
    print(f"Data quality report saved to: {report_path}")
    return report_df

def main():
    """Main function to clean data"""
    data_folder = "data"
    output_folder = "cleaned_data"
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found!")
        return
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    print("STREAMWATCH DATA CLEANING")
    print("=" * 80)
    
    # Start with the largest file - process only first 5 sheets to avoid memory issues
    largest_file = "30 yr StreamWatch Data Analysis.xlsx"
    file_path = os.path.join(data_folder, largest_file)
    output_path = os.path.join(output_folder, f"cleaned_{largest_file}")
    
    if os.path.exists(file_path):
        print(f"Processing {largest_file} (first 5 sheets only for safety)")
        cleaned_sheets, cleaning_log = clean_excel_file(file_path, output_path, max_sheets=5)
        
        if cleaned_sheets:
            # Create quality report
            create_data_quality_report(cleaned_sheets, output_path)
            
            print(f"\n{'='*80}")
            print("CLEANING COMPLETE")
            print(f"{'='*80}")
            print(f"Cleaned data saved to: {output_path}")
            print(f"Quality report saved to: {output_path.replace('.xlsx', '_quality_report.xlsx')}")
        else:
            print("Cleaning failed!")
    else:
        print(f"File {largest_file} not found!")

if __name__ == "__main__":
    main()
