"""
AP2 Financial Reports Scraper
Downloads PDF reports from AP2 website
"""

import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

import config

# Setup timestamp for this run
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
download_dir = os.path.join('downloads', timestamp)
os.makedirs(download_dir, exist_ok=True)

print("=" * 80)
print("AP2 Financial Reports Scraper")
print("=" * 80)
print(f"Target year: {config.TARGET_YEAR}")
print(f"Download directory: {download_dir}")
print(f"Website: {config.BASE_URL}")


def setup_driver():
    """Initialize Chrome driver"""
    print("\nSetting up Chrome driver...")

    options = uc.ChromeOptions()
    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options)
    driver.implicitly_wait(10)

    print("OK Chrome driver ready")
    return driver


def wait_for_download(initial_files, timeout=120):
    """Wait for download to complete"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        complete_files = {f for f in new_files if not f.endswith((".crdownload", ".tmp", ".part"))}

        if complete_files:
            new_file = list(complete_files)[0]
            file_path = os.path.join(download_dir, new_file)

            # Check file stability
            time.sleep(1)
            size1 = os.path.getsize(file_path)
            time.sleep(2)
            size2 = os.path.getsize(file_path)

            if size1 == size2 and size2 > 0:
                print(f"  OK Downloaded: {new_file} ({size2 / 1024:.1f} KB)")
                return file_path

        time.sleep(1)

    raise TimeoutError(f"Download timeout after {timeout}s")


def parse_reports_page(driver):
    """Parse the financial reports page"""
    print(f"\nNavigating to {config.BASE_URL}...")
    driver.get(config.BASE_URL)
    time.sleep(3)

    # Accept cookies
    try:
        accept_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'cmplz-accept')]"))
        )
        accept_btn.click()
        print("OK Accepted cookies")
        time.sleep(2)
    except:
        pass

    # Parse page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    content_div = soup.find('div', class_='content')

    if not content_div:
        print("ERROR: Could not find content div")
        return []

    reports = []
    current_year = None

    for element in content_div.find_all(['h2', 'div', 'p']):
        # Check for year header
        if element.name == 'h2' and element.get('class') and 'wp-block-heading' in element.get('class'):
            try:
                current_year = int(element.text.strip())
            except:
                continue

        # Check for report links
        if current_year:
            links = element.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href and href.endswith('.pdf'):
                    report_name = link.text.strip()
                    report_type = 'half_year' if 'half' in report_name.lower() else 'annual'

                    reports.append({
                        'year': current_year,
                        'name': report_name,
                        'url': href,
                        'type': report_type
                    })

    # Deduplicate by URL (same report may appear multiple times on page)
    seen_urls = set()
    unique_reports = []
    for report in reports:
        if report['url'] not in seen_urls:
            seen_urls.add(report['url'])
            unique_reports.append(report)

    print(f"OK Found {len(unique_reports)} unique reports on page")
    return unique_reports


def filter_reports(all_reports):
    """Filter reports based on config"""
    # Determine target year
    if config.TARGET_YEAR == "latest":
        if all_reports:
            target_year = max(r['year'] for r in all_reports)
            print(f"\n'latest' resolved to year: {target_year}")
        else:
            print("ERROR: No reports found")
            return []
    else:
        target_year = int(config.TARGET_YEAR)
        print(f"\nTarget year: {target_year}")

    # Filter
    filtered = []
    for report in all_reports:
        if report['year'] == target_year:
            if config.REPORT_TYPES.get(report['type'], False):
                filtered.append(report)
                print(f"  - {report['name']}")

    print(f"\nOK Filtered to {len(filtered)} reports to download")
    return filtered


def download_reports(driver, reports):
    """Download all filtered reports"""
    print(f"\n{'='*80}")
    print("DOWNLOADING REPORTS")
    print(f"{'='*80}")

    downloaded = []

    for i, report in enumerate(reports, 1):
        print(f"\n[{i}/{len(reports)}] {report['name']}...")

        try:
            initial_files = set(os.listdir(download_dir))
            driver.get(report['url'])
            downloaded_file = wait_for_download(initial_files)

            # Rename with year and type
            new_name = f"AP2_{report['year']}_{report['type']}.pdf"
            new_path = os.path.join(download_dir, new_name)

            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(downloaded_file, new_path)

            downloaded.append(new_path)
            time.sleep(2)

        except Exception as e:
            print(f"  FAILED Failed: {e}")

    return downloaded


def main():
    """Main execution"""
    driver = None

    try:
        driver = setup_driver()
        all_reports = parse_reports_page(driver)
        reports_to_download = filter_reports(all_reports)

        if not reports_to_download:
            print("\nWARNING: No reports match filter criteria")
            print("Check config.py TARGET_YEAR and REPORT_TYPES settings")
            return

        downloaded = download_reports(driver, reports_to_download)

        print(f"\n{'='*80}")
        print("SCRAPER COMPLETED")
        print(f"{'='*80}")
        print(f"OK Downloaded {len(downloaded)} reports")
        print(f"OK Location: {download_dir}")
        print(f"{'='*80}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
