#!/usr/bin/env python3
"""
Quick script to check if HTML cards have employee information
"""

import re

def check_html_cards():
    # Read HTML file
    with open('docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for employee cards
    cards = re.findall(r'<div class="employee-card">(.*?)</div>', content, re.DOTALL)

    if cards:
        print(f'✅ Found {len(cards)} employee cards in HTML')
        print('')
        print('Sample card content (first 1000 chars):')
        first_card = cards[0]
        print(repr(first_card[:1000]))

        # Check for basic structure
        has_header = 'employee-header' in first_card
        has_name = 'employee-name' in first_card
        has_fields = 'field' in first_card

        print('')
        print('Structure check:')
        print(f'  Has header section: {has_header}')
        print(f'  Has name field: {has_name}')
        print(f'  Has data fields: {has_fields}')

        if has_name:
            name_match = re.search(r'employee-name[^>]*>([^<]+)</div>', first_card)
            if name_match:
                print(f'  Employee name: {name_match.group(1)}')

    else:
        print('❌ No employee cards found in HTML')

if __name__ == "__main__":
    check_html_cards()
