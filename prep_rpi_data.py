# prep_rpi_data.py

import pandas as pd
import os
import re
from load_rsi_data_v2 import get_csv_data

# Load the CSV data
csv_df = pd.read_csv("data/series-210325.csv", header=None)

# Extract metadata
sheet_name = str(csv_df.iloc[1, 1]).strip()  # CDID from B2
dataset_code = str(csv_df.iloc[2, 1]).strip()  # Source dataset ID from B3

# Detect start of data at row 9 (index 8)
start_row = 8
csv_data = csv_df.iloc[start_row:].dropna(how='all')

# Assign column names
csv_data.columns = ["date", "value"] + [f"extra_{i}" for i in range(2, len(csv_data.columns))]
csv_data = csv_data[["date", "value"]]  # Only keep the first two columns
csv_data = csv_data.dropna(subset=["date", "value"])

# Detect frequency with full text
def detect_frequency(date_str):
    if re.match(r"^\d{4}$", date_str):
        return "annual"
    elif re.match(r"^\d{4}\s+[A-Za-z]+$", date_str):
        return "monthly"
    elif re.match(r"^\d{4}\s+Q\d$", date_str):
        return "quarterly"
    return "unknown"

csv_data["frequency"] = csv_data["date"].apply(lambda d: detect_frequency(str(d).strip()))

# Build final dataframe
csv_data["sheet_name"] = sheet_name
csv_data["table_name"] = ""
csv_data["agg_sic_code"] = ""
csv_data["dataset_code"] = dataset_code

final_df = csv_data[
    ["sheet_name", "table_name", "date", "value", "frequency", "agg_sic_code", "dataset_code"]
]

# Save output
os.makedirs("cleansed", exist_ok=True)
final_df.to_csv("cleansed/cleaned_rpi_data.csv", index=False)
print("✅ Saved: cleansed/cleaned_rpi_data.csv")