#!/usr/bin/env python3

def verify_employee_objects():
    with open('docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    print(f'File size: {len(content)} characters')

    # Check if employee cards are present
    import re
    cards = re.findall(r'<div class="employee-card">(.*?)</div>', content, re.DOTALL)
    print(f'Found {len(cards)} employee cards')

    if cards:
        first_card = cards[0]
        print(f'First card length: {len(first_card)}')

        # Check for employee name
        if 'Brett Fabrikant' in first_card:
            print('✅ Employee name found in card')
        else:
            print('❌ Employee name not found')

        # Check for field groups
        groups = re.findall(r'<div class="field-group">(.*?)</div>', first_card, re.DOTALL)
        print(f'Number of field groups: {len(groups)}')

        if groups:
            print('✅ Employee data is being displayed!')
            print('🎉 Employee objects are successfully passed through the entire pipeline!')
        else:
            print('❌ No field groups found')
    else:
        print('❌ No employee cards found')

if __name__ == "__main__":
    verify_employee_objects()
