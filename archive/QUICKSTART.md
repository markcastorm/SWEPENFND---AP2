# AP2 Scraper - Quick Start Guide

Get started with the AP2 Financial Reports Scraper in 3 easy steps!

## Step 1: Install Dependencies

```bash
cd "C:\Users\casto\Documents\SWEPENFND – AP2"
pip install -r requirements.txt
```

## Step 2: Configure (Optional)

Open [config.py](config.py) and set your preferences:

```python
# Scrape latest year (default)
TARGET_YEAR = "latest"

# OR scrape specific year
TARGET_YEAR = 2024
```

## Step 3: Run the Scraper

```bash
python ap2_scraper.py
```

## What It Does

1. Opens Chrome browser automatically
2. Navigates to AP2 financial reports page
3. Downloads PDF reports for your target year
4. Extracts financial tables from PDFs
5. Saves structured data to Excel/CSV

## Where to Find Results

- **Latest data**: `output/latest/AP2_Financial_Data_latest.xlsx`
- **Timestamped data**: `output/YYYYMMDD_HHMMSS/`
- **Downloaded PDFs**: `downloads/YYYYMMDD_HHMMSS/`
- **Logs**: `logs/YYYYMMDD_HHMMSS/`

## Example Output

The Excel file will contain all 21 columns matching your sample data:

| Unnamed: 0 | AP2.FUNDCAPITALCARRIEDFORWARD... | AP2.NETOUTFLOWS... | ... |
|------------|----------------------------------|---------------------|-----|
| 2024       | 123456                           | 7890                | ... |
| 2025       | 234567                           | 8901                | ... |

## Common Tasks

### Scrape 2024 Reports Only
```python
# In config.py
TARGET_YEAR = 2024
```

### Scrape Multiple Years
```python
# In config.py
TARGET_YEAR = None
YEARS_TO_SCRAPE = [2024, 2023, 2022]
```

### Only Download Annual Reports
```python
# In config.py
REPORT_TYPES = {
    'annual': True,
    'half_year': False,
}
```

### Change Output Format
```python
# In config.py
OUTPUT_CONFIG = {
    'output_format': 'both',  # Saves both Excel and CSV
}
```

## Troubleshooting

### Issue: Chrome driver error
**Solution**: Update undetected-chromedriver
```bash
pip install --upgrade undetected-chromedriver
```

### Issue: No data extracted
**Solution**: Check the logs in `logs/` folder for details

### Issue: Import errors
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## Need More Help?

See the full [README.md](README.md) for detailed documentation.

---

Happy scraping!
