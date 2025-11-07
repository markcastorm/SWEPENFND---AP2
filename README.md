# AP2 Financial Reports Scraper

Automated scraper for downloading and parsing financial reports from AP2 (Andra AP-fonden) Swedish pension fund.

## Features

- **Automated Download**: Downloads Annual and Half-year financial reports from AP2 website
- **PDF Parsing**: Extracts financial tables from PDFs automatically
- **Orchestrator**: Advanced scheduling, retry logic, and monitoring
- **Configurable**: Easy configuration for target years and report types
- **Organized Structure**: Timestamped folders for logs, downloads, and outputs
- **Latest Folder**: Always maintains the most recent data in a "latest" folder
- **Excel/CSV Output**: Exports data in structured format matching your schema
- **One-Click Run**: Windows batch files for easy operation

## Project Structure

```
SWEPENFND – AP2/
├── ap2_scraper.py          # Main scraper script
├── pdf_parser.py            # PDF parsing module
├── config.py                # Configuration file (IMPORTANT!)
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── logs/                   # Timestamped log files for each run
│   └── YYYYMMDD_HHMMSS/
│       └── scraper_*.log
│
├── downloads/              # Downloaded PDF files
│   └── YYYYMMDD_HHMMSS/
│       └── *.pdf
│
├── output/                 # Parsed financial data
│   ├── YYYYMMDD_HHMMSS/
│   │   └── AP2_Financial_Data_*.xlsx
│   └── latest/             # Always contains most recent data
│       └── AP2_Financial_Data_latest.xlsx
│
└── project information/    # Reference materials
    ├── AP2_SA_SWEPENFND_DATA_20220920.xlsx
    ├── AP2_SWEPENFND_Runbook.docx
    └── sample of the loaded site.txt
```

## Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- Internet connection

### Setup

1. **Clone or download this project** to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd "C:\Users\casto\Documents\SWEPENFND – AP2"
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

   If you encounter issues with camelot-py, you can skip it:
   ```bash
   pip install selenium undetected-chromedriver beautifulsoup4 lxml pdfplumber pandas openpyxl
   ```

## Configuration

Edit [config.py](config.py) to customize the scraper behavior:

### Target Year Settings

```python
# Scrape the latest year's reports
TARGET_YEAR = "latest"

# OR scrape a specific year
TARGET_YEAR = 2024

# OR scrape multiple years
TARGET_YEAR = None
YEARS_TO_SCRAPE = [2024, 2023, 2022]
```

### Report Types

```python
REPORT_TYPES = {
    'annual': True,      # Download Annual Reports
    'half_year': True,   # Download Half-year Reports
    'year_end': False    # Download Year-end Reports
}
```

### Output Format

```python
OUTPUT_CONFIG = {
    'output_format': 'xlsx',  # Options: 'xlsx', 'csv', 'both'
    'include_metadata': True,  # Include metadata sheet
}
```

### Important: Output Headers

The `OUTPUT_HEADERS` list in [config.py](config.py) contains all 21 column headers in **exact order** as per the sample data. **DO NOT CHANGE THE ORDER** of these headers unless you modify your entire data pipeline.

## Usage

### Quick Start (Windows)

Double-click these files:

1. **`install.bat`** - Install dependencies (first time only)
2. **`run.bat`** - Run the scraper
3. **`status.bat`** - Check status

### Basic Usage (Command Line)

Run the scraper with default settings (scrapes latest year):

```bash
# Using orchestrator (recommended - has retry logic)
python orchestrator.py run --retry

# Direct run
python ap2_scraper.py
```

### Scrape Specific Year

1. Edit [config.py](config.py):
   ```python
   TARGET_YEAR = 2024
   ```

2. Run the scraper:
   ```bash
   python orchestrator.py run --retry
   ```

### Scheduled Runs

Run automatically every day at 9 AM:

```bash
# Windows: Double-click schedule_daily.bat
# Or command line:
python orchestrator.py daily --hour 9 --minute 0
```

