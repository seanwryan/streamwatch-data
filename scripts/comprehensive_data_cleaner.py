#!/usr/bin/env python3
"""
Comprehensive Data Cleaner for StreamWatch Data
This script systematically cleans all Excel files in the data folder.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def clean_column_names(df):
    """Standardize column names across all sheets"""
    new_columns = []
    for col in df.columns:
        # Remove special characters, replace spaces with underscores
        clean_name = str(col).strip()
        clean_name = clean_name.replace(' ', '_').replace('(', '').replace(')', '')
        clean_name = clean_name.replace('[', '').replace(']', '').replace('%', 'pct')
        clean_name = clean_name.replace('°', 'deg').replace('µ', 'u')
        clean_name = clean_name.replace('/', '_per_').replace('-', '_')
        clean_name = clean_name.replace('&', 'and').replace('+', 'plus')
        
        # Handle duplicate names
        if clean_name in new_columns:
            clean_name = f"{clean_name}_2"
        
        new_columns.append(clean_name)
    
    df.columns = new_columns
    return df

def clean_sheet_data(df, sheet_name, verbose=True):
    """Clean a single sheet's data with improved logic"""
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
    
    # 2. Handle unnamed columns more intelligently
    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
    if unnamed_cols:
        for col in unnamed_cols:
            if df[col].isna().all():
                df = df.drop(columns=[col])
                cleaning_log.append(f"Removed empty unnamed column: {col}")
            else:
                # Try to infer column purpose from content
                col_index = df.columns.get_loc(col)
                sample_values = df[col].dropna().head(5).tolist()
                
                # Common patterns for water quality data
                if any('site' in str(val).lower() for val in sample_values):
                    df = df.rename(columns={col: 'Site_ID'})
                elif any('date' in str(val).lower() for val in sample_values):
                    df = df.rename(columns={col: 'Date'})
                elif col_index == 0:
                    df = df.rename(columns={col: 'Site_ID'})
                elif col_index == 1:
                    df = df.rename(columns={col: 'Date'})
                else:
                    df = df.rename(columns={col: f'Column_{col_index}'})
                
                cleaning_log.append(f"Renamed unnamed column {col}")
    
    # 3. Standardize column names
    df = clean_column_names(df)
    cleaning_log.append("Standardized column names")
    
    # 4. Remove duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates()
        cleaning_log.append(f"Removed {duplicates} duplicate rows")
    
    # 5. Fix data type issues for water quality parameters
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
        'TDS': 'float64',
        'E_coli': 'float64',
        'Bacteria': 'float64',
        'Chloride': 'float64',
        'Sulfate': 'float64',
        'Alkalinity': 'float64',
        'Hardness': 'float64'
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
    
    # 6. Handle date columns
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            cleaning_log.append(f"Converted {col} to datetime")
        except:
            pass
    
    # 7. Add data quality flags
    df['data_quality_flag'] = 'clean'
    
    # Flag rows with too many missing values
    missing_threshold = 0.5  # 50% missing
    for idx, row in df.iterrows():
        missing_pct = row.isna().sum() / len(row)
        if missing_pct > missing_threshold:
            df.at[idx, 'data_quality_flag'] = 'high_missing'
    
    # Flag potential outliers in numeric columns
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            non_null_values = df[col].dropna()
            if len(non_null_values) > 10:
                Q1 = non_null_values.quantile(0.25)
                Q3 = non_null_values.quantile(0.75)
                IQR = Q3 - Q1
                outliers = non_null_values[(non_null_values < Q1 - 1.5*IQR) | 
                                         (non_null_values > Q3 + 1.5*IQR)]
                if len(outliers) > 0:
                    df.loc[df[col].isin(outliers), 'data_quality_flag'] = 'potential_outlier'
    
    if verbose:
        print(f"    Final shape: {df.shape}")
        print(f"    Rows removed: {original_shape[0] - df.shape[0]}")
        print(f"    Columns removed: {original_shape[1] - df.shape[1]}")
        if cleaning_log:
            print(f"    Cleaning actions: {len(cleaning_log)}")
    
    return df, cleaning_log

