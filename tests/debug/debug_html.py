#!/usr/bin/env python3

def debug_html():
    with open('../../docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find employee cards
    import re
    cards = re.findall(r'<div class="employee-card">(.*?)</div>', content, re.DOTALL)

    if cards:
        print(f'Found {len(cards)} cards')
        print('First card content:')
        print(cards[0][:500])  # First 500 chars
        print('...')
        print(f'Total length: {len(cards[0])}')

        # Check if it has fields-container
        if 'fields-container' in cards[0]:
            print('✅ Has fields-container')
        else:
            print('❌ Missing fields-container')

    else:
        print('No cards found')

if __name__ == "__main__":
    debug_html()
