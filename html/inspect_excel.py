import pandas as pd

filename = "data_files/arrests_initial.xlsx"
sheets_to_inspect = ['סטטוס תיק נקי', 'עילות סגירת תיק נקי']

try:
    for sheet in sheets_to_inspect:
        print(f"\n--- Reading sheet: {sheet} ---")
        try:
            df = pd.read_excel(filename, sheet_name=sheet)
            print("Columns:")
            print(df.columns.tolist())
            print("\nFirst 3 rows:")
            print(df.head(3).to_string())
        except ValueError:
            print(f"Sheet '{sheet}' not found.")
        except Exception as e:
            print(f"Error reading sheet '{sheet}': {e}")

except Exception as e:
    print(f"General error: {e}")
