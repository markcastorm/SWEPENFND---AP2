"""
AP2 Orchestrator
Main entry point that coordinates scraper and parser execution.
"""

import os
import sys
import logging
from datetime import datetime
import subprocess

# Create directories if they don't exist
os.makedirs('downloads', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('output', exist_ok=True)

# Setup logging with timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/orchestrator_{timestamp}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_script(script_name, description):
    """
    Run a Python script and capture its output.

    Args:
        script_name: Name of the Python script to run
        description: Description of what the script does

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("=" * 80)
    logger.info(f"Starting: {description}")
    logger.info("=" * 80)

    try:
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=False
        )

        # Log the output
        if result.stdout:
            for line in result.stdout.splitlines():
                logger.info(f"[{script_name}] {line}")

        if result.stderr:
            for line in result.stderr.splitlines():
                # Filter out common warnings
                if 'UserWarning' not in line and 'warn(' not in line:
                    logger.warning(f"[{script_name}] {line}")

        # Check return code
        if result.returncode != 0:
            logger.error(f"{script_name} failed with return code {result.returncode}")
            return False

        logger.info(f"OK {description} completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error running {script_name}: {e}")
        return False


def main():
    """Main orchestration function."""
    logger.info("=" * 80)
    logger.info("AP2 Data Pipeline Orchestrator")
    logger.info(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)

    start_time = datetime.now()

    # Step 1: Run Scraper
    logger.info("\n[STEP 1/2] Running Web Scraper...")
    scraper_success = run_script('ap2_scraper.py', 'Web Scraper (Download PDFs)')

    if not scraper_success:
        logger.error("=" * 80)
        logger.error("Pipeline failed at Step 1: Web Scraper")
        logger.error("=" * 80)
        sys.exit(1)

    # Step 2: Run Parser
    logger.info("\n[STEP 2/2] Running Enhanced PDF Parser...")
    parser_success = run_script('pdf_parser_enhanced.py', 'Enhanced PDF Parser (Table Extraction)')

    if not parser_success:
        logger.error("=" * 80)
        logger.error("Pipeline failed at Step 2: PDF Parser")
        logger.error("=" * 80)
        sys.exit(1)

    # Success
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("\n" + "=" * 80)
    logger.info("OK PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"Total execution time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
    logger.info(f"Output file: output/latest/AP2_Financial_Data_latest.xlsx")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}")
        sys.exit(1)
