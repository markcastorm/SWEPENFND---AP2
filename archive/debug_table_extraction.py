"""Debug script to visualize extracted table structure"""
import camelot
import pandas as pd

pdf_path = r"downloads\20251107_104414\AP2_2025_half_year.pdf"
page_num = 6

print("=" * 80)
print("Extracting table from Balance Sheet page...")
print("=" * 80)

# Extract with Camelot
tables = camelot.read_pdf(pdf_path, pages=str(page_num), flavor='lattice')

print(f"\nFound {len(tables)} table(s)\n")

for i, table in enumerate(tables):
    df = table.df
    print(f"\nTable {i+1}:")
    print(f"Shape: {df.shape}")
    print(f"Accuracy: {table.parsing_report['accuracy']}")
    print("\nFirst 30 rows:")
    print(df.head(30).to_string())
    print("\n" + "=" * 80)

# Save to CSV for inspection
df.to_csv("debug_table_output.csv", index=False)
print("\nSaved full table to: debug_table_output.csv")
