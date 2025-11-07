# AP2 Financial Reports Scraper - Project Summary

## Overview

Complete automated scraping solution for AP2 (Andra AP-fonden) Swedish pension fund financial reports. Downloads PDFs from their website, extracts financial data tables, and outputs structured data matching your exact 21-column schema.

## Project Location

```
C:\Users\casto\Documents\SWEPENFND – AP2\
```

## Complete File Structure

```
SWEPENFND – AP2/
│
├── Core Scripts
│   ├── config.py              # Configuration with 21 headers in exact order
│   ├── ap2_scraper.py         # Main scraper with Selenium automation
│   ├── pdf_parser.py          # PDF table extraction and parsing
│   ├── orchestrator.py        # Scheduling and automation controller
│   └── test_config.py         # Configuration validation script
│
├── Windows Batch Files (Double-click to run)
│   ├── install.bat            # Install all dependencies
│   ├── run.bat                # Run scraper once
│   ├── status.bat             # Show scraper status
│   └── schedule_daily.bat     # Run daily at 9 AM
│
├── Documentation
│   ├── README.md              # Complete documentation
│   ├── QUICKSTART.md          # Quick start guide
│   ├── ORCHESTRATOR_GUIDE.md  # Orchestrator manual
│   ├── PROJECT_SUMMARY.md     # This file
│   └── requirements.txt       # Python dependencies
│
├── Project Information (Reference)
│   └── project information/
│       ├── AP2_SA_SWEPENFND_DATA_20220920.xlsx  # Sample data
│       ├── AP2_SWEPENFND_Runbook.docx           # Runbook
│       └── sample of the loaded site.txt         # Site HTML
│
├── Output Folders (Auto-created)
│   ├── logs/
│   │   ├── orchestrator.log
│   │   └── YYYYMMDD_HHMMSS/
│   │       └── scraper_*.log
│   │
│   ├── downloads/
│   │   └── YYYYMMDD_HHMMSS/
│   │       └── *.pdf
│   │
│   └── output/
│       ├── YYYYMMDD_HHMMSS/
│       │   └── AP2_Financial_Data_*.xlsx
│       └── latest/                 ← Always current!
│           └── AP2_Financial_Data_latest.xlsx
│
└── State Files (Auto-created)
    └── orchestrator_state.json    # Run history and stats
```

## Key Features

### 1. Automated Web Scraping
- Uses Selenium with undetected-chromedriver
- Handles cookie consent automatically
- Extracts all report links from AP2 website
- Filters by year and report type
- Downloads PDFs with verification

### 2. PDF Parsing
- Extracts tables using pdfplumber
- Identifies financial tables automatically
- Pattern-based field extraction
- Maps to 21-column output schema
- Handles multiple table formats

### 3. Orchestrator
- **Run once**: Simple execution with retry logic
- **Schedule**: Run every N hours automatically
- **Daily**: Run at specific time each day
- **Status**: Monitor success/failure history
- **Clean**: Remove old files automatically
- **State tracking**: Maintains run history

### 4. Configuration System
- **21 headers** in exact order (DO NOT CHANGE ORDER!)
- Configure target year: "latest" or specific year
- Select report types: Annual, Half-year
- Choose output format: Excel, CSV, or both
- Adjustable logging and parsing settings

### 5. Folder Organization
- Timestamped folders for each run
- Separate logs, downloads, and outputs
- "latest" folder always contains newest data
- Easy cleanup of old runs

## Quick Start

### For Windows Users (Easiest)

1. **Install** (first time only)
   - Double-click `install.bat`
   - Wait for installation to complete

2. **Run**
   - Double-click `run.bat`
   - Results appear in `output\latest\`

3. **Check Status**
   - Double-click `status.bat`

### For Command Line Users

```bash
# Install
pip install -r requirements.txt

# Test configuration
python test_config.py

# Run once
python orchestrator.py run --retry

