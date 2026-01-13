
import pandas as pd
import glob
import os

def inspect_offenses():
    files = glob.glob(os.path.join('data_files', 'arrests*.xlsx'))
    if not files: return
    
    df = pd.read_excel(files[0], sheet_name=0)
    col_name = 'עבירה'
    
    if col_name in df.columns:
        print("Unique Offenses:")
        for offense in df[col_name].unique():
            print(f"- {offense}")
            
    # Also check law description for backup
    col_law = 'תאור סמל חוק'
    if col_law in df.columns:
        print("\nUnique Law Descriptions:")
        for law in df[col_law].unique():
            print(f"- {law}")

if __name__ == "__main__":
    inspect_offenses()
