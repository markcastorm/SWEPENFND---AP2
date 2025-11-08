"""
LLM-based PDF Field Extractor
Uses OpenRouter API with free models for robust extraction when Camelot/Regex fail
Zero cost using deepseek/deepseek-chat-v3.1 or other free models
"""
import os
import json
import logging
import requests
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extract fields using LLM when traditional methods fail"""

    def __init__(self):
        """Initialize LLM extractor with OpenRouter API"""
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('LLM_MODEL', 'deepseek/deepseek-chat-v3.1')
        self.enabled = os.getenv('ENABLE_LLM_FALLBACK', 'true').lower() == 'true'

        if not self.api_key:
            logger.warning("  [WARNING] OPENROUTER_API_KEY not found in .env file")
            logger.warning("  [WARNING] LLM fallback will be disabled")
            self.enabled = False

        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def extract_balance_sheet(self, text: str) -> Dict[str, float]:
        """
        Extract all 17 Balance Sheet fields using LLM

        Args:
            text: Raw text from Balance Sheet page

        Returns:
            Dict with extracted fields (in SEK million, NOT billions)
        """
        if not self.enabled:
            logger.debug("  LLM extraction disabled (no API key or disabled in .env)")
            return {}

        prompt = f"""Extract the following 17 Balance Sheet fields from this Swedish pension fund report text. Return ONLY a JSON object with these exact field names and their numeric values (in SEK million):

Required fields:
- EQUITIESANDPARTICIPATIONSLISTED (Listed shares)
- EQUITIESANDPARTICIPATIONSUNLISTED (Unlisted shares)
- BONDSANDOTHERFIXEDINCOMESECURITIES (Bonds and other interest-bearing securities)
- DERIVATIVEINSTRUMENTS (Derivative instruments - assets side)
- CASHANDBANKBALANCES (Cash and cash equivalents)
- OTHERASSETS
- PREPAIDEXPENSESANDACCRUEDINCOME (Prepaid expenses and accrued income)
- TOTALASSETS
- DERIVATIVEINSTRUMENTSLIABILITIES (Derivative instruments - liabilities side)
- OTHERLIABILITIES
- DEFERREDINCOMEANDACCRUEDEXPENSES (Deferred income and accrued expenses)
- TOTALLIABILITIES
- FUNDCAPITALCARRIEDFORWARD (Fund capital carried forward/brought forward)
- NETPAYMENTSTOTHENATIONALPENSIONSYSTEM (Net payments to/from pension system)
- NETRESULTFORTHEPERIOD (Net result for the period)
- TOTALFUNDCAPITAL
- TOTALFUNDCAPITALANDLIABILITIES

IMPORTANT NOTES:
1. "Derivative instruments" appears TWICE - once in Assets section and once in Liabilities section. Use the correct one for each field.
2. Keep values in SEK MILLION (do NOT convert to billions)
3. Preserve negative signs (e.g., net payments may be negative)
4. Return ONLY valid JSON, no markdown, no explanations

TEXT TO EXTRACT FROM:
{text}"""

        try:
            response = self._call_llm(prompt)
            data = json.loads(response)

            # Convert to integers (values are in millions)
            result = {}
            for key, value in data.items():
                try:
                    # Handle both float and int values, preserve sign
                    result[key] = int(float(value)) if value is not None else None
                except (ValueError, TypeError):
                    logger.warning(f"  [WARNING] Could not convert {key}={value} to number")
                    continue

            logger.info(f"  [LLM] Extracted {len(result)}/17 Balance Sheet fields")
            return result

        except Exception as e:
            logger.error(f"  [LLM ERROR] Balance Sheet extraction failed: {e}")
            return {}

    def extract_key_ratios(self, text: str) -> Dict[str, float]:
        """
        Extract 3 Key Ratios fields using LLM

        Args:
            text: Raw text from Key Ratios page

        Returns:
            Dict with extracted fields (in SEK billion)
        """
        if not self.enabled:
            logger.debug("  LLM extraction disabled (no API key or disabled in .env)")
            return {}

        prompt = f"""You are extracting financial data from a Swedish pension fund report. The report may contain tables with multiple columns showing different time periods.

STEP 1: Identify the table structure
- Look for column headers indicating time periods (e.g., "Jan.-June 2020", "Jan.-June 2019", "Jan.-Dec. 2019")
- The FIRST column (leftmost) after the row labels contains the CURRENT PERIOD data
- Other columns are comparison data from PREVIOUS periods - IGNORE THESE

