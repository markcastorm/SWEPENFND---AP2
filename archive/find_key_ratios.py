"""Find Key Ratios data in PDF"""
import camelot
import fitz

pdf_path = r"downloads\20251107_151315\AP2_2024_half_year.pdf"

print("=" * 80)
print("SEARCHING FOR KEY RATIOS PAGE")
print("=" * 80)

# Search all pages for "Key ratios"
doc = fitz.open(pdf_path)
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text().lower()

    if 'key ratios' in text or 'key ratio' in text:
        print(f"\nPage {page_num + 1}: Found 'Key ratios'")

        # Extract tables from this page
        tables = camelot.read_pdf(pdf_path, pages=str(page_num + 1), flavor='lattice')

        if len(tables) == 0:
            print("  Lattice mode found no tables, trying stream mode...")
            tables = camelot.read_pdf(pdf_path, pages=str(page_num + 1), flavor='stream', edge_tol=50, row_tol=10)

        if len(tables) > 0:
            print(f"  Found {len(tables)} table(s)")

            for i, table in enumerate(tables):
                df = table.df
                print(f"\n  Table {i+1} (shape: {df.shape}):")
                print(df.head(10).to_string())
                print("\n  Full table:")
                print(df.to_string())

doc.close()
