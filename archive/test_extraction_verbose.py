"""Test extraction with verbose logging for each row"""
import camelot
import pandas as pd
import re

def clean_number_string(value_str):
    """Clean and convert Swedish formatted numbers"""
    if pd.isna(value_str) or value_str is None:
        return None
    value_str = str(value_str).strip()
    if not value_str or value_str == '' or value_str == '-':
        return None
    cleaned = value_str.replace(' ', '').replace(',', '').replace('\xa0', '')
    if cleaned.startswith('-'):
        try:
            return -int(cleaned[1:])
        except (ValueError, IndexError):
            return None
    try:
        return int(cleaned)
    except ValueError:
        return None

pdf_path = r"downloads\20251107_104414\AP2_2025_half_year.pdf"
page_num = 6

# Extract with Camelot
tables = camelot.read_pdf(pdf_path, pages=str(page_num), flavor='lattice')
df = tables[1].df  # Table 2 (balance sheet)

print("=" * 80)
print("VERBOSE EXTRACTION TEST")
print("=" * 80)

field_patterns = {
    'EQUITIESANDPARTICIPATIONSUNLISTED': [r'^\s*unlisted\s*$'],
    'EQUITIESANDPARTICIPATIONSLISTED': [r'^\s*listed\s*$'],
    'OTHERASSETS': [r'^\s*other assets\s*$'],
    'OTHERLIABILITIES': [r'^\s*other liabilities\s*$'],
    'TOTALLIABILITIES': [r'^\s*total liabilities\s*$'],
    'FUNDCAPITALCARRIEDFORWARD': [r'fund capital carried forward'],
    'TOTALFUNDCAPITALANDLIABILITIES': [r'total fund capital and liabilities']
}

data = {}
in_assets_section = True

for idx, row in df.iterrows():
    field_name = str(row.iloc[0]).strip().lower() if not pd.isna(row.iloc[0]) else ""

    if not field_name:
        continue

    # Track sections
    if 'assets' in field_name and 'total' not in field_name:
        in_assets_section = True
        print(f"\n>>> Entering ASSETS section at row {idx}")
        continue
    elif 'liabilities' in field_name or 'fund capital and liabilities' in field_name:
        in_assets_section = False
        print(f"\n>>> Entering LIABILITIES section at row {idx}")
        continue
    elif 'fund capital' in field_name and 'total' not in field_name:
        in_assets_section = False
        print(f"\n>>> Entering FUND CAPITAL section at row {idx}")
        continue

    print(f"\nRow {idx}: '{field_name}' (section: {'Assets' if in_assets_section else 'Liabilities/Fund'})")

    # Try to match
    for field_key, patterns in field_patterns.items():
        if field_key in data:
            continue

        for pattern in patterns:
            if re.search(pattern, field_name, re.IGNORECASE):
                value = clean_number_string(row.iloc[1])
                print(f"  -> MATCHED {field_key}: {value:,} (pattern: {pattern})")

                if value is not None:
                    data[field_key] = value
                break

print("\n" + "=" * 80)
print(f"FINAL RESULT: Extracted {len(data)} fields")
for key, val in data.items():
    print(f"  {key}: {val:,}")
print("=" * 80)
