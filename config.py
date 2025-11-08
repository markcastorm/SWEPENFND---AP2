"""
Configuration file for AP2 Financial Reports Scraper
Contains all headers and settings in exact order as per sample data
"""

# ============================================================================
# OUTPUT HEADERS - EXACT ORDER FROM SAMPLE DATA (DO NOT CHANGE ORDER!)
# ============================================================================
OUTPUT_HEADERS = [
    'Unnamed: 0',
    'AP2.FUNDCAPITALCARRIEDFORWARD.LEVEL.NONE.H.1@AP2',
    'AP2.NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM.FLOW.NONE.H.1@AP2',
    'AP2.TOTAL.FLOW.NONE.H.1@AP2',
    'AP2.EQUITIESANDPARTICIPATIONSLISTED.FLOW.NONE.H.1@AP2',
    'AP2.EQUITIESANDPARTICIPATIONSUNLISTED.FLOW.NONE.H.1@AP2',
    'AP2.BONDSANDOTHERFIXEDINCOMESECURITIES.FLOW.NONE.H.1@AP2',
    'AP2.DERIVATIVEINSTRUMENTS.FLOW.NONE.H.1@AP2',
    'AP2.CASHANDBANKBALANCES.FLOW.NONE.H.1@AP2',
    'AP2.OTHERASSETS.FLOW.NONE.H.1@AP2',
    'AP2.PREPAIDEXPENSESANDACCRUEDINCOME.FLOW.NONE.H.1@AP2',
    'AP2.TOTALASSETS.FLOW.NONE.H.1@AP2',
    'AP2.DERIVATIVEINSTRUMENTSLIABILITIES.FLOW.NONE.H.1@AP2',
    'AP2.OTHERLIABILITIES.FLOW.NONE.H.1@AP2',
    'AP2.DEFERREDINCOMEANDACCRUEDEXPENSES.FLOW.NONE.H.1@AP2',
    'AP2.TOTALLIABILITIES.FLOW.NONE.H.1@AP2',
    'AP2.FUNDCAPITALCARRIEDFORWARD.FLOW.NONE.H.1@AP2',
    'AP2.NETPAYMENTSTOTHENATIONALPENSIONSYSTEM.FLOW.NONE.H.1@AP2',
    'AP2.NETRESULTFORTHEPERIOD.FLOW.NONE.H.1@AP2',
    'AP2.TOTALFUNDCAPITAL.FLOW.NONE.H.1@AP2',
    'AP2.TOTALFUNDCAPITALANDLIABILITIES.FLOW.NONE.H.1@AP2'
]

# Human-readable sub-headers (Row 2 in Excel) - EXACT match to sample
OUTPUT_SUBHEADERS = [
    None,  # First column has no sub-header
    'AP2 semi-annual: Fund capital carried forward',
    'AP2 semi-annual: Net outflows to the national pension system',
    'AP2 semi-annual: Net result for the year',
    'AP2 semi-annual: Balance - Equities and participations - Listed',
    'AP2 semi-annual: Balance - Equities and participations - Unlisted',
    'AP2 semi-annual: Balance - Bonds and other fixed-income securities',
    'AP2 semi-annual: Balance - Derivative instruments',
    'AP2 semi-annual: Balance - Cash and bank balances',
    'AP2 semi-annual: Balance - Other assets',
    'AP2 semi-annual: Balance - Prepaid expenses and accrued income',
    'AP2 semi-annual: Balance - Total Assets',
    'AP2 semi-annual: Balance - Derivative instruments (liabilities)',
    'AP2 semi-annual: Balance - Other liabilities',
    'AP2 semi-annual: Balance - Deferred income and accrued expenses',
    'AP2 semi-annual: Balance - Total liabilities',
    'AP2 semi-annual: Balance - Fund capital carried forward',
    'AP2 semi-annual: Balance - Net payments to the national pension system',
    'AP2 semi-annual: Balance - Net result for the period',
    'AP2 semi-annual: Balance - Total Fund capital',
    'AP2 semi-annual: Balance - Total Fund capital and other Liabilities'
]

# Readable header mapping for reference
HEADER_MAPPING = {
    'Fund Capital Carried Forward (Level)': 'AP2.FUNDCAPITALCARRIEDFORWARD.LEVEL.NONE.H.1@AP2',
    'Net Outflows to National Pension System': 'AP2.NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM.FLOW.NONE.H.1@AP2',
    'Total': 'AP2.TOTAL.FLOW.NONE.H.1@AP2',
    'Equities and Participations - Listed': 'AP2.EQUITIESANDPARTICIPATIONSLISTED.FLOW.NONE.H.1@AP2',
    'Equities and Participations - Unlisted': 'AP2.EQUITIESANDPARTICIPATIONSUNLISTED.FLOW.NONE.H.1@AP2',
    'Bonds and Other Fixed Income Securities': 'AP2.BONDSANDOTHERFIXEDINCOMESECURITIES.FLOW.NONE.H.1@AP2',
    'Derivative Instruments (Assets)': 'AP2.DERIVATIVEINSTRUMENTS.FLOW.NONE.H.1@AP2',
    'Cash and Bank Balances': 'AP2.CASHANDBANKBALANCES.FLOW.NONE.H.1@AP2',
    'Other Assets': 'AP2.OTHERASSETS.FLOW.NONE.H.1@AP2',
    'Prepaid Expenses and Accrued Income': 'AP2.PREPAIDEXPENSESANDACCRUEDINCOME.FLOW.NONE.H.1@AP2',
    'Total Assets': 'AP2.TOTALASSETS.FLOW.NONE.H.1@AP2',
    'Derivative Instruments (Liabilities)': 'AP2.DERIVATIVEINSTRUMENTSLIABILITIES.FLOW.NONE.H.1@AP2',
    'Other Liabilities': 'AP2.OTHERLIABILITIES.FLOW.NONE.H.1@AP2',
    'Deferred Income and Accrued Expenses': 'AP2.DEFERREDINCOMEANDACCRUEDEXPENSES.FLOW.NONE.H.1@AP2',
    'Total Liabilities': 'AP2.TOTALLIABILITIES.FLOW.NONE.H.1@AP2',
    'Fund Capital Carried Forward (Flow)': 'AP2.FUNDCAPITALCARRIEDFORWARD.FLOW.NONE.H.1@AP2',
    'Net Payments to National Pension System': 'AP2.NETPAYMENTSTOTHENATIONALPENSIONSYSTEM.FLOW.NONE.H.1@AP2',
    'Net Result for the Period': 'AP2.NETRESULTFORTHEPERIOD.FLOW.NONE.H.1@AP2',
    'Total Fund Capital': 'AP2.TOTALFUNDCAPITAL.FLOW.NONE.H.1@AP2',
    'Total Fund Capital and Liabilities': 'AP2.TOTALFUNDCAPITALANDLIABILITIES.FLOW.NONE.H.1@AP2'
}

