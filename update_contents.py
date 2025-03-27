# update_contents.py

import pandas as pd
import os
from load_rsi_data_v2 import get_csv_data

# Load existing cleaned contents
contents_path = "cleansed/cleaned_contents.csv"
df_contents = pd.read_csv(contents_path)

# Drop any accidentally added columns with spaces
columns_to_drop = [col for col in df_contents.columns if col.strip().lower().replace(" ", "_") in ["worksheet_number", "worksheet_description"] and col != "worksheet_number" and col != "worksheet_description"]
df_contents.drop(columns=columns_to_drop, inplace=True, errors='ignore')

# Load the CSV data source using shared loader, skipping header row
df_csv = pd.read_csv("data/series-210325.csv", header=None).iloc[:5, :]

# Extract correct metadata
worksheet_number = str(df_csv.iloc[1, 1]).strip()       # CDID (B2)
worksheet_description = str(df_csv.iloc[0, 1]).strip()  # Title (B1)

# Avoid duplicate entry
if not ((df_contents['worksheet_number'] == worksheet_number) & (df_contents['worksheet_description'] == worksheet_description)).any():
    new_row = {
        "worksheet_number": worksheet_number,
        "worksheet_description": worksheet_description
    }
    df_contents = pd.concat([df_contents, pd.DataFrame([new_row])], ignore_index=True)

# Save back to the CSV
os.makedirs("cleansed", exist_ok=True)
df_contents.to_csv(contents_path, index=False)

print("✅ Cleaned up and updated cleaned_contents.csv with series-210325.csv metadata.")