# Check status
python orchestrator.py status
```

## Common Use Cases

### Use Case 1: One-Time Data Collection

**Goal**: Get the latest financial data right now

**Steps**:
1. Double-click `run.bat` (or `python orchestrator.py run --retry`)
2. Wait for completion (2-5 minutes)
3. Open `output\latest\AP2_Financial_Data_latest.xlsx`

### Use Case 2: Daily Automated Collection

**Goal**: Automatically collect data every morning

**Steps**:
1. Double-click `schedule_daily.bat`
2. Keep window open (or setup as Windows Task)
3. Data updates automatically each day

### Use Case 3: Historical Data Collection

**Goal**: Get data for multiple past years

**Steps**:
1. Edit `config.py`:
   ```python
   TARGET_YEAR = None
   YEARS_TO_SCRAPE = [2024, 2023, 2022, 2021]
   ```
2. Run: `python orchestrator.py run --retry`
3. Results consolidated in output folder

### Use Case 4: Monitoring and Maintenance

**Goal**: Track scraper performance over time

**Steps**:
1. Check status: `python orchestrator.py status`
2. Review logs: `logs\orchestrator.log`
3. Clean old files: `python orchestrator.py clean --keep-days 30`

## Configuration Examples

### Example 1: Scrape Latest Year Only

```python
# In config.py
TARGET_YEAR = "latest"

REPORT_TYPES = {
    'annual': True,
    'half_year': True,
}
```

### Example 2: Scrape 2024 Annual Reports

```python
# In config.py
TARGET_YEAR = 2024

REPORT_TYPES = {
    'annual': True,
    'half_year': False,
}
```

### Example 3: Scrape Multiple Years

```python
# In config.py
TARGET_YEAR = None
YEARS_TO_SCRAPE = [2024, 2023, 2022]

REPORT_TYPES = {
    'annual': True,
    'half_year': True,
}
```

## Data Schema

### Output Headers (21 columns - EXACT ORDER)

1. `Unnamed: 0` - Year
2. `AP2.FUNDCAPITALCARRIEDFORWARD.LEVEL.NONE.H.1@AP2`
3. `AP2.NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM.FLOW.NONE.H.1@AP2`
4. `AP2.TOTAL.FLOW.NONE.H.1@AP2`
5. `AP2.EQUITIESANDPARTICIPATIONSLISTED.FLOW.NONE.H.1@AP2`
6. `AP2.EQUITIESANDPARTICIPATIONSUNLISTED.FLOW.NONE.H.1@AP2`
7. `AP2.BONDSANDOTHERFIXEDINCOMESECURITIES.FLOW.NONE.H.1@AP2`
8. `AP2.DERIVATIVEINSTRUMENTS.FLOW.NONE.H.1@AP2`
9. `AP2.CASHANDBANKBALANCES.FLOW.NONE.H.1@AP2`
10. `AP2.OTHERASSETS.FLOW.NONE.H.1@AP2`
11. `AP2.PREPAIDEXPENSESANDACCRUEDINCOME.FLOW.NONE.H.1@AP2`
12. `AP2.TOTALASSETS.FLOW.NONE.H.1@AP2`
13. `AP2.DERIVATIVEINSTRUMENTSLIABILITIES.FLOW.NONE.H.1@AP2`
14. `AP2.OTHERLIABILITIES.FLOW.NONE.H.1@AP2`
15. `AP2.DEFERREDINCOMEANDACCRUEDEXPENSES.FLOW.NONE.H.1@AP2`
16. `AP2.TOTALLIABILITIES.FLOW.NONE.H.1@AP2`
17. `AP2.FUNDCAPITALCARRIEDFORWARD.FLOW.NONE.H.1@AP2`
18. `AP2.NETPAYMENTSTOTHENATIONALPENSIONSYSTEM.FLOW.NONE.H.1@AP2`
19. `AP2.NETRESULTFORTHEPERIOD.FLOW.NONE.H.1@AP2`
20. `AP2.TOTALFUNDCAPITAL.FLOW.NONE.H.1@AP2`
21. `AP2.TOTALFUNDCAPITALANDLIABILITIES.FLOW.NONE.H.1@AP2`

**IMPORTANT**: Never change this order! Your downstream systems depend on it.

## Orchestrator Commands Reference

```bash
# Basic execution
python orchestrator.py run                              # Run once
python orchestrator.py run --retry                      # Run with auto-retry
python orchestrator.py run --retry --max-retries 5      # Custom retry

