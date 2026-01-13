
import pandas as pd
import glob
import os

def inspect_cities():
    files = glob.glob(os.path.join('data_files', 'arrests*.xlsx'))
    if not files:
        print("No files found.")
        return

    filepath = files[0]
    print(f"Reading {filepath}")
    
    try:
        df = pd.read_excel(filepath, sheet_name=0)
        col_name = 'ישוב עבירה מחושב'
        
        if col_name not in df.columns:
            print(f"Column {col_name} not found. Available: {df.columns.tolist()}")
            return
            
        counts = df[col_name].value_counts()
        print("\nTop 50 Cities:")
        print(counts.head(50))
        
        print("\n--- Specific Checks ---")
        param_cities = ['ירושלים', 'תל אביב', 'חיפה', 'באר שבע', 'פתח תקווה']
        for p in param_cities:
            # Find close matches
            matches = [c for c in df[col_name].unique() if str(c) != 'nan' and p in str(c)]
            print(f"Matches for {p}: {matches}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_cities()
