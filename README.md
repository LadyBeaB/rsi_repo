load_rsi_data_v2.py - loads both files
clean_contents_v2.py - extracts contents 
clean_notes.py - exrtacts notes
clean_dual_table_worksheet_v2.py - CPSA:KPSA 1-4, Table ID* - added frequency
clean_multiheader_table.py - Table 1-2 A,Q,M, 5 header, 3 header, handles AGG21/X "All retailing, including..." vs "All retailing including"
clean_table_3_4_v3.py - Table 3-4 A,Q,M, missing agg - unmatched_log, retain time_period_description for now for lookup in rerun
update_contents.py - series-210325, update cleaned_contents.csv - no duplicates
prep_rpi_data.py - series-210325 - preps the data for merge
clean_table_5.py - no agg_sic_code, dataset_code labeled instead, not fully normalised
clean_table_6.py - new table - [c] confidential, null left
merge_agg_reference_v2.py - cleanse note_ref, sales_in_2022, clean time_period_description, add 2 missing agg_sic_code manuall text, move files once done, log of duplicates
rerun_table_3_4.py - lookup agg_sic_code in agg_reference_merged.csv and fill, drop time_period_description 
merge_rsi_data.py - agg_sic_code all CAPS, no spaces, merge all files including Retail Sales Index data with the RPI data, year, month column (0 on annual and quarter convert to int)   
table_name_clean.py - create table_name table, replaces tabel_name with table_code, uid
run_all.py - executes all above in one go
