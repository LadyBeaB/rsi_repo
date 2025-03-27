# clean_notes.py

import pandas as pd
from load_rsi_data_v2 import get_excel_file

# Load workbook
xls = get_excel_file()

# Check if "Notes" worksheet exists
if "Notes" not in xls.sheet_names:
    raise ValueError("Worksheet 'Notes' not found in the Excel file.")

# Load Notes sheet without headers first
raw_df = xls.parse("Notes", header=None, dtype=str)

# Find header row containing 'Note number' and 'Note text'
header_row_index = None
for i, row in raw_df.iterrows():
    if (
        row.astype(str).str.lower().str.contains("note number").any()
        and row.astype(str).str.lower().str.contains("note text").any()
    ):
        header_row_index = i
        break

if header_row_index is None:
    raise ValueError("Header row with 'Note number' and 'Note text' not found.")

# Load again using detected header row
df_notes = xls.parse("Notes", header=header_row_index, dtype=str)

# Standardise column names
df_notes.columns = [col.strip().lower() for col in df_notes.columns]

# Extract only relevant columns
df_cleaned_notes = df_notes[['note number', 'note text']].copy()
df_cleaned_notes.columns = ['note_number', 'note_text']

# Drop rows with missing notes
df_cleaned_notes.dropna(subset=['note_number', 'note_text'], inplace=True)

# Reset index
df_cleaned_notes.reset_index(drop=True, inplace=True)

# Save to CSV
df_cleaned_notes.to_csv('cleansed/cleaned_notes.csv', index=False)
print("\n ✅ Saved cleaned notes to 'cleansed/cleaned_notes.csv'")