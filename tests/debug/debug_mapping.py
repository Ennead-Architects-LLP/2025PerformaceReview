import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from app.modules.header_mapper import HeaderMapper
import pandas as pd

# Load Excel and check header mapping
df = pd.read_excel('../../assets/data/Employee Self-Evaluation Data Export From MS Form.xlsx')
header_mapper = HeaderMapper()
mappings = header_mapper.map_excel_headers(df)

print('Header mappings for performance ratings (showing conflicts):')
rating_mappings = {}
for col_index, mapping in mappings.items():
    if mapping.group_under.value == 'performance_ratings':
        field_name = mapping.mapped_header
        if field_name not in rating_mappings:
            rating_mappings[field_name] = []
        rating_mappings[field_name].append((col_index, mapping))

for field_name, field_mappings in rating_mappings.items():
    print(f'Field: {field_name}')
    if len(field_mappings) > 1:
        print(f'  *** CONFLICT DETECTED - {len(field_mappings)} mappings ***')

    for col_index, mapping in field_mappings:
        print('2d')
        if mapping.original_header in df.columns:
            try:
                sample_value = df.iloc[0][mapping.original_header]
                try:
                    int_val = int(sample_value)
                    data_type = 'NUMERIC'
                except:
                    data_type = 'TEXT'
                print(f'  Sample: {str(sample_value)[:30]}... ({data_type})')
            except Exception as e:
                print(f'  Sample: ERROR - {e}')
        else:
            print(f'  Column not found in Excel!')
    print()

print('\nAll columns with rating-related names:')
for i, col in enumerate(df.columns):
    if any(keyword in col.lower() for keyword in ['communication', 'collaboration', 'professionalism', 'technical', 'workflow']):
        sample_value = df.iloc[0][col]
        try:
            int_val = int(sample_value)
            data_type = 'NUMERIC (rating)'
        except:
            data_type = 'TEXT (comment)'
        print('2d')