Run every 24 hours:

```bash
python orchestrator.py schedule --interval 24
```

See [ORCHESTRATOR_GUIDE.md](ORCHESTRATOR_GUIDE.md) for complete scheduling documentation.

### Scrape Multiple Years

1. Edit [config.py](config.py):
   ```python
   TARGET_YEAR = None
   YEARS_TO_SCRAPE = [2024, 2023, 2022]
   ```

2. Run the scraper:
   ```bash
   python ap2_scraper.py
   ```

## Output Data

### Excel Format

The output Excel file contains:

1. **Financial Data Sheet**: Main data with all 21 columns matching your schema
2. **Metadata Sheet**: Run information (timestamp, target year, reports processed)

### Data Schema

The output follows this exact column order:

1. `Unnamed: 0` - Year
2. `AP2.FUNDCAPITALCARRIEDFORWARD.LEVEL.NONE.H.1@AP2`
3. `AP2.NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM.FLOW.NONE.H.1@AP2`
4. ... (all 21 columns as defined in config.py)

### Finding Your Data

- **Latest data**: Always in `output/latest/AP2_Financial_Data_latest.xlsx`
- **Timestamped data**: In `output/YYYYMMDD_HHMMSS/AP2_Financial_Data_*.xlsx`
- **Downloaded PDFs**: In `downloads/YYYYMMDD_HHMMSS/`
- **Logs**: In `logs/YYYYMMDD_HHMMSS/scraper_*.log`

## Logging

The scraper provides detailed logging:

- **Console output**: Real-time progress information
- **Log files**: Detailed logs saved to `logs/` folder with timestamps

Log levels can be configured in [config.py](config.py):
```python
LOGGING_CONFIG = {
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
}
```

## Troubleshooting

### Chrome Driver Issues

If you get Chrome driver errors:
```bash
pip install --upgrade undetected-chromedriver
```

### PDF Parsing Issues

If PDFs are not parsing correctly:

1. Check the log files in `logs/` folder for detailed error messages
2. Verify PDFs were downloaded successfully in `downloads/` folder
3. Try adjusting PDF parsing settings in [config.py](config.py)

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### Website Structure Changed

If AP2 changes their website structure:

1. Check the logs for specific errors
2. The HTML structure may need updating in `ap2_scraper.py`
3. Verify the URL is still correct: https://ap2.se/en/news-and-reports/reports/financial-reports/

## Customization

### Adding Custom Fields

To extract additional fields from PDFs:

1. Add new header to `OUTPUT_HEADERS` in [config.py](config.py)
2. Add corresponding pattern in `field_patterns` dictionary in [pdf_parser.py](pdf_parser.py)
3. The parser will automatically attempt to extract matching data

### Changing Table Detection

Modify the `_is_financial_table()` method in [pdf_parser.py](pdf_parser.py) to adjust how financial tables are detected.

## Reference

- **AP2 Website**: https://ap2.se/en/news-and-reports/reports/financial-reports/
- **Sample Data**: See `project information/AP2_SA_SWEPENFND_DATA_20220920.xlsx`
- **Runbook**: See `project information/AP2_SWEPENFND_Runbook.docx`

## Notes

- The scraper respects cookies and handles the consent banner automatically
- Downloads are performed using Selenium to handle dynamic content
- PDF parsing uses pdfplumber for reliable table extraction
- All timestamps are in `YYYYMMDD_HHMMSS` format
- The "latest" folder is always updated with the most recent run

## Support

For issues or questions:

1. Check the log files in `logs/` folder
2. Verify your configuration in [config.py](config.py)
3. Ensure all dependencies are installed correctly
4. Check that Chrome browser is up to date

## Version History

- **v1.0** (2025-11-06): Initial release
  - Automated download from AP2 website
  - PDF parsing with table extraction
  - Configurable year and report type filtering
  - Timestamped folder structure
  - Excel/CSV output with metadata

---

**Last Updated**: 2025-11-06
