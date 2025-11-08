"""
Test: Can LLM extract ALL 20 fields with 100% accuracy if Camelot completely fails?

This script tests the LLM's ability to extract all fields from raw PDF text
without any help from Camelot table extraction.
"""

import fitz
import os
from llm_extractor import extract_balance_sheet_llm, extract_key_ratios_llm

def test_llm_full_extraction():
    print('='*80)
    print('TESTING: LLM FULL EXTRACTION (Without Camelot)')
    print('='*80)
    print()

    # Find the most recent 2020 PDF (good test case - multi-column)
    downloads_dir = 'downloads'
    pdf_path = None

    for folder in sorted(os.listdir(downloads_dir), reverse=True):
        folder_path = os.path.join(downloads_dir, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if '2020' in file and file.endswith('.pdf'):
                    pdf_path = os.path.join(folder_path, file)
                    break
        if pdf_path:
            break

    if not pdf_path:
        print("ERROR: No 2020 PDF found. Please run orchestrator with TARGET_YEAR=2020 first.")
        return

    print(f'Testing with: {pdf_path}')
    print()

    # Expected values from 2020 PDF verification
    expected_bs = {
        'DERIVATIVEINSTRUMENTS': 6997,
        'CASHANDBANKBALANCES': 5670,
        'OTHERASSETS': 957,
        'PREPAIDEXPENSESANDACCRUEDINCOME': 1524,
        'TOTALASSETS': 362451,
        'DERIVATIVEINSTRUMENTSLIABILITIES': 2188,
        'OTHERLIABILITIES': 2165,
        'DEFERREDINCOMEANDACCRUEDEXPENSES': 210,
        'TOTALLIABILITIES': 4563,
        'FUNDCAPITALCARRIEDFORWARD': 381350,
        'NETPAYMENTSTOTHENATIONALPENSIONSYSTEM': -4200,
        'NETRESULTFORTHEPERIOD': -19262,
        'TOTALFUNDCAPITAL': 357888,
        'TOTALFUNDCAPITALANDLIABILITIES': 362451,
        # Note: Equities fields come from Income Statement, not Balance Sheet
        # LLM extracts from Balance Sheet page, so these will be different
    }

    expected_kr = {
        'FUNDCAPITALCARRIEDFORWARDLEVEL': 357.9,
        'NETOUTFLOWSTOTHENATIONALPENSIONSYSTEM': -4.2,
        'TOTAL': -19.3
    }

    print('='*80)
    print('TEST 1: Balance Sheet Extraction (17 fields)')
    print('='*80)

    # Extract Balance Sheet
    bs_data = extract_balance_sheet_llm(pdf_path, page_num=5)

    print(f'\nLLM extracted {len(bs_data)}/17 Balance Sheet fields:')

    bs_correct = 0
    bs_total = 0

    for field, value in bs_data.items():
        if field in expected_bs:
            expected = expected_bs[field]
            match = 'OK' if value == expected else 'MISMATCH'
            if value == expected:
                bs_correct += 1
            bs_total += 1
            print(f'  {field}: {value:,} | Expected: {expected:,} | {match}')
        else:
            print(f'  {field}: {value:,} | (Income Statement field - not in Balance Sheet)')

    print()
    print('='*80)
    print('TEST 2: Key Ratios Extraction (3 fields)')
    print('='*80)

    # Extract Key Ratios
    kr_data = extract_key_ratios_llm(pdf_path, page_num=2)

    print(f'\nLLM extracted {len(kr_data)}/3 Key Ratios fields:')

    kr_correct = 0
    kr_total = 0

    for field, value in kr_data.items():
        if field in expected_kr:
            expected = expected_kr[field]
            match = 'OK' if value == expected else 'MISMATCH'
            if value == expected:
                kr_correct += 1
            kr_total += 1
            print(f'  {field}: {value} | Expected: {expected} | {match}')

    print()
    print('='*80)
    print('FINAL RESULTS:')
    print('='*80)

    total_extracted = len(bs_data) + len(kr_data)
    total_correct = bs_correct + kr_correct
    total_expected = bs_total + kr_total

    print(f'\nTotal fields extracted: {total_extracted}/20')
    print(f'Verifiable fields: {total_expected}/20')
    print(f'Correct extractions: {total_correct}/{total_expected}')

    if total_expected > 0:
        accuracy = (total_correct / total_expected) * 100
        print(f'Accuracy: {accuracy:.1f}%')
        print()

        if accuracy == 100 and total_extracted == 20:
            print('CONCLUSION: LLM CAN extract all 20 fields with 100% accuracy!')
        elif accuracy >= 95 and total_extracted >= 18:
            print('CONCLUSION: LLM CAN extract most fields with high accuracy!')
        elif accuracy >= 90:
            print('CONCLUSION: LLM CAN extract fields with good accuracy!')
        else:
            print('CONCLUSION: LLM needs improvement for full extraction')

    print('='*80)

if __name__ == '__main__':
    test_llm_full_extraction()
