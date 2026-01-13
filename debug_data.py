import pandas as pd

filename = "data_files/arrests_initial.xlsx"

def inspect_uniques(sheet_name, col_name):
    try:
        df = pd.read_excel(filename, sheet_name=sheet_name)
        if col_name in df.columns:
            print(f"\n--- Unique values in '{sheet_name}' -> '{col_name}' ---")
            # Get value counts to see frequency of potential "bad" data
            print(df[col_name].value_counts(dropna=False).to_string())
        else:
            print(f"Column '{col_name}' not found in '{sheet_name}'")
    except Exception as e:
        print(f"Error reading '{sheet_name}': {e}")

inspect_uniques('סטטוס תיק נקי', 'סטטוס תיק כולל החלטה שיפוטית')
inspect_uniques('עילות סגירת תיק נקי', 'תאור סיבת סגירת תיק')
