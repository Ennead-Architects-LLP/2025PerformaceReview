#!/usr/bin/env python3

def detailed_check():
    with open('../../docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find employee cards
    import re
    cards = re.findall(r'<div class="employee-card">(.*?)</div>', content, re.DOTALL)

    if cards:
        print(f'✅ Found {len(cards)} employee cards')

        first_card = cards[0]
        print(f'First card total length: {len(first_card)}')

        print('\\nFull card content:')
        print('=' * 80)
        print(first_card)
        print('=' * 80)

        # Check for employee name
        name_match = re.search(r'<div class="employee-name">([^<]+)</div>', first_card)
        if name_match:
            print(f'\\n✅ Employee name found: {name_match.group(1)}')
        else:
            print('\\n❌ Employee name not found')

        # Check for fields-container
        if 'fields-container' in first_card:
            print('✅ Has fields-container')
        else:
            print('❌ Missing fields-container')

    else:
        print('❌ No employee cards found')

if __name__ == "__main__":
    detailed_check()
