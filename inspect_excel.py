import pandas as pd
import os
import glob

# Configuration
data_dir = 'data_files'

def inspect_all_sheets():
    # Load Excel file (assuming first one found)
    files = glob.glob(os.path.join(data_dir, '*.xlsx'))
    if not files:
        print("No Excel files found.")
        return

    filepath = files[0]
    print(f"Inspecting file: {filepath}")

    xls = pd.ExcelFile(filepath)
    print(f"Sheet names: {xls.sheet_names}")

    for sheet_name in xls.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name, nrows=5)
            print("Columns:")
            for col in df.columns:
                print(f"  - {col}")
        except ValueError:
            print(f"Sheet '{sheet_name}' not found.")
        except Exception as e:
            print(f"Error reading sheet: {e}")

if __name__ == "__main__":
    inspect_all_sheets()
