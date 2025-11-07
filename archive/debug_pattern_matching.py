"""Debug pattern matching for missing fields"""
import camelot
import pandas as pd
import re

pdf_path = r"downloads\20251107_104414\AP2_2025_half_year.pdf"
page_num = 6

# Extract with Camelot
tables = camelot.read_pdf(pdf_path, pages=str(page_num), flavor='lattice')
df = tables[1].df  # Table 2 (balance sheet)

print("=" * 80)
print("DEBUGGING PATTERN MATCHING")
print("=" * 80)

# Fields we're looking for
missing_fields = {
    'OTHER ASSETS': [r'^\s*other assets\s*$', r'other assets(?!\w)'],
    'OTHER LIABILITIES': [r'^\s*other liabilities\s*$', r'other liabilities(?!\w)'],
    'TOTAL LIABILITIES': [r'^\s*total liabilities\s*$', r'total liabilities(?!\w)'],
    'FUND CAPITAL CARRIED FORWARD': [r'fund capital carried forward', r'carried.*forward'],
    'TOTAL FUND CAPITAL AND LIABILITIES': [r'total fund capital and liabilities', r'total.*capital.*liabilities']
}

print("\nAll rows in balance sheet table:\n")
for idx, row in df.iterrows():
    field_name = str(row.iloc[0]).strip()
    value = str(row.iloc[1]).strip()

    print(f"Row {idx:2d}: '{field_name}' = '{value}'")

    # Check against missing fields
    for field_key, patterns in missing_fields.items():
        for pattern in patterns:
            if re.search(pattern, field_name, re.IGNORECASE):
                print(f"        [MATCH] {field_key} with pattern: {pattern}")

print("\n" + "=" * 80)
