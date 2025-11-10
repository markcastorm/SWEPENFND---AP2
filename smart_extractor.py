"""
Smart Keyword + Proximity Extractor
Uses PyMuPDF to extract text with coordinates and find numbers near keywords
Zero external API costs, pure Python libraries
"""
import fitz
import re
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SmartExtractor:
    """Extract fields using keyword proximity scoring"""

    # Field definitions with multiple synonym keywords
    # IMPORTANT: Order matters! More specific keywords first
    FIELD_KEYWORDS = {
        'FUNDCAPITALCARRIEDFORWARDLEVEL': [
            'fund capital brought forward',  # Opening balance (preferred)
            'opening fund capital',
            'fund capital at start',
            # 'fund capital carried forward',  # Closing balance (skip to avoid confusion)
        ],
        'NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM': [
            'net outflow',
            'net outflows',
            'net flow to pension',
            'pension system',
            'national pension system',
        ],
        'TOTAL': [
            'result amounted to sek',  # Most specific
            'net result for the period',
            'net result for the year',
            'result for the period, sek billion',
            'result for the year, sek billion',
        ],
    }

    # Expected value ranges for validation (in billions SEK)
    VALUE_RANGES = {
        'FUNDCAPITALCARRIEDFORWARDLEVEL': (300, 600),  # Fund typically 300-600B
        'NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM': (-10, 0),  # Outflows are negative
        'TOTAL': (-50, 50),  # Result can be -50 to +50B
    }

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def extract_from_page(self, page_num: int, field_name: str) -> Optional[float]:
        """
        Extract a specific field from a page using smart proximity matching

        Args:
            page_num: Page number (1-indexed)
            field_name: Field key from FIELD_KEYWORDS

        Returns:
            Extracted value or None
        """
        doc = fitz.open(self.pdf_path)
        page = doc[page_num - 1]  # 0-indexed

        # Get keywords for this field
        keywords = self.FIELD_KEYWORDS.get(field_name, [])
        if not keywords:
            logger.warning(f"No keywords defined for {field_name}")
            doc.close()
            return None

        # Extract text blocks with coordinates
        blocks = page.get_text("dict")["blocks"]

        # Find all numbers on the page with their positions
        numbers = self._extract_numbers_with_positions(blocks)

        # Find keyword matches with their positions
        keyword_positions = self._find_keyword_positions(blocks, keywords)

        if not keyword_positions:
            logger.debug(f"  No keywords found for {field_name}")
            doc.close()
            return None

        # Score each number based on proximity to keywords
        candidates = []
        for keyword_pos in keyword_positions:
            for num_value, num_pos in numbers:
                distance = self._calculate_distance(keyword_pos, num_pos)
                score = self._calculate_score(num_value, field_name, distance, keyword_pos['keyword'])

                if score > 0:
                    candidates.append({
                        'value': num_value,
                        'score': score,
                        'distance': distance,
                        'keyword': keyword_pos['keyword']
                    })

                    # Debug: Log all candidates
                    logger.debug(f"      Candidate: {num_value} near '{keyword_pos['keyword']}' (dist: {distance:.0f}, score: {score:.1f})")

        doc.close()

        if not candidates:
            logger.debug(f"  No valid candidates for {field_name}")
            return None

        # Sort by score and return best match
        best = max(candidates, key=lambda x: x['score'])
        logger.info(f"    [OK] {field_name}: {best['value']} (score: {best['score']:.1f}, keyword: '{best['keyword']}')")

        return best['value']

    def _extract_numbers_with_positions(self, blocks: List) -> List[Tuple[float, Dict]]:
        """Extract all numbers from text blocks with their positions"""
        numbers = []

        for block in blocks:
            if block.get("type") != 0:  # Skip non-text blocks
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    bbox = span.get("bbox", [0, 0, 0, 0])

                    # Find numbers (including decimals and negatives)
                    # Match: 407.1, -2.6, 19.4, etc.
                    matches = re.finditer(r'-?\d+\.?\d*', text)

                    for match in matches:
                        try:
                            value = float(match.group())

                            # Filter out obviously wrong values
                            if abs(value) > 0.01 and abs(value) < 10000:
                                numbers.append((value, {
                                    'x': bbox[0],
                                    'y': bbox[1],
                                    'text': text,
                                    'bbox': bbox
                                }))
                        except ValueError:
                            continue

        return numbers

    def _find_keyword_positions(self, blocks: List, keywords: List[str]) -> List[Dict]:
        """Find positions of keyword matches"""
        positions = []

        for block in blocks:
            if block.get("type") != 0:
                continue

            for line in block.get("lines", []):
                line_text = ""
                line_bbox = None

                # Concatenate spans into full line text
                for span in line.get("spans", []):
                    line_text += span.get("text", "") + " "
                    if line_bbox is None:
                        line_bbox = list(span.get("bbox", [0, 0, 0, 0]))
                    else:
                        # Extend bbox to cover full line
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        line_bbox[2] = max(line_bbox[2], bbox[2])
                        line_bbox[3] = max(line_bbox[3], bbox[3])

                line_text = line_text.lower().strip()

                # Check if any keyword matches
                for keyword in keywords:
                    if keyword.lower() in line_text:
                        positions.append({
                            'keyword': keyword,
                            'x': line_bbox[0],
                            'y': line_bbox[1],
                            'text': line_text,
                            'bbox': line_bbox
                        })

        return positions

    def _calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """Calculate Euclidean distance between two positions"""
        dx = pos1['x'] - pos2['x']
        dy = pos1['y'] - pos2['y']
        return (dx**2 + dy**2) ** 0.5

    def _calculate_score(self, value: float, field_name: str, distance: float, keyword: str) -> float:
        """
        Calculate score for a number based on:
        1. Proximity to keyword (closer = better)
        2. Value range validation (in expected range = better)
        3. Keyword quality (better keywords = higher score)
        4. Context validation (billion qualifier, avoid percentages)
        """
        score = 0

        # Proximity score (max 50 points)
        # Closer numbers score higher
        if distance < 50:
            score += 50
        elif distance < 100:
            score += 40
        elif distance < 200:
            score += 30
        elif distance < 300:
            score += 20
        elif distance < 500:
            score += 10
        else:
            return 0  # Too far away

        # Value range validation (max 40 points - increased importance)
        expected_range = self.VALUE_RANGES.get(field_name)
        if expected_range:
            min_val, max_val = expected_range
            if min_val <= value <= max_val:
                score += 40  # Perfect range match
            elif min_val * 0.5 <= value <= max_val * 1.5:
                # Within 50% margin
                score += 15
            else:
                # Out of range - heavily penalize
                score -= 50  # Stronger penalty

        # Keyword quality score (max 20 points)
        # More specific keywords get higher scores
        if 'brought forward' in keyword:
            score += 25  # Prefer opening balance
        elif 'result amounted to sek' in keyword:
            score += 25  # Very specific
        elif 'outflow' in keyword:
            score += 20
        elif 'fund capital' in keyword:
            score += 15
        elif 'result' in keyword:
            score += 15
        else:
            score += 10

        return max(0, score)  # Don't return negative scores


def extract_key_ratios_smart(pdf_path: str, key_ratios_page: int) -> Dict:
    """
    Extract Key Ratios using smart keyword proximity matching

    Args:
        pdf_path: Path to PDF file
        key_ratios_page: Page number containing Key Ratios (1-indexed)

    Returns:
        Dict with extracted fields
    """
    logger.info("  Extracting Key Ratios using smart extractor...")

    extractor = SmartExtractor(pdf_path)
    data = {}

    # Extract each field
    for field_name in SmartExtractor.FIELD_KEYWORDS.keys():
        value = extractor.extract_from_page(key_ratios_page, field_name)
        if value is not None:
            data[field_name] = value

    logger.info(f"    [INFO] Smart extractor found {len(data)}/3 fields")
    return data


if __name__ == "__main__":
    # Test on 2023 PDF
    import sys
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    pdf_path = "downloads/20251107_171033/AP2_2023_half_year.pdf"

    print("="*80)
    print("SMART EXTRACTOR TEST - 2023 PDF")
    print("="*80)

    data = extract_key_ratios_smart(pdf_path, key_ratios_page=2)

    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"Extracted {len(data)}/3 fields:")
    for field, value in data.items():
        print(f"  {field}: {value}")
