#!/usr/bin/env python3
"""
Check HTML structure more thoroughly
"""

import re

def check_html_structure():
    with open('../../docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find employee cards
    cards = re.findall(r'<div class="employee-card">(.*?)</div>', content, re.DOTALL)

    if cards:
        first_card = cards[0]
        print(f'Found {len(cards)} employee cards')
        print(f'First card length: {len(first_card)} characters')

        # Check for different field patterns
        field_patterns = [
            r'<div class="field">',
            r'<div class="field[^"]*">',
            r'field-label',
            r'field-value'
        ]

        for pattern in field_patterns:
            matches = re.findall(pattern, first_card)
            print(f'Pattern "{pattern}": {len(matches)} matches')

        # Look for group titles
        group_titles = re.findall(r'<div class="group-title">([^<]+)</div>', first_card)
        print(f'Group titles found: {group_titles}')

        # Check if there's actual content
        if len(first_card) > 1000:
            print('✅ Card has substantial content')
        else:
            print('❌ Card content is too short')

    else:
        print('❌ No employee cards found')

if __name__ == "__main__":
    check_html_structure()
