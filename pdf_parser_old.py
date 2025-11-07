"""
PDF Parser Module for AP2 Financial Reports
Extracts and parses financial tables from PDF reports
"""

import os
import re
import pandas as pd
import pdfplumber
import logging
from typing import List, Dict, Optional

import config


class PDFParser:
    """Parser for extracting financial data from PDF reports"""

    def __init__(self, logger=None):
        """Initialize the PDF parser"""
        self.logger = logger or logging.getLogger('PDFParser')

    def extract_tables_from_pdf(self, pdf_path: str) -> List[pd.DataFrame]:
        """
        Extract all tables from a PDF file using pdfplumber

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of DataFrames containing extracted tables
        """
        tables = []

        try:
            self.logger.debug(f"Opening PDF: {pdf_path}")

            with pdfplumber.open(pdf_path) as pdf:
                self.logger.debug(f"PDF has {len(pdf.pages)} pages")

                for page_num, page in enumerate(pdf.pages, 1):
                    self.logger.debug(f"Processing page {page_num}/{len(pdf.pages)}")

                    # Extract tables from page
                    page_tables = page.extract_tables()

                    if page_tables:
                        self.logger.debug(f"Found {len(page_tables)} tables on page {page_num}")

                        for table_num, table_data in enumerate(page_tables, 1):
                            if table_data and len(table_data) > 1:  # At least header + 1 data row
                                # Convert to DataFrame
                                df = pd.DataFrame(table_data[1:], columns=table_data[0])

                                # Clean the DataFrame
                                df = self._clean_table(df)

                                if not df.empty:
                                    # Check if table contains financial data
                                    if self._is_financial_table(df):
                                        tables.append({
                                            'page': page_num,
                                            'table_num': table_num,
                                            'data': df
                                        })
                                        self.logger.debug(f"Added financial table from page {page_num}, table {table_num}")

            self.logger.info(f"Extracted {len(tables)} financial tables from PDF")

        except Exception as e:
            self.logger.error(f"Error extracting tables from PDF: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())

        return tables

    def _clean_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean extracted table data"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all').reset_index(drop=True)
        df = df.dropna(axis=1, how='all')

        # Replace None with empty string
        df = df.fillna('')

        # Strip whitespace from all cells
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Remove rows where all values are empty strings
        df = df[~(df == '').all(axis=1)].reset_index(drop=True)

        return df

    def _is_financial_table(self, df: pd.DataFrame) -> bool:
        """
        Check if a table contains financial data based on keywords and structure

        Args:
            df: DataFrame to check

        Returns:
            Boolean indicating if this is a financial table
        """
        # Convert all content to lowercase string for searching
        table_text = ' '.join(df.astype(str).values.flatten()).lower()

        # Check for financial keywords
        financial_keywords = [
            'assets', 'liabilities', 'fund capital', 'balance sheet',
            'equity', 'bonds', 'derivatives', 'cash', 'securities',
            'income', 'expenses', 'result', 'total assets', 'total liabilities',
            'financial position', 'statement', 'investments'
        ]

        keyword_matches = sum(1 for keyword in financial_keywords if keyword in table_text)

        # Require at least 3 keyword matches
        if keyword_matches >= 3:
            return True

        # Check for numeric data (financial tables should have numbers)
        numeric_pattern = re.compile(r'\d+[\d,.\s]*\d*')
        numeric_cells = df.applymap(lambda x: bool(numeric_pattern.search(str(x))))
        numeric_ratio = numeric_cells.sum().sum() / (df.shape[0] * df.shape[1])

        # If more than 30% of cells contain numbers and at least 1 keyword match
        if numeric_ratio > 0.3 and keyword_matches >= 1:
            return True

        return False

    def _extract_numeric_value(self, value: str) -> Optional[float]:
        """
        Extract numeric value from string, handling various formats

        Args:
            value: String containing numeric value

        Returns:
            Float value or None if cannot be parsed
        """
        if not value or not isinstance(value, str):
            return None

        # Remove common non-numeric characters but keep decimal separators
        # Handle formats like: 450,002 or 450.002 or 450 002
        cleaned = re.sub(r'[^\d.,\-]', '', value.strip())

        if not cleaned:
            return None

        try:
            # Handle European format (space or comma as thousand separator)
            # and convert to standard format
            cleaned = cleaned.replace(' ', '')

            # Determine if comma is decimal or thousand separator
            # If there's a period after comma, comma is thousand separator
            if ',' in cleaned and '.' in cleaned:
                if cleaned.rindex(',') < cleaned.rindex('.'):
                    # Format: 1,234.56 (US format)
                    cleaned = cleaned.replace(',', '')
                else:
                    # Format: 1.234,56 (EU format)
                    cleaned = cleaned.replace('.', '').replace(',', '.')
            elif ',' in cleaned:
                # Only comma - could be decimal or thousand separator
                # If comma is followed by exactly 3 digits and nothing else, it's thousand separator
                if re.match(r'^[\d,]+,\d{3}$', cleaned):
                    cleaned = cleaned.replace(',', '')
                else:
                    # Assume it's decimal separator
                    cleaned = cleaned.replace(',', '.')

            return float(cleaned)

        except (ValueError, AttributeError):
            return None

    def _find_balance_sheet_data(self, tables: List[Dict]) -> Optional[Dict]:
        """
        Find and extract balance sheet data from tables

        Args:
            tables: List of table dictionaries from PDF

        Returns:
            Dictionary with extracted financial data
        """
        balance_sheet_keywords = [
            'balance sheet', 'statement of financial position',
            'assets and liabilities', 'balance'
        ]

        for table in tables:
            df = table['data']
            table_text = ' '.join(df.astype(str).values.flatten()).lower()

            # Check if this is a balance sheet
            if any(keyword in table_text for keyword in balance_sheet_keywords):
                self.logger.info(f"Found balance sheet on page {table['page']}")

                # Try to extract data
                extracted_data = self._extract_financial_values(df)

                if extracted_data:
                    return extracted_data

        return None

    def _extract_financial_values(self, df: pd.DataFrame) -> Dict:
        """
        Extract financial values from a DataFrame

        Args:
            df: DataFrame containing financial data

        Returns:
            Dictionary mapping field names to values
        """
        extracted = {}

        # Common patterns to match against our required fields
        field_patterns = {
            'EQUITIESANDPARTICIPATIONSLISTED': [
                'equities.*listed', 'listed.*equities', 'listed.*shares',
                'quoted.*equities', 'publicly.*traded.*equities'
            ],
            'EQUITIESANDPARTICIPATIONSUNLISTED': [
                'equities.*unlisted', 'unlisted.*equities', 'private.*equities',
                'unquoted.*equities'
            ],
            'BONDSANDOTHERFIXEDINCOMESECURITIES': [
                'bonds', 'fixed.*income', 'debt.*securities', 'interest.*bearing.*securities'
            ],
            'DERIVATIVEINSTRUMENTS': [
                'derivatives', 'derivative.*instruments', 'financial.*derivatives'
            ],
            'CASHANDBANKBALANCES': [
                'cash', 'bank.*balances', 'cash.*equivalents', 'liquid.*assets'
            ],
            'OTHERASSETS': [
                'other.*assets'
            ],
            'PREPAIDEXPENSESANDACCRUEDINCOME': [
                'prepaid.*expenses', 'accrued.*income', 'prepaid.*accrued'
            ],
            'TOTALASSETS': [
                'total.*assets', 'assets.*total'
            ],
            'DERIVATIVEINSTRUMENTSLIABILITIES': [
                'derivative.*liabilities', 'derivatives.*liabilities'
            ],
            'OTHERLIABILITIES': [
                'other.*liabilities'
            ],
            'DEFERREDINCOMEANDACCRUEDEXPENSES': [
                'deferred.*income', 'accrued.*expenses', 'deferred.*accrued'
            ],
            'TOTALLIABILITIES': [
                'total.*liabilities', 'liabilities.*total'
            ],
            'FUNDCAPITALCARRIEDFORWARD': [
                'fund.*capital.*carried.*forward', 'opening.*fund.*capital',
                'carried.*forward'
            ],
            'NETPAYMENTSTOTHENATIONALPENSIONSYSTEM': [
                'net.*payments.*pension', 'pension.*system.*payments',
                'net.*outflows.*pension', 'net.*pension'
            ],
            'NETRESULTFORTHEPERIOD': [
                'net.*result', 'result.*period', 'profit.*loss', 'net.*income'
            ],
            'TOTALFUNDCAPITAL': [
                'total.*fund.*capital', 'fund.*capital.*total', 'net.*assets'
            ],
        }

        # Search for each field in the table
        for field_key, patterns in field_patterns.items():
            for _, row in df.iterrows():
                row_text = ' '.join(str(cell) for cell in row.values).lower()

                # Check if any pattern matches
                for pattern in patterns:
                    if re.search(pattern, row_text):
                        # Try to extract numeric value from this row
                        for cell in row.values:
                            value = self._extract_numeric_value(str(cell))
                            if value is not None:
                                extracted[field_key] = value
                                self.logger.debug(f"Extracted {field_key}: {value}")
                                break
                        break

                if field_key in extracted:
                    break

        return extracted

    def map_to_output_format(self, tables: List[Dict], year: int, report_type: str) -> Dict:
        """
        Map extracted table data to the output format

        Args:
            tables: List of extracted tables
            year: Year of the report
            report_type: Type of report (annual, half_year, etc.)

        Returns:
            Dictionary with data mapped to output headers
        """
        self.logger.info(f"Mapping data for year {year}, report type: {report_type}")

        # Initialize output with empty values
        output = {header: None for header in config.OUTPUT_HEADERS}

        # Set the year in the first column
        output['Unnamed: 0'] = year

        # Try to find balance sheet data
        financial_data = self._find_balance_sheet_data(tables)

        if financial_data:
            self.logger.info(f"Found {len(financial_data)} financial values")

            # Map extracted data to output headers
            for field_key, value in financial_data.items():
                # Find the matching header
                for header in config.OUTPUT_HEADERS:
                    if field_key in header:
                        output[header] = value
                        break
        else:
            self.logger.warning("Could not find balance sheet data in tables")

            # Fallback: try to extract data from all tables
            all_data = {}
            for table in tables:
                extracted = self._extract_financial_values(table['data'])
                all_data.update(extracted)

            if all_data:
                self.logger.info(f"Extracted {len(all_data)} values from all tables")
                for field_key, value in all_data.items():
                    for header in config.OUTPUT_HEADERS:
                        if field_key in header:
                            output[header] = value
                            break

        # Log which fields were successfully mapped
        mapped_count = sum(1 for v in output.values() if v is not None) - 1  # -1 for year
        self.logger.info(f"Successfully mapped {mapped_count} out of {len(config.OUTPUT_HEADERS) - 1} fields")

        return output

    def debug_print_tables(self, tables: List[Dict], max_rows: int = 10):
        """
        Print tables for debugging purposes

        Args:
            tables: List of tables to print
            max_rows: Maximum rows to display per table
        """
        for i, table in enumerate(tables, 1):
            self.logger.debug(f"\n{'=' * 80}")
            self.logger.debug(f"Table {i} (Page {table['page']}, Table {table['table_num']})")
            self.logger.debug(f"{'=' * 80}")
            self.logger.debug(f"\n{table['data'].head(max_rows).to_string()}")
            self.logger.debug(f"\nShape: {table['data'].shape}")
