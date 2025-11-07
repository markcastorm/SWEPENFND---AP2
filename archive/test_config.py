"""
Configuration Test Script
Run this to verify your configuration is correct before running the scraper
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    required_packages = [
        ('selenium', 'selenium'),
        ('undetected_chromedriver', 'undetected-chromedriver'),
        ('bs4', 'beautifulsoup4'),
        ('pdfplumber', 'pdfplumber'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
    ]

    missing = []
    for module, package in required_packages:
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    else:
        print("\n✓ All required packages installed")
        return True

def test_config():
    """Test configuration file"""
    print("\nTesting configuration...")

    try:
        import config
        print("  ✓ config.py imported successfully")

        # Test headers
        if len(config.OUTPUT_HEADERS) == 21:
            print(f"  ✓ OUTPUT_HEADERS has correct length (21)")
        else:
            print(f"  ✗ OUTPUT_HEADERS has incorrect length ({len(config.OUTPUT_HEADERS)} instead of 21)")
            return False

        # Test target year
        if config.TARGET_YEAR == "latest" or isinstance(config.TARGET_YEAR, int):
            print(f"  ✓ TARGET_YEAR is valid ({config.TARGET_YEAR})")
        else:
            print(f"  ✗ TARGET_YEAR is invalid ({config.TARGET_YEAR})")
            return False

        # Test report types
        enabled_types = [k for k, v in config.REPORT_TYPES.items() if v]
        if enabled_types:
            print(f"  ✓ Report types enabled: {', '.join(enabled_types)}")
        else:
            print(f"  ✗ No report types enabled")
            return False

        # Test folders
        print(f"  ✓ Logs folder: {config.LOGS_DIR}")
        print(f"  ✓ Downloads folder: {config.DOWNLOADS_DIR}")
        print(f"  ✓ Output folder: {config.OUTPUT_DIR}")

        return True

    except Exception as e:
        print(f"  ✗ Error loading config: {str(e)}")
        return False

def test_modules():
    """Test if custom modules can be imported"""
    print("\nTesting custom modules...")

    try:
        import pdf_parser
        print("  ✓ pdf_parser.py")
    except Exception as e:
        print(f"  ✗ pdf_parser.py - {str(e)}")
        return False

    try:
        import ap2_scraper
        print("  ✓ ap2_scraper.py")
    except Exception as e:
        print(f"  ✗ ap2_scraper.py - {str(e)}")
        return False

    return True

def test_chrome():
    """Test if Chrome can be launched"""
    print("\nTesting Chrome driver...")

    try:
        import undetected_chromedriver as uc
        driver = uc.Chrome(headless=True)
        driver.quit()
        print("  ✓ Chrome driver works")
        return True
    except Exception as e:
        print(f"  ✗ Chrome driver error: {str(e)}")
        print("     Make sure Chrome browser is installed")
        return False

def test_folders():
    """Test folder creation"""
    print("\nTesting folder creation...")

    try:
        import config
        folders = config.get_run_folders()
        config.create_run_folders(folders['timestamp'])

        for name, path in folders.items():
            if name == 'timestamp':
                continue
            if os.path.exists(path):
                print(f"  ✓ {name}: {path}")
            else:
                print(f"  ✗ {name}: {path} - Failed to create")
                return False

        # Clean up test folders
        import shutil
        for name, path in folders.items():
            if name == 'timestamp':
                continue
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                except:
                    pass

        return True

    except Exception as e:
        print(f"  ✗ Error creating folders: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("AP2 SCRAPER - CONFIGURATION TEST")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Config Test", test_config()))
    results.append(("Module Test", test_modules()))
    results.append(("Folder Test", test_folders()))
    results.append(("Chrome Test", test_chrome()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:.<30} {status}")

    all_passed = all(passed for _, passed in results)

    print("=" * 80)
    if all_passed:
        print("✓ ALL TESTS PASSED - Ready to run scraper!")
        print("\nRun the scraper with:")
        print("  python ap2_scraper.py")
    else:
        print("✗ SOME TESTS FAILED - Fix issues before running scraper")
        print("\nCheck the errors above and:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Verify config.py settings")
        print("  3. Make sure Chrome browser is installed")
    print("=" * 80)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
