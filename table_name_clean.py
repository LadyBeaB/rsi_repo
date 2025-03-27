# table_name_clean.py

import pandas as pd
import os

# Ensure the 'cleansed' folder exists
os.makedirs("cleansed", exist_ok=True)

# Define file paths
merged_csv_path = "cleansed/rsi_data_merged.csv"
clean_table_name_path = "cleansed/clean_table_name.csv"

# Read the merged RSI data
df = pd.read_csv(merged_csv_path, dtype=str)

# Get unique table names from the 'table_name' column (dropping any NaN)
unique_table_names = df['table_name'].dropna().unique()

# Create a DataFrame with the unique table names
table_names_df = pd.DataFrame(unique_table_names, columns=['table_name'])

# Define the unwanted table name text (to be removed)
unwanted_text = "Some cells in this table are empty because data was not collected for these variables at these time points."

# Remove the unwanted row from the unique table names
table_names_df = table_names_df[table_names_df['table_name'] != unwanted_text].copy()

# Function to create a table code by taking the first letter of each word in the table name
def create_table_code(name):
    return ''.join(word[0].upper() for word in name.split())

# Apply the function to create a new 'table_code' column
table_names_df['table_code'] = table_names_df['table_name'].apply(create_table_code)

# Save the unique table names mapping to a CSV file
table_names_df.to_csv(clean_table_name_path, index=False)
print("Saved unique table names mapping to:", clean_table_name_path)

# --- Now update the main merged data ---

# Remove rows where table_name is the unwanted text
df_clean = df[df['table_name'] != unwanted_text].copy()

# Create a dictionary mapping from table_name to table_code
table_code_dict = table_names_df.set_index('table_name')['table_code'].to_dict()

# Map the table_code to the main data based on table_name
df_clean['table_code'] = df_clean['table_name'].map(table_code_dict)

# Create a unique identifier (uid) as "sheet_name-table_code-date"
# Ensure that sheet_name, table_code, and date are strings
df_clean['uid'] = df_clean['sheet_name'].astype(str) + "-" + df_clean['table_code'].astype(str) + "-" + df_clean['date'].astype(str)

# Remove the 'table_name' column before saving
df_clean.drop(columns=["table_name"], inplace=True)

# Save the updated merged data back to the same CSV file (or a new one if preferred)
updated_csv_path = "cleansed/rsi_data_merged.csv"
df_clean.to_csv(updated_csv_path, index=False)
print("Updated merged data saved to:", updated_csv_path)