STEP 2: Extract these 3 fields (return as JSON):
- FUNDCAPITALCARRIEDFORWARDLEVEL: Look for "Fund capital carried forward" (preferred) or "Fund capital brought forward". Extract the FIRST numeric value that appears after this label.
- NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM: Look for "Net outflows to the national pension system". Extract the FIRST numeric value (may be negative).
- TOTAL: Look for "Net result for the period" or "Net result for the year". Extract the FIRST numeric value (may be negative).

STEP 3: Format rules
- All values must be in SEK BILLION
- Preserve negative signs (e.g., -4.2 not 4.2)
- Return ONLY a valid JSON object like: {{"FUNDCAPITALCARRIEDFORWARDLEVEL": 357.9, "NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM": -4.2, "TOTAL": -19.3}}

CRITICAL: When you see multiple numbers after a field name, take the FIRST one (current period), not subsequent ones (comparison periods).

Example from text:
"Fund capital carried forward, SEK billion
357.9    367.4    381.3"
→ Extract: 357.9 (first value = current period)
NOT 381.3 (third value = old comparison period)

TEXT TO EXTRACT FROM:
{text}"""

        try:
            response = self._call_llm(prompt)
            data = json.loads(response)

            # Convert to float (values are in billions)
            result = {}
            for key, value in data.items():
                try:
                    result[key] = float(value) if value is not None else None
                except (ValueError, TypeError):
                    logger.warning(f"  [WARNING] Could not convert {key}={value} to number")
                    continue

            logger.info(f"  [LLM] Extracted {len(result)}/3 Key Ratios fields")
            return result

        except Exception as e:
            logger.error(f"  [LLM ERROR] Key Ratios extraction failed: {e}")
            return {}

    def _call_llm(self, prompt: str) -> str:
        """
        Call OpenRouter API with the given prompt

        Args:
            prompt: User prompt for extraction

        Returns:
            Raw text response from LLM
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yourusername/ap2-scraper",
            "X-Title": "AP2 PDF Parser"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.0  # Deterministic for data extraction
        }

        logger.debug(f"  [LLM] Calling {self.model} via OpenRouter...")

        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()
        content = result['choices'][0]['message']['content']

        # Remove markdown code blocks if present
        content = content.replace('```json', '').replace('```', '').strip()

        # Extract JSON from response (in case model adds extra text)
        # Look for first { and last }
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx+1]

        return content


def extract_balance_sheet_llm(pdf_path: str, page_num: int) -> Dict[str, float]:
    """
    Extract Balance Sheet using LLM fallback

    Args:
        pdf_path: Path to PDF file
        page_num: Page number containing Balance Sheet (1-indexed)

    Returns:
        Dict with extracted Balance Sheet fields
    """
    import fitz

    logger.info("  [LLM FALLBACK] Attempting LLM-based Balance Sheet extraction...")

    # Extract text from page
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]  # 0-indexed
    text = page.get_text()
    doc.close()

    # Use LLM to extract
    extractor = LLMExtractor()
    return extractor.extract_balance_sheet(text)


def extract_key_ratios_llm(pdf_path: str, page_num: int) -> Dict[str, float]:
    """
    Extract Key Ratios using LLM fallback

    Args:
        pdf_path: Path to PDF file
        page_num: Page number containing Key Ratios (1-indexed)

    Returns:
        Dict with extracted Key Ratios fields
    """
    import fitz

    logger.info("  [LLM FALLBACK] Attempting LLM-based Key Ratios extraction...")

    # Extract text from page
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]  # 0-indexed
    text = page.get_text()
    doc.close()

    # Use LLM to extract
    extractor = LLMExtractor()
    return extractor.extract_key_ratios(text)


if __name__ == "__main__":
    # Test LLM extractor
    import sys
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    pdf_path = "downloads/20251107_142545/AP2_2025_half_year.pdf"

    print("="*80)
    print("LLM EXTRACTOR TEST - 2025 PDF")
    print("="*80)

    # Test Balance Sheet
    print("\n[TEST 1] Balance Sheet Extraction")
    data = extract_balance_sheet_llm(pdf_path, page_num=6)
    print(f"\nExtracted {len(data)}/17 fields:")
    for field, value in data.items():
        print(f"  {field}: {value:,}")

    # Test Key Ratios
    print("\n" + "="*80)
    print("[TEST 2] Key Ratios Extraction")
    data = extract_key_ratios_llm(pdf_path, page_num=3)
    print(f"\nExtracted {len(data)}/3 fields:")
    for field, value in data.items():
        print(f"  {field}: {value}")
