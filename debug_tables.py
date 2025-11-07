"""Debug script to see what tables are extracted from PDF"""

import pdfplumber
import glob
import os

# Find latest PDF
pdf_folders = glob.glob('downloads/*')
if pdf_folders:
    latest_folder = max(pdf_folders, key=os.path.getmtime)
    pdf_files = glob.glob(os.path.join(latest_folder, '*.pdf'))

    if pdf_files:
        pdf_file = pdf_files[0]
        print(f"Analyzing: {pdf_file}\n")

        with pdfplumber.open(pdf_file) as pdf:
            print(f"Total pages: {len(pdf.pages)}\n")

            for page_num, page in enumerate(pdf.pages[:10], 1):  # First 10 pages
                tables = page.extract_tables()

                if tables:
                    print(f"=" * 80)
                    print(f"PAGE {page_num} - Found {len(tables)} table(s)")
                    print(f"=" * 80)

                    for i, table in enumerate(tables, 1):
                        if table and len(table) > 0:
                            print(f"\nTable {i}:")
                            print(f"Rows: {len(table)}, Columns: {len(table[0]) if table[0] else 0}")

                            # Print first few rows
                            for row_idx, row in enumerate(table[:5]):
                                print(f"  Row {row_idx}: {row}")

                            if len(table) > 5:
                                print(f"  ... ({len(table) - 5} more rows)")

                    print()
