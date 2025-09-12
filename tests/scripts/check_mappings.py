import json

with open('../../assets/data/header_mappings.json', 'r') as f:
    mappings = json.load(f)

print('Current mappings by index:')
for mapping in mappings:
    print(f"{mapping['index_column']:2d} ({mapping['index_letter']}): {mapping['header_text'][:50]} -> {mapping['mapped_header']}")

print('\nChecking for duplicates:')
indices = {}
for mapping in mappings:
    idx = mapping['index_column']
    if idx in indices:
        print(f"DUPLICATE INDEX {idx}: {indices[idx]} AND {mapping['mapped_header']}")
    else:
        indices[idx] = mapping['mapped_header']
