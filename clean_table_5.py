# clean_table_5.py

import pandas as pd
import os
import re
from load_rsi_data_v2 import get_excel_file

# Load Excel
xls = get_excel_file()
df_raw = xls.parse("Table 5", header=None, dtype=str)

all_data = []

def clean_text(val):
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

# Detect start rows
time_period_rows = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("Time Period", case=False).any(), axis=1)].index.tolist()

for i, start_idx in enumerate(time_period_rows):
    table_name_row = start_idx - 1
    table_name = df_raw.iloc[table_name_row].dropna().values[0] if table_name_row >= 0 else f"Table5_{i+1}"

    header_rows = df_raw.iloc[start_idx:start_idx+3].fillna('')

    col_mappings = []
    for col in range(1, header_rows.shape[1]):
        time_desc, note_ref = clean_text(header_rows.iloc[0, col])
        header_1 = str(header_rows.iloc[1, col]).strip()
        header_2 = str(header_rows.iloc[2, col]).strip()

        if "Average weekly sales in 2022 (£ millions)" in header_1:
            average_sales = header_1
            dataset_code = header_2
        else:
            average_sales = ''
            dataset_code = header_2 if "Average weekly sales in 2022 (£ millions)" in header_2 else header_1

        if dataset_code:
            col_mappings.append({
                "col_index": col,
                "time_period_description": time_desc,
                "note_ref": note_ref,
                "average_sales_2022": average_sales,
                "dataset_code": dataset_code,
                "table_name": table_name
            })

    data_start = start_idx + len(header_rows)
    data_end = time_period_rows[i + 1] if i + 1 < len(time_period_rows) else len(df_raw)
    df_data = df_raw.iloc[data_start:data_end].reset_index(drop=True)

    for _, row in df_data.iterrows():
        date_val = row[0]
        if pd.isna(date_val):
            continue
        frequency = detect_frequency(str(date_val).strip())
        for mapping in col_mappings:
            val = row[mapping["col_index"]]
            if pd.isna(val):
                continue
            try:
                all_data.append({
                    "sheet_name": "Table 5",
                    "table_name": mapping["table_name"],
                    "date": date_val.strip(),
                    "value": float(val),
                    "frequency": frequency,
                    "time_period_description": mapping["time_period_description"],
                    "average_sales_2022": mapping["average_sales_2022"],
                    "note_ref": mapping["note_ref"],
                    "dataset_code": mapping["dataset_code"]
                })
            except ValueError:
                continue

# Save to CSV
os.makedirs("cleansed", exist_ok=True)
df_final = pd.DataFrame(all_data)
df_final.to_csv("cleansed/cleaned_table_5_data.csv", index=False)

print("✅ Saved: cleansed/cleaned_table_5_data.csv")