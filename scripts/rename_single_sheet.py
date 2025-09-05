#!/usr/bin/env python3
import pandas as pd
import os

def rename_sheet_columns(sheet_name):
    """Rename columns in a specific sheet"""
    file_path = "data/30 yr StreamWatch Data Analysis.xlsx"
    
    print(f"Processing sheet: {sheet_name}")
    
    # Read the sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Rename unnamed columns
    new_columns = []
    for i, col in enumerate(df.columns):
        if str(col).startswith('Unnamed'):
            new_columns.append(f"column_{i}")
        else:
            new_columns.append(col)
    
    df.columns = new_columns
    
    # Save back
    with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"✅ Renamed columns in {sheet_name}")

# Process one sheet at a time
if __name__ == "__main__":
    # You can change this to process different sheets
    sheet_name = "TURBIDITY"  # Start with smallest sheet
    rename_sheet_columns(sheet_name)
