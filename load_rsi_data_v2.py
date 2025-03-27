# load_rsi_data.py

import pandas as pd

def get_excel_file():
    """Load the main Excel workbook."""
    excel_path = 'data/mainreferencetables.xlsx'
    return pd.ExcelFile(excel_path)

def get_csv_data():
    """Load the series CSV file."""
    csv_path = 'data/series-210325.csv'
    return pd.read_csv(csv_path)

def list_sheet_names(xls):
    """Print all available sheet names from the Excel file."""
    print("Sheets in workbook:", xls.sheet_names)

# def preview_all_sheets(xls, rows=5):
   # """Preview top rows from all Excel sheets."""
   # for sheet in xls.sheet_names:
   #     print(f"\n--- Preview of '{sheet}' ---")
   #     df = xls.parse(sheet)
   #     print(df.head(rows))

# def preview_csv(df_csv, rows=5):
   # """Preview top rows from the CSV file."""
   # print(f"\n--- Preview of CSV file ---")
   # print(df_csv.head(rows))


# Test block: Only runs when this file is executed directly
if __name__ == "__main__":
    # Load both files
    xls = get_excel_file()
    df_csv = get_csv_data()

    # Test previews
    list_sheet_names(xls)
    # preview_all_sheets(xls)
    # preview_csv(df_csv)