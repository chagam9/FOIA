
import pandas as pd
import glob
import os

def inspect_missing_data():
    files = glob.glob(os.path.join('data_files', 'arrests*.xlsx'))
    if not files: return
    
    df = pd.read_excel(files[0], sheet_name=0)
    
    # 1. Check Missing Ages
    missing_age = df['גיל'].isna().sum()
    total_rows = len(df)
    print(f"Total Rows: {total_rows}")
    print(f"Rows with missing Age: {missing_age}")
    
    # 2. Check Specific Cities
    print("\n--- Specific City Analysis ---")
    for city in ['תל אביב', 'ירושלים']:
        rows = df[df['ישוב עבירה מחושב'].astype(str).str.contains(city, na=False)]
        print(f"City: {city}, Total Rows: {len(rows)}")
        print(f"Missing Age: {rows['גיל'].isna().sum()}")

if __name__ == "__main__":
    inspect_missing_data()
