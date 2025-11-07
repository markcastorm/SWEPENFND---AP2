"""Analyze sample data to understand expected structure"""
import pandas as pd

# Read sample file
sample_file = r"project information\AP2_SA_SWEPENFND_DATA_20220920.xlsx"
df = pd.read_excel(sample_file, header=1)

print("=" * 80)
print("SAMPLE DATA ANALYSIS")
print("=" * 80)

print(f"\nShape: {df.shape}")
print(f"Years in data: {df['Unnamed: 0'].tolist()}")

print("\n" + "=" * 80)
print("COLUMN MAPPING (what data goes where)")
print("=" * 80)

# Show all columns with sample values
for i, col in enumerate(df.columns):
    if i == 0:
        continue

    # Get first non-null value
    val = df[col].dropna().iloc[0] if not df[col].dropna().empty else "NO DATA"

    # Extract field name from column
    parts = col.split('.')
    field_name = parts[1] if len(parts) > 1 else col

    print(f"\n{i}. {field_name}")
    print(f"   Column: {col}")
    print(f"   Sample value: {val}")

print("\n" + "=" * 80)
print("ACTUAL DATA ROWS")
print("=" * 80)
print(df.to_string())

# Now check our output
print("\n" + "=" * 80)
print("COMPARING WITH OUR OUTPUT")
print("=" * 80)

our_file = r"output\latest\AP2_Financial_Data_latest.xlsx"
our_df = pd.read_excel(our_file)

print(f"\nOur output shape: {our_df.shape}")
print(f"Sample shape: {df.shape}")

print("\nOur data:")
print(our_df.to_string())

# Compare column by column
print("\n" + "=" * 80)
print("FIELD-BY-FIELD COMPARISON (2025 data vs sample structure)")
print("=" * 80)

for i, col in enumerate(df.columns):
    if i == 0:
        continue

    parts = col.split('.')
    field_name = parts[1] if len(parts) > 1 else col

    our_val = our_df[col].iloc[0] if not pd.isna(our_df[col].iloc[0]) else "MISSING"

    print(f"{i}. {field_name}: {our_val}")
