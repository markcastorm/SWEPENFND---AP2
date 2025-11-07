
import pandas as pd
import numpy as np

# --- CONFIGURATION ---
# Paths to the Excel files
GENERATED_FILE = r'output\latest\AP2_Financial_Data_latest.xlsx'
MANUAL_FILE = r'project information\AP2_SA_SWEPENFND_DATA_20220920.xlsx'

# Year to compare
YEAR_TO_COMPARE = 2024

# --- SCRIPT ---

print("=" * 80)
print("Comparing Generated Data vs. Manual Data")
print(f"Year: {YEAR_TO_COMPARE}")
print("=" * 80)

def read_generated_file(path):
    """Reads the generated Excel file which has two header rows."""
    try:
        df = pd.read_excel(path, header=None) # Read without headers
        # The actual data starts from the 3rd row (index 2)
        # The first header row (index 0) contains the technical names
        # The second header row (index 1) contains the human-readable names
        
        # Use the first header row (index 0) for column names for the data
        df_data = df.iloc[2:].copy() # Get data rows, make a copy to avoid SettingWithCopyWarning
        df_data.columns = df.iloc[0] # Assign the first header row as column names
        
        # Rename the first column (which is the year) for consistent access
        # The first column in df.iloc[0] is None, so we need to handle that
        df_data = df_data.rename(columns={df_data.columns[0]: 'Year'})
        
        # Reset index to make 'Year' a regular column if it became the index
        if 'Year' in df_data.index.names:
            df_data = df_data.reset_index()

        return df_data
    except FileNotFoundError:
        print(f"ERROR: Generated file not found at {path}")
        return None

def read_manual_file(path):
    """Reads the manual data file."""
    try:
        df = pd.read_excel(path, sheet_name='Sheet2')
        # Assuming the first column of the manual file is also the year
        df = df.rename(columns={df.columns[0]: 'Year'})
        return df
    except FileNotFoundError:
        print(f"ERROR: Manual file not found at {path}")
        return None
    except ValueError as e:
        if "Worksheet named 'Sheet2' not found" in str(e):
            print(f"ERROR: The manual file must have a sheet named 'Sheet2'.")
            return None
        raise e

def main():
    # Read both files
    df_gen = read_generated_file(GENERATED_FILE)
    df_manual = read_manual_file(MANUAL_FILE)

    if df_gen is None or df_manual is None:
        return

    # --- Data Preparation ---
    # Get the row for the target year from both dataframes
    # In generated file, year is in the first column 'Unnamed: 0'
    gen_row = df_gen[df_gen['Year'] == YEAR_TO_COMPARE]
    
    # In manual file, year is in the first column, which might be named differently (e.g., 'Year')
    manual_year_col = df_manual.columns[0]
    manual_row = df_manual[df_manual[manual_year_col] == YEAR_TO_COMPARE]

    if gen_row.empty:
        print(f"ERROR: Year {YEAR_TO_COMPARE} not found in the generated file.")
        return

    if manual_row.empty:
        print(f"ERROR: Year {YEAR_TO_COMPARE} not found in the manual sample file.")
        return

    # Convert rows to simple lists of values, ignoring the first column (year)
    gen_values = gen_row.iloc[0, 1:].tolist()
    manual_values = manual_row.iloc[0, 1:].tolist()

    # Align column count if they differ
    min_cols = min(len(gen_values), len(manual_values))
    if len(gen_values) != len(manual_values):
        print(f"WARNING: Column count mismatch. Generated: {len(gen_values)}, Manual: {len(manual_values)}. Comparing first {min_cols} columns.")
        gen_values = gen_values[:min_cols]
        manual_values = manual_values[:min_cols]

    # --- Comparison ---
    discrepancies = []
    for i in range(min_cols):
        gen_val = gen_values[i]
        manual_val = manual_values[i]

        # Standardize NaN/None values for comparison
        is_gen_nan = pd.isna(gen_val) or gen_val in ['', '-']
        is_manual_nan = pd.isna(manual_val) or manual_val in ['', '-']

        if is_gen_nan and is_manual_nan:
            continue # Both are empty, so they match

        # Clean and convert numbers for a robust comparison
        try:
            # Convert to numeric, coercing errors to NaN
            gen_num = pd.to_numeric(gen_val, errors='coerce')
            manual_num = pd.to_numeric(manual_val, errors='coerce')

            # If both are numbers, compare them with a tolerance for floating point issues
            if not np.isnan(gen_num) and not np.isnan(manual_num):
                if not np.isclose(gen_num, manual_num):
                    discrepancies.append((i + 1, gen_val, manual_val))
            # If one is a number and the other isn't, it's a discrepancy
            elif is_gen_nan != is_manual_nan:
                 discrepancies.append((i + 1, gen_val, manual_val))

        except (ValueError, TypeError):
             # Fallback to string comparison if conversion fails
            if str(gen_val).strip() != str(manual_val).strip():
                discrepancies.append((i + 1, gen_val, manual_val))

    # --- Report Results ---
    print("\n" + "-" * 80)
    if not discrepancies:
        print(f"[SUCCESS] 100% ACCURACY CONFIRMED!")
        print(f"All {min_cols} data points for the year {YEAR_TO_COMPARE} match the manual sample.")
    else:
        print(f"[FAILURE] Found {len(discrepancies)} discrepancies for the year {YEAR_TO_COMPARE}.")
        print("\n{:<10} {:<30} {:<30}".format('Column', 'Generated Value', 'Manual Value'))
        print("-" * 70)
        for col, gen, man in discrepancies:
            print("{:<10} {:<30} {:<30}".format(col, str(gen), str(man)))
    print("-" * 80)

if __name__ == "__main__":
    main()
