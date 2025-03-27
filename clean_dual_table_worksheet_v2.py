# clean_dual_table_worksheet_v2.py

import pandas as pd
from load_rsi_data_v2 import get_excel_file
import re

xls = pd.ExcelFile(get_excel_file())

all_data = []
agg_reference = {}

# Define target sheets
target_sheets = [
    s for s in xls.sheet_names
    if re.match(r'^(CPSA|CPSB|CPSC|KPSA[1-4]?|Table ID)', s)
]

def clean_text(val):
    """Extracts note (e.g. [note1]) and returns (cleaned_text, note_ref)"""
    if pd.isna(val):
        return '', ''
    val_str = str(val)
    match = re.search(r'\[(.*?)\]', val_str)
    note = match.group(1).capitalize() if match else ''
    cleaned = re.sub(r'\[.*?\]', '', val_str).strip()
    return cleaned, note

def detect_frequency(date_str):
    if re.match(r"^\d{4}$", date_str):
        return "annual"
    elif re.match(r"^\d{4}\s+[A-Za-z]+$", date_str):
        return "monthly"
    elif re.match(r"^\d{4}\s+Q\d$", date_str):
        return "quarterly"
    return "unknown"

# Process each sheet
for sheet_name in target_sheets:
    df_raw = xls.parse(sheet_name, header=None, dtype=str)
    if df_raw.empty:
        continue

    # Find all occurrences of "Time Period" to detect both tables
    time_period_rows = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("Time Period", case=False).any(), axis=1)].index.tolist()

    for i, headers_start_idx in enumerate(time_period_rows):
        # Get table name from the row above "Time Period"
        table_name_row = headers_start_idx - 1
        table_name = df_raw.iloc[table_name_row].dropna().values[0] if table_name_row >= 0 else f"{sheet_name}_table_{i+1}"

        # Extract header rows
        header_rows = df_raw.iloc[headers_start_idx:headers_start_idx+3].fillna('')

        # Extract and clean multi-header info
        column_mappings = []
        for col in range(1, header_rows.shape[1]):
            time_period_desc, note_ref = clean_text(header_rows.iloc[0, col])
            agg_sic = header_rows.iloc[1, col]
            dataset_code = header_rows.iloc[2, col]
            if agg_sic:
                column_mappings.append({
                    "col_index": col,
                    "agg_sic_code": agg_sic,
                    "dataset_code": dataset_code,
                    "table_name": table_name,
                    "sheet_name": sheet_name
                })
                if agg_sic not in agg_reference:
                    agg_reference[agg_sic] = {
                        "time_period_description": time_period_desc,
                        "note_ref": note_ref
                    }

        # Define data block range
        data_start_idx = headers_start_idx + 3
        data_end_idx = time_period_rows[i + 1] if i + 1 < len(time_period_rows) else len(df_raw)
        df_data = df_raw.iloc[data_start_idx:data_end_idx].reset_index(drop=True)

        for _, row in df_data.iterrows():
            date_val = row[0]
            if pd.isna(date_val):
                continue
            frequency = detect_frequency(str(date_val).strip())
            for mapping in column_mappings:
                val = row[mapping["col_index"]]
                if pd.isna(val):
                    continue
                try:
                    all_data.append({
                        "sheet_name": mapping["sheet_name"],
                        "table_name": mapping["table_name"],
                        "date": date_val.strip(),
                        "value": float(val),
                        "frequency": frequency,
                        "agg_sic_code": mapping["agg_sic_code"],
                        "dataset_code": mapping["dataset_code"]
                    })
                except ValueError:
                    continue

# Final DataFrames
df_main = pd.DataFrame(all_data)
df_agg_ref = pd.DataFrame([
    {"agg_sic_code": k, **v} for k, v in agg_reference.items()
])

# Save outputs with frequency and table_name included
df_main.to_csv("cleansed/cleaned_dual_table_data.csv", index=False)
df_agg_ref.to_csv("cleansed/agg_reference.csv", index=False)

# Preview the first few rows
print(df_main.head())
print(df_agg_ref.head())

print("\n ✅ Saved cleaned 'cleaned_dual_table_data.csv'")