# Scheduling
python orchestrator.py schedule --interval 24           # Every 24 hours
python orchestrator.py daily --hour 9 --minute 0        # Daily at 9:00 AM

# Monitoring
python orchestrator.py status                           # Show status & history

# Maintenance
python orchestrator.py clean --keep-days 30             # Clean old files
```

## Technology Stack

- **Python 3.8+**: Core language
- **Selenium**: Web browser automation
- **undetected-chromedriver**: Anti-detection Chrome driver
- **BeautifulSoup4**: HTML parsing
- **pdfplumber**: PDF table extraction
- **pandas**: Data manipulation
- **openpyxl**: Excel file writing

## Dependencies

All dependencies listed in `requirements.txt`:

```
selenium>=4.15.0
undetected-chromedriver>=3.5.4
beautifulsoup4>=4.12.0
pdfplumber>=0.10.0
pandas>=2.0.0
openpyxl>=3.1.0
```

Install with: `pip install -r requirements.txt`

## Troubleshooting

### Issue: "Python not found"
**Solution**: Install Python 3.8+ from https://www.python.org/

### Issue: "Chrome driver error"
**Solution**:
```bash
pip install --upgrade undetected-chromedriver
```

### Issue: "No data extracted from PDFs"
**Solution**:
1. Check logs in `logs/` folder
2. Verify PDFs downloaded correctly in `downloads/` folder
3. PDF structure may have changed - check `pdf_parser.py`

### Issue: "Import errors"
**Solution**:
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "Permission denied" on folders
**Solution**: Run as administrator or check folder permissions

## Support Documentation

- **[README.md](README.md)** - Complete project documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 steps
- **[ORCHESTRATOR_GUIDE.md](ORCHESTRATOR_GUIDE.md)** - Complete orchestrator manual

## Source Information

- **Website**: https://ap2.se/en/news-and-reports/reports/financial-reports/
- **Data Coverage**: Financial reports from 2001-2025
- **Report Types**: Annual Reports, Half-year Reports, Year-end Reports
- **Update Frequency**: Semi-annually (every 6 months)

## Project History

- **Created**: 2025-11-06
- **Based on**: KMFK runbook automation pattern
- **Sample Data**: AP2_SA_SWEPENFND_DATA_20220920.xlsx
- **Version**: 1.0

## Best Practices

1. **Test Before Scheduling**: Always run `python test_config.py` first
2. **Start Manual**: Do one manual run before scheduling
3. **Monitor Initially**: Check status after first few scheduled runs
4. **Regular Cleanup**: Run cleanup monthly to save disk space
5. **Backup Config**: Keep backups of `config.py` with your settings
6. **Check Logs**: Review logs if any issues occur
7. **Update Dependencies**: Occasionally update with `pip install -r requirements.txt --upgrade`

## Success Indicators

✅ `output/latest/` contains recent Excel file
✅ `python orchestrator.py status` shows successful runs
✅ No errors in `logs/orchestrator.log`
✅ Excel file has 21 columns in correct order
✅ Data matches report years configured

## Next Steps

1. **Install dependencies**: Run `install.bat` or `pip install -r requirements.txt`
2. **Test setup**: Run `python test_config.py`
3. **Configure**: Edit `config.py` if needed
4. **First run**: Execute `run.bat` or `python orchestrator.py run --retry`
5. **Check results**: Open `output/latest/AP2_Financial_Data_latest.xlsx`
6. **Schedule** (optional): Setup daily runs with `schedule_daily.bat`

## Contact & Support

For issues:
1. Check documentation in README.md
2. Review logs in `logs/` folder
3. Verify configuration in `config.py`
4. Test with `python test_config.py`

---

**Ready to use! Start with `install.bat` then `run.bat`** 🚀
