"""
Test LLM Integration with Working DeepSeek Model
Tests the llm_extractor with deepseek/deepseek-r1:free (confirmed working)
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_extractor import LLMExtractor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Sample Balance Sheet text (simplified Swedish pension fund format)
SAMPLE_BALANCE_SHEET = """
BALANCE SHEET
as at 30 June 2020

ASSETS                                          SEK million
Equities and participations, listed             245,678
Equities and participations, unlisted            89,432
Bonds and other fixed-income securities         123,456
Derivative instruments                           12,345
Cash and bank balances                            8,765
Other assets                                      5,432
Prepaid expenses and accrued income               2,109
TOTAL ASSETS                                    487,217

LIABILITIES
Derivative instruments                           15,678
Other liabilities                                 3,456
Deferred income and accrued expenses              1,234
TOTAL LIABILITIES                                20,368

FUND CAPITAL
Fund capital carried forward                    450,123
Net payments to the national pension system      -5,432
Net result for the period                        22,158
TOTAL FUND CAPITAL                              466,849
TOTAL FUND CAPITAL AND LIABILITIES              487,217
"""

# Sample Key Ratios text
SAMPLE_KEY_RATIOS = """
KEY RATIOS
                                        Jan.-June 2020  Jan.-June 2019  Jan.-Dec. 2019
Fund capital carried forward, SEK bn        450.1          425.3          425.3
Net outflows to pension system, SEK bn       -5.4           -6.2          -11.8
Net result for the period, SEK bn            22.2          -18.5            36.6
"""


def test_balance_sheet_extraction():
    """Test Balance Sheet extraction with working model"""
    print("=" * 80)
    print("TEST 1: Balance Sheet Extraction")
    print("=" * 80)

    # Override model to use working one
    os.environ['LLM_MODEL'] = 'deepseek/deepseek-r1:free'

    extractor = LLMExtractor()

    if not extractor.enabled:
        print("❌ LLM extractor is disabled!")
        print("   Make sure OPENROUTER_API_KEY is set in your .env file")
        return False

    print(f"✓ Using model: {extractor.model}")
    print(f"✓ API key found: {extractor.api_key[:20]}...")
    print("\nExtracting Balance Sheet fields...")

    try:
        result = extractor.extract_balance_sheet(SAMPLE_BALANCE_SHEET)

        if not result:
            print("❌ No fields extracted!")
            return False

        print(f"\n✅ Successfully extracted {len(result)}/17 fields:")
        expected_fields = [
            'EQUITIESANDPARTICIPATIONSLISTED',
            'EQUITIESANDPARTICIPATIONSUNLISTED',
            'BONDSANDOTHERFIXEDINCOMESECURITIES',
            'DERIVATIVEINSTRUMENTS',
            'CASHANDBANKBALANCES',
            'OTHERASSETS',
            'PREPAIDEXPENSESANDACCRUEDINCOME',
            'TOTALASSETS',
            'DERIVATIVEINSTRUMENTSLIABILITIES',
            'OTHERLIABILITIES',
            'DEFERREDINCOMEANDACCRUEDEXPENSES',
            'TOTALLIABILITIES',
            'FUNDCAPITALCARRIEDFORWARD',
            'NETPAYMENTSTOTHENATIONALPENSIONSYSTEM',
            'NETRESULTFORTHEPERIOD',
            'TOTALFUNDCAPITAL',
            'TOTALFUNDCAPITALANDLIABILITIES'
        ]

        for field in expected_fields:
            if field in result:
                print(f"  ✓ {field}: {result[field]:,}")
            else:
                print(f"  ✗ {field}: MISSING")

        return len(result) >= 10  # At least 10/17 fields

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_key_ratios_extraction():
    """Test Key Ratios extraction with working model"""
    print("\n" + "=" * 80)
    print("TEST 2: Key Ratios Extraction")
    print("=" * 80)

    # Override model to use working one
    os.environ['LLM_MODEL'] = 'deepseek/deepseek-r1:free'

    extractor = LLMExtractor()

    if not extractor.enabled:
        print("❌ LLM extractor is disabled!")
        return False

    print(f"✓ Using model: {extractor.model}")
    print("\nExtracting Key Ratios fields...")

    try:
        result = extractor.extract_key_ratios(SAMPLE_KEY_RATIOS)

        if not result:
            print("❌ No fields extracted!")
            return False

        print(f"\n✅ Successfully extracted {len(result)}/3 fields:")
        expected_fields = [
            'FUNDCAPITALCARRIEDFORWARDLEVEL',
            'NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM',
            'TOTAL'
        ]

        for field in expected_fields:
            if field in result:
                print(f"  ✓ {field}: {result[field]}")
            else:
                print(f"  ✗ {field}: MISSING")

        return len(result) >= 2  # At least 2/3 fields

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("LLM INTEGRATION TEST SUITE")
    print("Testing with deepseek/deepseek-r1:free (confirmed working)")
    print("=" * 80 + "\n")

    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in .env file!")
        print("   Please add it to your .env file")
        return

    results = []

    # Test Balance Sheet
    test1 = test_balance_sheet_extraction()
    results.append(("Balance Sheet", test1))

    # Test Key Ratios
    test2 = test_key_ratios_extraction()
    results.append(("Key Ratios", test2))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 All tests passed! Your LLM integration is working correctly.")
        print("\n💡 Recommendation: Update your .env file:")
        print("   LLM_MODEL=deepseek/deepseek-r1:free")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")


if __name__ == "__main__":
    main()
