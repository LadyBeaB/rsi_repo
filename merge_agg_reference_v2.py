# merge_agg_reference_v2.py

import pandas as pd
import os
import re
import shutil
from collections import defaultdict

# Load all agg_reference files
ref_paths = [
    "cleansed/agg_reference.csv",
    "cleansed/agg_reference_extended.csv",
    "cleansed/agg_reference_table_3_4.csv"
]

dfs = [pd.read_csv(path, dtype=str) for path in ref_paths]

# Normalise all columns to expected names
for df in dfs:
    if 'sales_in_2022' in df.columns:
        df.rename(columns={'sales_in_2022': 'sales_in_2022_mln'}, inplace=True)
    if 'sales_in_2022_£_mln' in df.columns:
        df.rename(columns={'sales_in_2022_£_mln': 'sales_in_2022_mln'}, inplace=True)
    if 'sales_in_2022_mln' not in df.columns:
        df['sales_in_2022_mln'] = ''
    if 'percentage_weight' not in df.columns:
        df['percentage_weight'] = ''
    if 'note_ref' not in df.columns:
        df['note_ref'] = ''

# Concatenate all references
merged_df = pd.concat(dfs, ignore_index=True)

# Clean and normalize fields
merged_df['agg_sic_code'] = merged_df['agg_sic_code'].str.upper().str.replace(' ', '')
merged_df['note_ref'] = merged_df['note_ref'].str.replace(r'(?i)^note(\d+)$', r'Note \1', regex=True)
merged_df['sales_in_2022_mln'] = (
    merged_df['sales_in_2022_mln']
    .str.replace(r'[^\d.,]', '', regex=True)
    .str.replace('m', '', case=False)
    .str.strip()
)

# Track duplicates for logging
dup_log = []
final_rows = []
deduped_descriptions = {}

# Deduplicate by time_period_description
for _, row in merged_df.iterrows():
    desc = row['time_period_description']
    current_code = row['agg_sic_code']

    if desc not in deduped_descriptions:
        deduped_descriptions[desc] = row
        final_rows.append(row)
    else:
        existing = deduped_descriptions[desc]
        if current_code != existing['agg_sic_code']:
            dup_log.append({
                "type": "time_period_description",
                "time_period_description": desc,
                "kept_agg_sic_code": existing['agg_sic_code'],
                "dropped_agg_sic_code": current_code
            })

# Create DataFrame and check agg_sic_code duplicates
final_df = pd.DataFrame(final_rows)
agg_codes_seen = {}
final_rows_dedup = []

for _, row in final_df.iterrows():
    code = row['agg_sic_code']
    if code not in agg_codes_seen:
        agg_codes_seen[code] = row
        final_rows_dedup.append(row)
    else:
        dup_log.append({
            "type": "agg_sic_code",
            "time_period_description": row['time_period_description'],
            "kept_agg_sic_code": agg_codes_seen[code]['agg_sic_code'],
            "dropped_agg_sic_code": code
        })

# Final dataframe
final_df_dedup = pd.DataFrame(final_rows_dedup)

# Append manual corrections
manual_path = "manual_agg_ref.txt"
if os.path.exists(manual_path):
    manual_df = pd.read_csv(manual_path, sep="|", dtype=str).fillna('')

    # Clean manual entries the same way
    manual_df['agg_sic_code'] = manual_df['agg_sic_code'].str.upper().str.replace(' ', '')
    manual_df['note_ref'] = manual_df['note_ref'].str.replace(r'(?i)^note(\d+)$', r'Note \1', regex=True)
    manual_df['sales_in_2022_mln'] = (
        manual_df['sales_in_2022_mln']
        .str.replace(r'[^\d.,]', '', regex=True)
        .str.replace('m', '', case=False)
        .str.strip()
    )

    # Filter for new additions only
    existing_keys = set(zip(final_df_dedup['agg_sic_code'], final_df_dedup['time_period_description']))
    manual_df['key'] = list(zip(manual_df['agg_sic_code'], manual_df['time_period_description']))
    new_entries = manual_df[~manual_df['key'].isin(existing_keys)].drop(columns=['key'])

    # Merge and count
    rows_before = len(final_df_dedup)
    final_df_dedup = pd.concat([final_df_dedup, new_entries], ignore_index=True)
    added_rows = len(final_df_dedup) - rows_before
else:
    added_rows = 0

# Save merged reference file
os.makedirs("cleansed", exist_ok=True)
final_df_dedup.to_csv("cleansed/agg_reference_merged.csv", index=False)

# Save duplicates log
log_df = pd.DataFrame(dup_log)
log_df.to_csv("cleansed/agg_reference_duplicates_log.csv", index=False)

print("✅ Saved: cleansed/agg_reference_merged.csv")
print("📘 Duplicates log: cleansed/agg_reference_duplicates_log.csv")
print(f"➕ Rows added from manual_agg_ref.txt: {added_rows}")

# Move old reference files to archive
archive_dir = "cleansed/archive"
os.makedirs(archive_dir, exist_ok=True)

for path in ref_paths:
    if os.path.exists(path):
        shutil.move(path, os.path.join(archive_dir, os.path.basename(path)))

print("📦 Archived original reference files to 'cleansed/archive/'")