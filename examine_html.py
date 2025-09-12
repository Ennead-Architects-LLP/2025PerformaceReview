#!/usr/bin/env python3

def examine_html():
    with open('docs/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    print(f'File length: {len(content)}')

    # Find employee-list
    list_start = content.find('<div id="employee-list">')
    if list_start != -1:
        print(f'employee-list found at position {list_start}')

        # Show content from employee-list
        list_content = content[list_start:list_start+2000]
        print('Content from employee-list:')
        print(list_content[:1500])
    else:
        print('employee-list not found')

        # Show end of file
        print('End of file:')
        print(content[-1000:])

if __name__ == "__main__":
    examine_html()
