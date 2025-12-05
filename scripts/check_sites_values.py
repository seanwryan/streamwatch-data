
import pandas as pd

try:
    df = pd.read_excel('data/raw/2025 StreamWatch Locations.xlsx')
    
    status_cols = ['CAT_Status', 'BAT_Status', 'BACT_Status', 'Groundtruthing Status', 'Type']
    
    for col in status_cols:
        if col in df.columns:
            print(f"\nUnique values for {col}:")
            print(df[col].unique())
        else:
            print(f"\nColumn {col} not found")
            
except Exception as e:
    print(f"Error: {e}")
