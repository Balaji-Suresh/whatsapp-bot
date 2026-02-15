import pandas as pd

# Convert CSV to Excel
df = pd.read_csv('contacts.csv')
df.to_excel('contacts.xlsx', index=False)
print("Excel file created: contacts.xlsx")