# clean_table_3_4_v3.py

import pandas as pd
import re
import os
from load_rsi_data_v2 import get_excel_file

# Ensure output folder exists
os.makedirs("cleansed", exist_ok=True)

# Load Excel file and reference from agg_reference_extended.csv
xls = pd.ExcelFile(get_excel_file())
df_agg_lookup = pd.read_csv("cleansed/agg_reference_extended.csv")

# Build time_period_description lookup using agg_reference_extended.csv
description_lookup = {}
for _, row in df_agg_lookup.iterrows():
    desc = str(row.get("time_period_description", '')).strip().lower()
    if desc and desc not in description_lookup:
        description_lookup[desc] = {
            "agg_sic_code": str(row.get("agg_sic_code", '')).strip(),
            "note_ref": str(row.get("note_ref", '')).strip()
        }

# Target only Table 3 and 4 sheets
target_sheets = [s for s in xls.sheet_names if re.match(r'^Table [34] [MQA]$', s)]

all_data = []
agg_ref = {}
unmatched_log = []

def clean_text(val):
    if pd.isna(val):
        return '', ''
    val_str = str(val)
    match = re.search(r'\[(.*?)\]', val_str)
    note = match.group(1).capitalize() if match else ''
    cleaned = re.sub(r'\[.*?\]', '', val_str).strip()
    return cleaned, note

def detect_frequency(date_str):
    date_str = date_str.strip()
    if re.match(r"^\d{4} [A-Za-z]{3}$", date_str):
        return "monthly"
    elif re.match(r"^\d{4} Q[1-4]$", date_str):
        return "quarterly"
    elif re.match(r"^\d{4}$", date_str):
        return "annual"
    return "unknown"

# Suffix mapping:
suffix_map = {
    "all businesses": "-AB",
    "large businesses": "-LB",
    "small businesses": "-SB"
}

for sheet_name in target_sheets:
    df_raw = xls.parse(sheet_name, header=None, dtype=str)
    if df_raw.empty:
        continue

    time_period_rows = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("Time Period", case=False).any(), axis=1)].index.tolist()

    for i, headers_start_idx in enumerate(time_period_rows):
        table_name_row = headers_start_idx - 1
        table_name = df_raw.iloc[table_name_row].dropna().values[0] if table_name_row >= 0 else f"{sheet_name}_table_{i+1}"

        next_header_idx = time_period_rows[i + 1] if i + 1 < len(time_period_rows) else len(df_raw)
        header_block = df_raw.iloc[headers_start_idx:next_header_idx].fillna('')

        header_rows = header_block.iloc[:3]  # Max 3 rows
        df_data = header_block.iloc[3:].reset_index(drop=True)

        time_period_header = header_rows.iloc[0]
        dataset_code_row = None
        sales_in_2022_row = None

        # Detect actual header row positions
        for row_idx in range(1, 3):
            row_vals = header_rows.iloc[row_idx].astype(str).str.lower().tolist()
            if any("dataset identifier code" in val for val in row_vals):
                dataset_code_row = header_rows.iloc[row_idx]
            elif any("sales in 2022" in val for val in row_vals):
                sales_in_2022_row = header_rows.iloc[row_idx]

        for col in range(1, header_rows.shape[1]):
            raw_time_period = time_period_header[col]
            cleaned_desc, note_ref = clean_text(raw_time_period)

            # Split description into parts using commas. 
            # If there are multiple commas, join all except the last one as the base description.
            parts = [part.strip() for part in cleaned_desc.split(",")]
            if len(parts) > 1:
                suffix = parts[-1].lower()  # business size suffix
                base_key = ", ".join(parts[:-1]).lower()  # join all parts except the last one
            else:
                suffix = ""
                base_key = parts[0].lower()

            suffix_tag = suffix_map.get(suffix, '')
            base_lookup = description_lookup.get(base_key, {})
            base_agg_code = base_lookup.get("agg_sic_code", '')
            note_ref = base_lookup.get("note_ref", note_ref)
            final_agg_code = f"{base_agg_code}{suffix_tag}" if base_agg_code else ''

            dataset_code = dataset_code_row[col].strip() if dataset_code_row is not None else ''
            sales_in_2022 = sales_in_2022_row[col].strip() if sales_in_2022_row is not None else ''

            if not base_agg_code:
                unmatched_log.append({
                    "sheet_name": sheet_name,
                    "table_name": table_name,
                    "dataset_code": dataset_code,
                    "time_period_description": cleaned_desc
                })

            if final_agg_code and final_agg_code not in agg_ref:
                agg_ref[final_agg_code] = {
                    "time_period_description": cleaned_desc,
                    "note_ref": note_ref,
                    "sales_in_2022": sales_in_2022
                }

            for _, row in df_data.iterrows():
                date_val = row[0]
                val = row[col]
                if pd.isna(date_val) or pd.isna(val):
                    continue

                frequency = detect_frequency(str(date_val))

                try:
                    all_data.append({
                        "sheet_name": sheet_name,
                        "table_name": table_name,
                        "date": str(date_val).strip(),
                        "frequency": frequency,
                        "value": float(val),
                        "agg_sic_code": final_agg_code,
                        "dataset_code": dataset_code,
                        "time_period_description": cleaned_desc  
                    })
                except ValueError:
                    continue

# Output the CSV files, including time_period_description in the main data CSV
pd.DataFrame(all_data).to_csv("cleansed/cleaned_table_3_4_data_v3.csv", index=False)
pd.DataFrame([{"agg_sic_code": k, **v} for k, v in agg_ref.items()]).to_csv("cleansed/agg_reference_table_3_4.csv", index=False)
pd.DataFrame(unmatched_log).to_csv("cleansed/unmatched_table_3_4_log.csv", index=False)

output_file = "cleansed/cleaned_table_3_4_data_v3.csv"
print("Output written to:", output_file)

print("✅ Saved:")
print(" - cleansed/cleaned_table_3_4_data_v3.csv")
print(" - cleansed/agg_reference_table_3_4.csv")
print(" - cleansed/unmatched_table_3_4_log.csv")