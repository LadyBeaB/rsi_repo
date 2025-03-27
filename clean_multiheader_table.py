# clean_multiheader_table.py

import pandas as pd
import re
import os
from load_rsi_data_v2 import get_excel_file

# Ensure cleansed directory exists
os.makedirs("cleansed", exist_ok=True)

# Load Excel file
xls = pd.ExcelFile(get_excel_file())

# Target sheets
target_sheets = [s for s in xls.sheet_names if re.match(r'^Table [1-2] [MQA]$', s)]

all_data = []
agg_reference = {}

# Helper to clean text and extract note

def clean_text(val):
    if pd.isna(val):
        return '', ''
    val_str = str(val)
    match = re.search(r'\[(.*?)\]', val_str)
    note = match.group(1).capitalize() if match else ''
    cleaned = re.sub(r'\[.*?\]', '', val_str).strip()
    return cleaned, note

# Frequency detection

def detect_frequency(date_str):
    date_str = date_str.strip()
    if re.match(r"^\d{4} [A-Za-z]{3}$", date_str):
        return "monthly"
    elif re.match(r"^\d{4} Q[1-4]$", date_str):
        return "quarterly"
    elif re.match(r"^\d{4}$", date_str):
        return "annual"
    return "unknown"

# Field labels to detect
FIELD_LABELS = {
    'time_period_description': ['time period'],
    'sales_in_2022': ['sales in 2022'],
    'agg_sic_code': ['agg/sic', 'agg/sic code'],
    'percentage_weight': ['percentage weight'],
    'dataset_code': ['dataset identifier code']
}

# Process each sheet
for sheet_name in target_sheets:
    df_raw = xls.parse(sheet_name, header=None, dtype=str)
    if df_raw.empty:
        continue

    time_period_rows = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("Time Period", case=False).any(), axis=1)].index.tolist()

    for i, headers_start_idx in enumerate(time_period_rows):
        table_name_row = headers_start_idx - 1
        table_name = df_raw.iloc[table_name_row].dropna().values[0] if table_name_row >= 0 else f"{sheet_name}_table_{i+1}"

        next_block_start = time_period_rows[i + 1] if i + 1 < len(time_period_rows) else len(df_raw)
        header_block = df_raw.iloc[headers_start_idx:next_block_start].fillna('')

        # Identify which row corresponds to which field
        field_row_map = {}
        for row_idx in range(min(5, header_block.shape[0])):
            first_cell = str(header_block.iloc[row_idx, 0]).strip().lower()
            for field, labels in FIELD_LABELS.items():
                if any(label in first_cell for label in labels):
                    field_row_map[field] = row_idx

        column_mappings = []
        for col in range(1, header_block.shape[1]):
            time_period_desc, note_ref = clean_text(header_block.iloc[field_row_map.get('time_period_description', -1), col]) if 'time_period_description' in field_row_map else ('', '')
            sales_in_2022 = header_block.iloc[field_row_map['sales_in_2022'], col] if 'sales_in_2022' in field_row_map else ''
            agg_sic = header_block.iloc[field_row_map['agg_sic_code'], col] if 'agg_sic_code' in field_row_map else ''
            percentage_weight = header_block.iloc[field_row_map['percentage_weight'], col] if 'percentage_weight' in field_row_map else ''
            dataset_code = header_block.iloc[field_row_map['dataset_code'], col] if 'dataset_code' in field_row_map else ''

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
                        "note_ref": note_ref,
                        "sales_in_2022": sales_in_2022,
                        "percentage_weight": percentage_weight
                    }

        # Read data rows
        data_start_idx = headers_start_idx + len(field_row_map)
        df_data = df_raw.iloc[data_start_idx:next_block_start].reset_index(drop=True)

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
                        "date": str(date_val).strip(),
                        "frequency": frequency,
                        "value": float(val),
                        "agg_sic_code": mapping["agg_sic_code"],
                        "dataset_code": mapping["dataset_code"]
                    })
                except ValueError:
                    continue

# Final output

pd.DataFrame(all_data).to_csv("cleansed/cleaned_multiheader_table_data.csv", index=False)
pd.DataFrame([{ "agg_sic_code": k, **v } for k, v in agg_reference.items()]).to_csv("cleansed/agg_reference_extended.csv", index=False)

print("✅ Saved:")
print(" - cleansed/cleaned_multiheader_table_data.csv")
print(" - cleansed/agg_reference_extended.csv")