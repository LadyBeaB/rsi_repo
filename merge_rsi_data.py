# merge_rsi_data.py

import pandas as pd
import os
import shutil
import re
import calendar

# Ensure archive directory exists
os.makedirs("cleansed/archive", exist_ok=True)

# Paths to input files
input_files = [
    "cleansed/cleaned_dual_table_data.csv",
    "cleansed/cleaned_multiheader_table_data.csv",
    "cleansed/cleaned_rpi_data.csv",
    "cleansed/cleaned_table_3_4_data_v3.csv"
]

# Read all files into dataframes and standardise columns
dataframes = []
row_counts = {}

for file_path in input_files:
    df = pd.read_csv(file_path, dtype=str)
    original_row_count = len(df)

    # Capitalise agg_sic_code if exists and remove spaces
    if 'agg_sic_code' in df.columns:
        df['agg_sic_code'] = df['agg_sic_code'].str.upper().str.replace(" ", "")

    # Reorder and select only relevant columns
    expected_cols = ['sheet_name', 'table_name', 'date', 'frequency', 'value', 'agg_sic_code', 'dataset_code']
    df = df[[col for col in expected_cols if col in df.columns]]

    dataframes.append(df)
    row_counts[os.path.basename(file_path)] = original_row_count

# Merge all dataframes into one
merged_df = pd.concat(dataframes, ignore_index=True)
final_row_count = len(merged_df)

# Extract year from the 'date' column
merged_df['year'] = merged_df['date'].str.extract(r'(^\d{4})')

# Create a month mapping dictionary using the calendar module
month_map = {abbr: idx for idx, abbr in enumerate(calendar.month_abbr) if abbr}

# For rows with frequency 'monthly', extract the last three letters from the 'date' column as month_name,
# then convert that month abbreviation to an integer month.
def extract_month(row):
    if str(row['frequency']).lower() == 'monthly' and isinstance(row['date'], str):
        # Use regex to extract the 3-letter month abbreviation at the end of the date string
        match = re.search(r'([A-Za-z]{3})$', row['date'].strip())
        if match:
            return match.group(1)
    return ''

merged_df['month_name'] = merged_df.apply(extract_month, axis=1)
merged_df['month'] = merged_df['month_name'].map(month_map)

# Missing vlaues in annual and quarter will be converted to 0 then all to int
merged_df['month'] = merged_df['month'].fillna(0).astype(int)

# Save the merged data
merged_df.to_csv("cleansed/rsi_data_merged.csv", index=False)

# Move original files to archive
for file_path in input_files:
    shutil.move(file_path, os.path.join("cleansed/archive", os.path.basename(file_path)))

# Print test summary
print("✅ Merged RSI data saved to: cleansed/rsi_data_merged.csv")
print("📊 Row counts:")
for name, count in row_counts.items():
    print(f" - {name}: {count} rows")
print(f"📦 Final merged file: {final_row_count} rows")
diff = final_row_count - sum(row_counts.values())
print(f"🔍 Difference after merge: {diff:+} rows")