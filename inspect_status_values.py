import pandas as pd
import glob
import os

data_dir = 'data_files'

def inspect_statuses():
    files = glob.glob(os.path.join(data_dir, '*.xlsx'))
    if not files:
        print("No Excel files found.")
        return

    filepath = files[0]
    try:
        df = pd.read_excel(filepath, sheet_name='סטטוס תיק נקי')
        col_name = 'סטטוס תיק כולל החלטה שיפוטית'
        if col_name in df.columns:
            print(f"Unique values in '{col_name}':")
            print(df[col_name].value_counts())
        else:
            print(f"Column '{col_name}' not found.")
            print("Available columns:", df.columns.tolist())
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_statuses()
