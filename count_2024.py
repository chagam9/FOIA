import pandas as pd
import glob
import os

data_dir = 'data_files'

def count_2024():
    files = glob.glob(os.path.join(data_dir, '*.xlsx'))
    if not files:
        print("No Excel files found.")
        return

    # Assuming first file is the relevant one
    filepath = files[0]
    try:
        df = pd.read_excel(filepath, sheet_name='מעצרים נקי')
        
        # 'תאריך מעצר' might be string or datetime
        date_col = 'תאריך מעצר'
        
        if date_col not in df.columns:
            print(f"Column '{date_col}' not found.")
            return

        # Convert to datetime, handling errors
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Check 'Column1' or similar for quantity
        candidates = [c for c in df.columns if 'Column' in c or 'S' in c or 'Quantity' in c or 'מספר' in c]
        print(f"Candidate quantity columns: {candidates}")
        
        if 'Column1' in df.columns:
            print("\nValues in Column1:")
            print(df['Column1'].value_counts().head())
            
            # Recalculate totals
            total_quantity = df['Column1'].sum()
            print(f"\nTotal Rows: {len(df)}")
            print(f"Total Quantity (Sum of Column1): {total_quantity}")
            
            # Yearly with Quantity
            df['year'] = df[date_col].dt.year
            yearly_sums = df.groupby('year')['Column1'].sum()
            print("\nArrests by Year (Weighted by Column1):")
            print(yearly_sums)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    count_2024()
