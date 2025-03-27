# rerun_table_3_4.py

import pandas as pd
import os

def normalize_description(desc):
    """Normalize the description by stripping whitespace and converting to lower-case."""
    if pd.isna(desc):
        return ""
    return desc.strip().lower()

# Load input files
main_data_path = "cleansed/cleaned_table_3_4_data_v3.csv"
reference_path = "cleansed/agg_reference_merged.csv"
log_path = "cleansed/unmatched_table_3_4_log.csv"

main_df = pd.read_csv(main_data_path, dtype=str)
agg_ref = pd.read_csv(reference_path, dtype=str)

# Create lookup keys using the full, normalised time_period_description
agg_ref["lookup_key"] = agg_ref["time_period_description"].apply(normalize_description)
lookup_dict = agg_ref.set_index("lookup_key")["agg_sic_code"].to_dict()

main_df["lookup_key"] = main_df["time_period_description"].apply(normalize_description)

# Debug prints to verify key consistency
print("Reference keys sample:", agg_ref["lookup_key"].dropna().unique()[:5])
print("Main DF keys sample:", main_df["lookup_key"].dropna().unique()[:5])

# Fill missing agg_sic_code using the lookup dictionary
main_df["agg_sic_code"] = main_df.apply(
    lambda row: lookup_dict.get(row["lookup_key"], row["agg_sic_code"]), axis=1
)

# Identify unmatched rows after filling
unmatched = main_df[main_df["agg_sic_code"].isna() | (main_df["agg_sic_code"] == "")]
unmatched.to_csv(log_path, index=False)

# Drop helper column if no longer needed
main_df.drop(columns=["lookup_key"], inplace=True)

# Save updated main file
main_df.to_csv(main_data_path, index=False)

print("✅ Updated:", main_data_path)
print("📘 Log of unmatched entries:", log_path)
print("Output written to:", main_data_path)