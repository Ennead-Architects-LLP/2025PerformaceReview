import pandas as pd

# Check all column names in Excel
df = pd.read_excel('../../assets/data/Employee Self-Evaluation Data Export From MS Form.xlsx')
print('All Excel columns:')
for i, col in enumerate(df.columns):
    print(f'{i:2d}: "{col}"')

print()
print('Sample data from first row (first 20 columns):')
for col in df.columns[:20]:
    value = df.iloc[0][col]
    print(f'{col[:20]:20}: {value}')
