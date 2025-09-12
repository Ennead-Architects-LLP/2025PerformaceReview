#!/usr/bin/env python3

def check_html_content():
    with open('docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the position of the first employee card
    card_start = content.find('<div class="employee-card">')
    if card_start != -1:
        print(f'First employee card starts at position: {card_start}')

        # Show 500 characters starting from that position
        card_section = content[card_start:card_start+500]
        print('HTML content around first card:')
        print(card_section)

        # Check if it ends with </div>
        if '</div>' in card_section:
            end_pos = card_section.find('</div>')
            print(f'Card ends at relative position: {end_pos}')
            print(f'Card length: {end_pos + 6}')  # +6 for </div>
        else:
            print('Card does not seem to end with </div> in first 500 chars')
    else:
        print('Employee card not found')

if __name__ == "__main__":
    check_html_content()