def clean_excel_file(file_path, output_path=None, max_sheets=None, max_rows_per_sheet=5000):
    """Clean an entire Excel file with memory management"""
    print(f"\n{'='*80}")
    print(f"CLEANING FILE: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
    try:
        # Get file size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"File size: {file_size:.2f} MB")
        
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
                
                # Read sheet with row limit for large files
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=max_rows_per_sheet)
                
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
        
        return cleaned_sheets, total_cleaning_log
        
    except Exception as e:
        print(f"Error cleaning file: {e}")
        return None, None

def create_cleaning_summary(all_cleaning_logs, output_path):
    """Create a comprehensive cleaning summary"""
    print(f"\nCreating comprehensive cleaning summary...")
    
    # Count cleaning actions by type
    action_counts = {}
    for log in all_cleaning_logs:
        action = log.split(': ')[1] if ': ' in log else log
        action_counts[action] = action_counts.get(action, 0) + 1
    
    # Create summary DataFrame
    summary_data = []
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        summary_data.append({
            'Cleaning_Action': action,
            'Count': count
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save summary
    summary_path = os.path.join(output_path, 'cleaning_summary.xlsx')
    summary_df.to_excel(summary_path, index=False)
    
    print(f"Cleaning summary saved to: {summary_path}")
    return summary_df

def main():
    """Main function to clean all data files"""
    data_folder = "data"
    output_folder = "cleaned_data"
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found!")
        return
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    print("COMPREHENSIVE STREAMWATCH DATA CLEANING")
    print("=" * 80)
    
    # Get all Excel files
    excel_files = []
    for f in os.listdir(data_folder):
        if f.endswith(('.xlsx', '.xlsm')) and os.path.isfile(os.path.join(data_folder, f)):
            excel_files.append(f)
    
    print(f"Found {len(excel_files)} Excel files to clean")
    
    all_cleaning_logs = []
    cleaned_files = []
    
    # Process each file
    for i, file in enumerate(excel_files, 1):
        print(f"\n{'='*60}")
        print(f"PROCESSING FILE {i}/{len(excel_files)}: {file}")
        print(f"{'='*60}")
        
        file_path = os.path.join(data_folder, file)
        output_path = os.path.join(output_folder, f"cleaned_{file}")
        
        # Determine max sheets based on file size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        if file_size > 5:
            max_sheets = 3  # Limit large files
            max_rows = 3000
        elif file_size > 2:
            max_sheets = 5
            max_rows = 5000
        else:
            max_sheets = None  # Process all sheets
            max_rows = 10000
        
        print(f"File size: {file_size:.2f} MB")
        if max_sheets:
            print(f"Processing first {max_sheets} sheets only")
        
        cleaned_sheets, cleaning_log = clean_excel_file(
            file_path, output_path, max_sheets=max_sheets, max_rows_per_sheet=max_rows
        )
        
        if cleaned_sheets:
            all_cleaning_logs.extend(cleaning_log)
            cleaned_files.append(file)
            print(f"✓ Successfully cleaned {file}")
        else:
            print(f"✗ Failed to clean {file}")
    
    # Create comprehensive summary
    if all_cleaning_logs:
        create_cleaning_summary(all_cleaning_logs, output_folder)
        
        print(f"\n{'='*80}")
        print("COMPREHENSIVE CLEANING COMPLETE")
        print(f"{'='*80}")
        print(f"Successfully cleaned {len(cleaned_files)} files")
        print(f"Total cleaning actions: {len(all_cleaning_logs)}")
        print(f"Cleaned files saved to: {output_folder}/")
        print(f"Cleaning summary saved to: {output_folder}/cleaning_summary.xlsx")
        
        # Show top cleaning actions
        action_counts = {}
        for log in all_cleaning_logs:
            action = log.split(': ')[1] if ': ' in log else log
            action_counts[action] = action_counts.get(action, 0) + 1
        
        print(f"\nTop 10 cleaning actions:")
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {action}: {count} times")
    else:
        print("No files were successfully cleaned!")

if __name__ == "__main__":
    main()
