"""
AP2 PDF Parser
Processes downloaded PDFs and extracts financial data to Excel
"""

import os
import glob
import pandas as pd
import pdfplumber
from datetime import datetime
import re

import config

print("=" * 80)
print("AP2 PDF Parser")
print("=" * 80)


def find_latest_download_folder():
    """Find the most recent download folder"""
    download_folders = glob.glob('downloads/*')
    if not download_folders:
        print("ERROR: No download folders found")
        return None

    latest_folder = max(download_folders, key=os.path.getmtime)
    print(f"Processing folder: {latest_folder}")
    return latest_folder


def extract_value(text):
    """Extract numeric value from text"""
    if not text or not isinstance(text, str):
        return None

    # Remove spaces and handle negative numbers
    cleaned = text.strip().replace(' ', '').replace('\xa0', '')

    # Check if negative
    is_negative = cleaned.startswith('-')
    if is_negative:
        cleaned = cleaned[1:]

    # Remove non-numeric except decimal point
    cleaned = re.sub(r'[^\d.]', '', cleaned)

    if not cleaned:
        return None

    try:
        value = float(cleaned)
        return -value if is_negative else value
    except:
        return None


def parse_balance_sheet_from_text(pdf_path, year):
    """Extract balance sheet data from PDF text"""
    print(f"\nExtracting from: {os.path.basename(pdf_path)}")

    data = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Search for balance sheet page (usually page 6 or 7)
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()

                if not text:
                    continue

                # Check if this is the balance sheet page
                if 'Balance sheet' in text or 'BALANCE SHEET' in text or 'TOTAL ASSETS' in text:
                    print(f"  Found balance sheet on page {page_num}")

                    lines = text.split('\n')

                    # Extract data by searching for key patterns
                    for i, line in enumerate(lines):
                        line_lower = line.lower()

                        # Look for the value in current or next line
                        current_values = re.findall(r'-?\d[\d\s,]*', line)
                        next_values = re.findall(r'-?\d[\d\s,]*', lines[i+1]) if i+1 < len(lines) else []

                        # Try to extract numeric values
                        all_values = current_values + next_values

                        # Listed equities
                        if 'listed' in line_lower and 'unlisted' not in line_lower:
                            if 'EQUITIESANDPARTICIPATIONSLISTED' not in data:  # Only take first occurrence
                                for val in all_values:
                                    extracted = extract_value(val)
                                    if extracted and extracted > 100000:  # Should be large number
                                        data['EQUITIESANDPARTICIPATIONSLISTED'] = extracted
                                        print(f"    - Listed equities: {extracted:,.0f}")
                                        break

                        # Unlisted equities
                        elif 'unlisted' in line_lower:
                            if 'EQUITIESANDPARTICIPATIONSUNLISTED' not in data:
                                for val in all_values:
                                    extracted = extract_value(val)
                                    if extracted and extracted > 100000:
                                        data['EQUITIESANDPARTICIPATIONSUNLISTED'] = extracted
                                        print(f"    - Unlisted equities: {extracted:,.0f}")
                                        break

                        # Bonds
                        elif 'bonds' in line_lower or 'fixed-income' in line_lower or 'fixed income' in line_lower:
                            if 'BONDSANDOTHERFIXEDINCOMESECURITIES' not in data:
                                for val in all_values:
                                    extracted = extract_value(val)
                                    if extracted and extracted > 100000:
                                        data['BONDSANDOTHERFIXEDINCOMESECURITIES'] = extracted
                                        print(f"    - Bonds: {extracted:,.0f}")
                                        break

                        # Derivative instruments (assets)
                        elif 'derivative instrument' in line_lower and 'DERIVATIVEINSTRUMENTS' not in data and 'liabilities' not in line_lower.lower() and 'Assets' in text[max(0, text.index(line)-200):text.index(line)+50]:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted and extracted > 0:
                                    data['DERIVATIVEINSTRUMENTS'] = extracted
                                    print(f"    - Derivative instruments (assets): {extracted:,.0f}")
                                    break

                        # Cash and bank balances
                        elif 'cash' in line_lower and 'bank' in line_lower and 'CASHANDBANKBALANCES' not in data:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted and extracted > 0:
                                    data['CASHANDBANKBALANCES'] = extracted
                                    print(f"    - Cash and bank balances: {extracted:,.0f}")
                                    break

                        # Total assets
                        elif ('total assets' in line_lower or 'total  assets' in line_lower) and 'TOTALASSETS' not in data:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted and extracted > 400000:  # Should be very large
                                    data['TOTALASSETS'] = extracted
                                    print(f"    - Total assets: {extracted:,.0f}")
                                    break

                        # Derivative instruments (liabilities)
                        elif 'derivative instrument' in line_lower and 'DERIVATIVEINSTRUMENTSLIABILITIES' not in data and ('Liabilities' in text[max(0, text.index(line)-200):text.index(line)+50] or 'liabilities' in line_lower):
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted and extracted > 0:
                                    data['DERIVATIVEINSTRUMENTSLIABILITIES'] = extracted
                                    print(f"    - Derivative instruments (liabilities): {extracted:,.0f}")
                                    break

                        # Total liabilities
                        elif 'total liabilities' in line_lower and 'TOTALLIABILITIES' not in data:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted and extracted > 1000:
                                    data['TOTALLIABILITIES'] = extracted
                                    print(f"    - Total liabilities: {extracted:,.0f}")
                                    break

                        # Fund capital carried forward
                        elif 'fund capital carried forward' in line_lower and 'FUNDCAPITALCARRIEDFORWARD' not in data:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted and extracted > 400000:
                                    data['FUNDCAPITALCARRIEDFORWARD'] = extracted
                                    print(f"    - Fund capital carried forward: {extracted:,.0f}")
                                    break

                        # Net payments to national pension system
                        elif 'net payment' in line_lower and 'pension' in line_lower and 'NETPAYMENTSTOTHENATIONALPENSIONSYSTEM' not in data:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted:  # Can be negative
                                    data['NETPAYMENTSTOTHENATIONALPENSIONSYSTEM'] = extracted
                                    print(f"    - Net payments to pension system: {extracted:,.0f}")
                                    break

                        # Net result for the period
                        elif 'net result for the period' in line_lower and 'NETRESULTFORTHEPERIOD' not in data:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted:  # Can be negative
                                    data['NETRESULTFORTHEPERIOD'] = extracted
                                    print(f"    - Net result for period: {extracted:,.0f}")
                                    break

                        # Total fund capital
                        elif 'total fund capital' in line_lower and 'liabilities' not in line_lower and 'TOTALFUNDCAPITAL' not in data:
                            for val in all_values:
                                extracted = extract_value(val)
                                if extracted and extracted > 400000:
                                    data['TOTALFUNDCAPITAL'] = extracted
                                    print(f"    - Total fund capital: {extracted:,.0f}")
                                    break

                    break  # Found balance sheet, stop searching

    except Exception as e:
        print(f"  ERROR: {e}")

    return data


