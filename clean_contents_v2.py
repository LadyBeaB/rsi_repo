# clean_contents_v2.py

import pandas as pd
from load_rsi_data_v2 import get_excel_file

# Load Excel via shared module
xls = get_excel_file()

# Drop the "Cover Sheet"
sheets = [s for s in xls.sheet_names if s != "Cover Sheet"]

# Load "Contents" sheet without headers
raw_df = xls.parse('Contents', header=None, dtype=str)

# Find header row
header_row_index = None
for i, row in raw_df.iterrows():
    if (
        row.astype(str).str.lower().str.contains("worksheet number").any()
        and row.astype(str).str.lower().str.contains("worksheet description").any()
    ):
        header_row_index = i
        break

if header_row_index is None:
    raise ValueError("Header row with expected column names not found.")

# Reload with proper header
df_contents = xls.parse('Contents', header=header_row_index, dtype=str)
df_contents.columns = [col.strip().lower() for col in df_contents.columns]

# Extract relevant columns
df_cleaned = df_contents[['worksheet number', 'worksheet description']].copy()
df_cleaned.columns = ['worksheet_number', 'worksheet_description']
df_cleaned.dropna(subset=['worksheet_number', 'worksheet_description'], inplace=True)
df_cleaned.reset_index(drop=True, inplace=True)

# Save to CSV
df_cleaned.to_csv('cleansed/cleaned_contents.csv', index=False)
print("\n ✅ Saved cleaned worksheet descriptions to 'cleansed/cleaned_contents.csv'")