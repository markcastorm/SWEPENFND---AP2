"""
AP2 Financial Reports Scraper
Automated scraper for downloading and parsing AP2 financial reports
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

import config
from pdf_parser import PDFParser


class AP2Scraper:
    """Main scraper class for AP2 financial reports"""

    def __init__(self):
        """Initialize the scraper"""
        self.timestamp = config.get_timestamp()
        self.folders = config.create_run_folders(self.timestamp)
        self.logger = self._setup_logging()
        self.driver = None
        self.pdf_parser = PDFParser(self.logger)
        self.downloaded_files = []
        self.parsed_data = []

    def _setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(self.folders['logs'], f"scraper_{self.timestamp}.log")

        logger = logging.getLogger('AP2Scraper')
        logger.setLevel(getattr(logging, config.LOGGING_CONFIG['log_level']))

        # File handler
        if config.LOGGING_CONFIG['log_to_file']:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(config.LOGGING_CONFIG['log_format']))
            logger.addHandler(file_handler)

        # Console handler
        if config.LOGGING_CONFIG['log_to_console']:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(config.LOGGING_CONFIG['log_format']))
            logger.addHandler(console_handler)

        return logger

    def setup_driver(self):
        """Initialize Selenium WebDriver with download preferences"""
        self.logger.info("Setting up Chrome driver...")

        options = uc.ChromeOptions()

        # Set download directory
        prefs = {
            "download.default_directory": self.folders['downloads'],
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,  # Download PDFs instead of opening
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = uc.Chrome(options=options)
        self.driver.implicitly_wait(config.SELENIUM_CONFIG['implicit_wait'])
        self.logger.info("Chrome driver setup complete")

        return self.driver

    def wait_for_download_completion(self, initial_files, timeout=None):
        """Wait for a new file to appear and finish downloading"""
        if timeout is None:
            timeout = config.SELENIUM_CONFIG['download_timeout']

        download_dir = self.folders['downloads']
        start_time = time.time()

        self.logger.debug(f"Waiting for download completion (timeout: {timeout}s)...")

        while time.time() - start_time < timeout:
            current_files = set(os.listdir(download_dir))
            new_files = current_files - initial_files

            # Remove temporary/partial downloads
            complete_files = {f for f in new_files if not f.endswith((".crdownload", ".tmp", ".part"))}

            if complete_files:
                new_file = list(complete_files)[0]
                file_path = os.path.join(download_dir, new_file)

                # Check file size stability (ensure download is complete)
                time.sleep(1)
                size1 = os.path.getsize(file_path)
                time.sleep(2)
                size2 = os.path.getsize(file_path)

                if size1 == size2 and size2 > 0:
                    self.logger.info(f"Download complete: {new_file} ({size2 / 1024:.2f} KB)")
                    return file_path

            time.sleep(1)

        raise TimeoutError(f"Download did not complete within {timeout} seconds")

    def parse_financial_reports_page(self):
        """Parse the financial reports page and extract report links"""
        self.logger.info(f"Navigating to {config.BASE_URL}...")
        self.driver.get(config.BASE_URL)
        time.sleep(3)  # Wait for page to load

        # Accept cookies if present
        try:
            accept_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'cmplz-accept')]"))
            )
            accept_button.click()
            self.logger.info("Accepted cookie consent")
            time.sleep(2)
        except Exception as e:
            self.logger.debug("No cookie banner found or already accepted")

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Extract all report links
        reports = []
        content_div = soup.find('div', class_='content')

        if not content_div:
            self.logger.error("Could not find content div on page")
            return reports

        # Find all year sections
        current_year = None
        for element in content_div.find_all(['h2', 'div', 'p']):

            # Check if it's a year header
            if element.name == 'h2' and element.get('class') and 'wp-block-heading' in element.get('class'):
                try:
                    current_year = int(element.text.strip())
                    self.logger.debug(f"Found year section: {current_year}")
                except ValueError:
                    continue

            # Check for report links
            if current_year:
                links = element.find_all('a', href=True)
                for link in links:
                    href = link.get('href')
                    if href and href.endswith('.pdf'):
                        report_name = link.text.strip()
                        report_type = self._classify_report_type(report_name)

                        reports.append({
                            'year': current_year,
                            'name': report_name,
                            'url': href,
                            'type': report_type
                        })

                        self.logger.debug(f"Found report: {report_name} ({current_year}) - {report_type}")

        self.logger.info(f"Found {len(reports)} total reports on the page")
        return reports

    def _classify_report_type(self, report_name):
        """Classify report type based on name"""
        name_lower = report_name.lower()

        if 'half-year' in name_lower or 'half year' in name_lower:
            return 'half_year'
        elif 'annual' in name_lower:
            return 'annual'
        elif 'year-end' in name_lower or 'year end' in name_lower:
            return 'year_end'
        else:
            return 'unknown'

    def filter_reports(self, all_reports):
        """Filter reports based on configuration settings"""
        filtered = []

        # Determine target years
        if config.TARGET_YEAR == "latest":
            if all_reports:
                target_years = [max(r['year'] for r in all_reports)]
                self.logger.info(f"Latest year detected: {target_years[0]}")
        elif config.YEARS_TO_SCRAPE:
            target_years = config.YEARS_TO_SCRAPE
        else:
            target_years = [config.TARGET_YEAR]

        self.logger.info(f"Target years: {target_years}")

        # Filter by year and report type
        for report in all_reports:
            if report['year'] in target_years:
                report_type = report['type']
                if report_type in config.REPORT_TYPES and config.REPORT_TYPES[report_type]:
                    filtered.append(report)
                    self.logger.info(f"Selected: {report['name']} ({report['year']})")

        self.logger.info(f"Filtered to {len(filtered)} reports to download")
        return filtered

    def download_report(self, report):
        """Download a single report"""
        self.logger.info(f"Downloading: {report['name']}...")

        try:
            # Get initial files
            initial_files = set(os.listdir(self.folders['downloads']))

            # Navigate to PDF URL (this triggers download)
            self.driver.get(report['url'])

            # Wait for download to complete
            downloaded_file = self.wait_for_download_completion(initial_files)

            # Rename file to include year and report type
            new_filename = f"AP2_{report['year']}_{report['type']}.pdf"
            new_filepath = os.path.join(self.folders['downloads'], new_filename)

            # Rename if file doesn't already exist with that name
            if downloaded_file != new_filepath:
                if os.path.exists(new_filepath):
                    os.remove(new_filepath)
                os.rename(downloaded_file, new_filepath)
                downloaded_file = new_filepath

            report['local_path'] = downloaded_file
            self.downloaded_files.append(report)

            self.logger.info(f"Successfully downloaded: {new_filename}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to download {report['name']}: {str(e)}")
            return False

    def parse_downloaded_pdfs(self):
        """Parse all downloaded PDFs to extract financial data"""
        self.logger.info(f"Parsing {len(self.downloaded_files)} downloaded PDFs...")

        for report in self.downloaded_files:
            self.logger.info(f"Parsing: {report['name']}...")

            try:
                # Parse the PDF
                tables = self.pdf_parser.extract_tables_from_pdf(report['local_path'])

                if tables:
                    self.logger.info(f"Extracted {len(tables)} tables from {report['name']}")

                    # Process and map tables to our data structure
                    parsed_data = self.pdf_parser.map_to_output_format(
                        tables,
                        year=report['year'],
                        report_type=report['type']
                    )

                    if parsed_data:
                        self.parsed_data.append(parsed_data)
                        self.logger.info(f"Successfully mapped data for {report['name']}")
                    else:
                        self.logger.warning(f"Could not map data for {report['name']}")
                else:
                    self.logger.warning(f"No tables found in {report['name']}")

            except Exception as e:
                self.logger.error(f"Error parsing {report['name']}: {str(e)}")
                import traceback
                self.logger.debug(traceback.format_exc())

        self.logger.info(f"Parsed {len(self.parsed_data)} reports successfully")

    def save_output(self):
        """Save parsed data to output files"""
        self.logger.info("Saving output data...")

        if not self.parsed_data:
            self.logger.warning("No data to save")
            return

        # Combine all parsed data into a single DataFrame
        df = pd.DataFrame(self.parsed_data, columns=config.OUTPUT_HEADERS)

        # Save to timestamped folder
        output_file_base = os.path.join(self.folders['output'], f"AP2_Financial_Data_{self.timestamp}")
        latest_file_base = os.path.join(self.folders['latest_output'], "AP2_Financial_Data_latest")

        # Save based on configuration
        if config.OUTPUT_CONFIG['output_format'] in ['xlsx', 'both']:
            xlsx_file = f"{output_file_base}.xlsx"
            latest_xlsx = f"{latest_file_base}.xlsx"

            # Save with metadata
            with pd.ExcelWriter(xlsx_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Financial Data', index=False)

                if config.OUTPUT_CONFIG['include_metadata']:
                    metadata = pd.DataFrame({
                        'Property': ['Run Timestamp', 'Target Year', 'Reports Downloaded', 'Reports Parsed'],
                        'Value': [self.timestamp, config.TARGET_YEAR, len(self.downloaded_files), len(self.parsed_data)]
                    })
                    metadata.to_excel(writer, sheet_name='Metadata', index=False)

            # Copy to latest folder
            import shutil
            shutil.copy2(xlsx_file, latest_xlsx)

            self.logger.info(f"Saved Excel file: {xlsx_file}")
            self.logger.info(f"Saved to latest: {latest_xlsx}")

        if config.OUTPUT_CONFIG['output_format'] in ['csv', 'both']:
            csv_file = f"{output_file_base}.csv"
            latest_csv = f"{latest_file_base}.csv"

            df.to_csv(csv_file, index=False)

            # Copy to latest folder
            import shutil
            shutil.copy2(csv_file, latest_csv)

            self.logger.info(f"Saved CSV file: {csv_file}")
            self.logger.info(f"Saved to latest: {latest_csv}")

    def run(self):
        """Main execution method"""
        self.logger.info("=" * 80)
        self.logger.info("AP2 Financial Reports Scraper - Starting")
        self.logger.info("=" * 80)
        self.logger.info(f"Run timestamp: {self.timestamp}")
        self.logger.info(f"Target year: {config.TARGET_YEAR}")
        self.logger.info(f"Logs directory: {self.folders['logs']}")
        self.logger.info(f"Downloads directory: {self.folders['downloads']}")
        self.logger.info(f"Output directory: {self.folders['output']}")

        try:
            # Setup driver
            self.setup_driver()

            # Parse the reports page
            all_reports = self.parse_financial_reports_page()

            # Filter reports based on configuration
            reports_to_download = self.filter_reports(all_reports)

            if not reports_to_download:
                self.logger.warning("No reports match the filter criteria")
                return

            # Download reports
            self.logger.info(f"Downloading {len(reports_to_download)} reports...")
            for report in reports_to_download:
                self.download_report(report)
                time.sleep(2)  # Brief pause between downloads

            # Parse downloaded PDFs
            self.parse_downloaded_pdfs()

            # Save output
            self.save_output()

            self.logger.info("=" * 80)
            self.logger.info("AP2 Financial Reports Scraper - Completed Successfully")
            self.logger.info("=" * 80)
            self.logger.info(f"Total reports downloaded: {len(self.downloaded_files)}")
            self.logger.info(f"Total reports parsed: {len(self.parsed_data)}")
            self.logger.info(f"Output saved to: {self.folders['output']}")

        except Exception as e:
            self.logger.error(f"Critical error during execution: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

        finally:
            if self.driver:
                self.logger.info("Closing browser...")
                self.driver.quit()


def main():
    """Main entry point"""
    scraper = AP2Scraper()
    scraper.run()


if __name__ == "__main__":
    main()
