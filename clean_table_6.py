# clean_table_6.py

import pandas as pd
import os
import re
from load_rsi_data_v2 import get_excel_file

# Load worksheet
xls = get_excel_file()
df_raw = xls.parse("Table 6", header=None, dtype=str)

all_data = []

# Clean and extract possible footnotes like [c]
def clean_value(val):
    if pd.isna(val):
        return None, None
    val_str = str(val)
    match = re.search(r"\[(.*?)\]", val_str)
    note_raw = match.group(1).capitalize() if match else ''
    note_ref = 'Confidential' if note_raw == 'C' else note_raw
    cleaned_val = re.sub(r"\[.*?\]", "", val_str).strip()
    try:
        return float(cleaned_val), note_ref
    except ValueError:
        return None, note_ref

# Identify header row
header_row_idx = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("Business type", case=False).any(), axis=1)].index[0]
header_row = df_raw.iloc[header_row_idx]

# Parse data block
df_data = df_raw.iloc[header_row_idx + 1:].dropna(how="all").reset_index(drop=True)
df_data.columns = header_row.fillna('').tolist()

# Melt data for normalization
id_vars = ['Business type']
value_vars = [col for col in df_data.columns if col not in id_vars]

df_melted = df_data.melt(id_vars=id_vars, value_vars=value_vars, var_name='column_type', value_name='raw_value')

# Clean values and extract footnotes
df_melted[['value', 'note_ref']] = df_melted['raw_value'].apply(clean_value).apply(pd.Series)

# Final structure
df_melted['sheet_name'] = 'Table 6'

# Reorder columns
df_final = df_melted[['sheet_name', 'Business type', 'column_type', 'value', 'note_ref']]

# Save output
os.makedirs("cleansed", exist_ok=True)
df_final.to_csv("cleansed/cleaned_table_6_data.csv", index=False)

print("✅ Saved: cleansed/cleaned_table_6_data.csv")