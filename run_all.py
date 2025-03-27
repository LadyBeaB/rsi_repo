# run_all.py

import subprocess
import sys

# List of scripts in the order to execute
scripts = [
    "load_rsi_data_v2.py",
    "clean_contents_v2.py",
    "clean_notes.py",
    "clean_dual_table_worksheet_v2.py",
    "clean_multiheader_table.py",
    "clean_table_3_4_v3.py",
    "update_contents.py",
    "prep_rpi_data.py",
    "merge_agg_reference_v2.py",
    "rerun_table_3_4.py",
    "merge_rsi_data.py",
    "table_name_clean.py",
    "clean_table_5.py",
    "clean_table_6.py"
]
print("Running:", __file__)

# Execute each script in order
for script in scripts:
    print(f"Running {script} ...")
    result = subprocess.run(["python", script])
    if result.returncode != 0:
        print(f"Error running {script}. Exiting.")
        sys.exit(result.returncode)
    print(f"{script} completed successfully.\n")

print("✅ All scripts executed successfully!")
