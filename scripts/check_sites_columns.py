
import pandas as pd

try:
    df = pd.read_excel('data/raw/2025 StreamWatch Locations.xlsx')
    print("Columns found:")
    for col in df.columns:
        print(f" - {col}")
    print(f"\nTotal rows: {len(df)}")
except Exception as e:
    print(f"Error: {e}")
