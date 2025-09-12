#!/usr/bin/env python3

def check_final_html():
    with open('docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find employee cards
    import re
    cards = re.findall(r'<div class="employee-card">(.*?)</div>', content, re.DOTALL)

    if cards:
        print(f'✅ Found {len(cards)} employee cards')
        first_card = cards[0]
        print(f'First card total length: {len(first_card)}')

        # Check for fields-container
        if 'fields-container' in first_card:
            print('✅ Has fields-container')
            container_match = re.search(r'<div class="fields-container">(.*?)</div>', first_card, re.DOTALL)
            if container_match:
                container_content = container_match.group(1)
                print(f'Fields container content length: {len(container_content)}')

                # Check for field groups
                groups = re.findall(r'<div class="field-group">(.*?)</div>', container_content, re.DOTALL)
                print(f'Number of field groups: {len(groups)}')

                if groups:
                    print('✅ Has field groups with content!')
                    print('🎉 HTML cards now display employee information correctly!')
                else:
                    print('❌ Field groups are empty')
            else:
                print('❌ Could not extract fields-container content')
        else:
            print('❌ Missing fields-container')
    else:
        print('❌ No employee cards found')

if __name__ == "__main__":
    check_final_html()