def create_output(all_data):
    """Create Excel output"""
    print(f"\n{'='*80}")
    print("CREATING OUTPUT")
    print(f"{'='*80}")

    # Create DataFrame with exact headers
    df_data = []

    for year, data in all_data.items():
        row = {'Unnamed: 0': year}

        # Map extracted data to headers
        for header in config.OUTPUT_HEADERS[1:]:  # Skip first column (year)
            value = None
            for field_key, field_value in data.items():
                if field_key in header:
                    value = field_value
                    break
            row[header] = value

        df_data.append(row)

    df = pd.DataFrame(df_data, columns=config.OUTPUT_HEADERS)

    # Create output folders
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_folder = os.path.join('output', timestamp)
    latest_folder = os.path.join('output', 'latest')

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(latest_folder, exist_ok=True)

    # Save files
    output_file = os.path.join(output_folder, f'AP2_Financial_Data_{timestamp}.xlsx')
    latest_file = os.path.join(latest_folder, 'AP2_Financial_Data_latest.xlsx')

    df.to_excel(output_file, index=False)
    df.to_excel(latest_file, index=False)

    print(f"OK Saved: {output_file}")
    print(f"OK Saved: {latest_file}")

    # Print summary
    filled_count = df.notna().sum().sum() - len(df)  # Subtract year column
    total_cells = len(df) * (len(config.OUTPUT_HEADERS) - 1)
    print(f"OK Filled {filled_count}/{total_cells} data cells ({filled_count/total_cells*100:.1f}%)")

    return output_file


def main():
    """Main execution"""
    try:
        # Find latest download folder
        download_folder = find_latest_download_folder()
        if not download_folder:
            return

        # Find all PDFs in folder
        pdf_files = glob.glob(os.path.join(download_folder, '*.pdf'))
        print(f"Found {len(pdf_files)} PDF files\n")

        if not pdf_files:
            print("ERROR: No PDF files found")
            return

        # Process each PDF
        all_data = {}

        for pdf_file in pdf_files:
            # Extract year from filename (AP2_YYYY_type.pdf)
            basename = os.path.basename(pdf_file)
            try:
                year = int(basename.split('_')[1])
            except:
                print(f"WARNING: Could not extract year from {basename}")
                continue

            # Extract data from PDF text
            data = parse_balance_sheet_from_text(pdf_file, year)

            if data:
                all_data[year] = data
                print(f"  OK Extracted {len(data)} fields")
            else:
                print(f"  WARNING: No data extracted")

        if not all_data:
            print("\nWARNING: No financial data extracted")
            return

        # Create output
        output_file = create_output(all_data)

        print(f"\n{'='*80}")
        print("PARSER COMPLETED")
        print(f"{'='*80}")
        print(f"OK Processed {len(pdf_files)} PDFs")
        print(f"OK Extracted data for {len(all_data)} years")
        print(f"OK Output: {output_file}")
        print(f"{'='*80}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