# ============================================================================
# SCRAPING CONFIGURATION
# ============================================================================

# Website URL
BASE_URL = "https://ap2.se/en/news-and-reports/reports/financial-reports/"

# Year settings
# Set TARGET_YEAR to a specific year (e.g., 2024) or "latest" to scrape the most recent year
TARGET_YEAR = 2018  # Options: "latest" or specific year like 2024, 2023, etc.

# Alternative: Set specific years to scrape (if TARGET_YEAR is not "latest")
# YEARS_TO_SCRAPE = [2024, 2023, 2022]  # Can be a list of years
YEARS_TO_SCRAPE = None  # Set to None to use TARGET_YEAR setting

# Report types to download
REPORT_TYPES = {
    'annual': False,      # Download Annual Reports
    'half_year': True,   # Download Half-year Reports
    'year_end': False    # Download Year-end Reports (rare, only some years)
}

# ============================================================================
# FOLDER STRUCTURE CONFIGURATION
# ============================================================================

# Base project directory (auto-detected)
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Folder names
LOGS_FOLDER = "logs"
DOWNLOADS_FOLDER = "downloads"
OUTPUT_FOLDER = "output"
LATEST_FOLDER_NAME = "latest"

# Full paths (auto-generated)
LOGS_DIR = os.path.join(PROJECT_ROOT, LOGS_FOLDER)
DOWNLOADS_DIR = os.path.join(PROJECT_ROOT, DOWNLOADS_FOLDER)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, OUTPUT_FOLDER)

# ============================================================================
# PDF PARSING CONFIGURATION
# ============================================================================

# Table keywords to search for in PDFs
TABLE_KEYWORDS = [
    'balance sheet',
    'statement of financial position',
    'assets and liabilities',
    'fund capital',
    'total assets',
    'income statement',
    'statement of comprehensive income'
]

# PDF parsing settings
PDF_PARSING = {
    'use_tabula': True,      # Use tabula-py for table extraction
    'use_camelot': True,     # Use camelot for table extraction (fallback)
    'multiple_tables': True,  # Extract multiple tables from each PDF
    'lattice_mode': True,    # Use lattice mode for tables with borders
    'stream_mode': True,     # Use stream mode for tables without borders
}

# ============================================================================
# SELENIUM/BROWSER CONFIGURATION
# ============================================================================

SELENIUM_CONFIG = {
    'implicit_wait': 10,        # Implicit wait time in seconds
    'page_load_timeout': 30,    # Page load timeout
    'download_timeout': 120,    # Download completion timeout
    'use_undetected_chrome': True,  # Use undetected_chromedriver
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    'log_level': 'INFO',  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_to_console': True,
    'log_to_file': True,
}

# ============================================================================
# OUTPUT FILE CONFIGURATION
# ============================================================================

OUTPUT_CONFIG = {
    'output_format': 'xlsx',  # Options: 'xlsx', 'csv', 'both'
    'include_metadata': True,  # Include metadata sheet with run information
    'preserve_formatting': True,  # Preserve number formatting
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_timestamp():
    """Generate timestamp for folder naming"""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_run_folders(timestamp=None):
    """Get folder paths for a specific run"""
    if timestamp is None:
        timestamp = get_timestamp()

    return {
        'timestamp': timestamp,
        'logs': os.path.join(LOGS_DIR, timestamp),
        'downloads': os.path.join(DOWNLOADS_DIR, timestamp),
        'output': os.path.join(OUTPUT_DIR, timestamp),
        'latest_output': os.path.join(OUTPUT_DIR, LATEST_FOLDER_NAME)
    }

def create_run_folders(timestamp=None):
    """Create all necessary folders for a run"""
    folders = get_run_folders(timestamp)

    for folder_path in [folders['logs'], folders['downloads'], folders['output'], folders['latest_output']]:
        os.makedirs(folder_path, exist_ok=True)

    return folders

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate configuration settings"""
    errors = []

    # Validate headers
    if len(OUTPUT_HEADERS) != 21:
        errors.append(f"Expected 21 headers, got {len(OUTPUT_HEADERS)}")

    # Validate year settings - be flexible with string/int
    if TARGET_YEAR is not None:
        if isinstance(TARGET_YEAR, str) and TARGET_YEAR.lower() != "latest":
            try:
                int(TARGET_YEAR)
            except ValueError:
                errors.append(f"TARGET_YEAR must be 'latest' or a year number, got '{TARGET_YEAR}'")

    # Validate report types
    if not any(REPORT_TYPES.values()):
        errors.append("At least one report type must be enabled")

    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))

    return True

# Validate on import
validate_config()
