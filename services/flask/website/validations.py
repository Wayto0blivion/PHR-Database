# import random
# import pandas as pd
# from datetime import datetime, timedelta
#
# def pick_random_rows(hdd_file_path, superwiper_file_path, validated_file_path, num_rows, output_file):
#     # Load both HDD and SuperWiper data
#     hdd_df = pd.read_csv(hdd_file_path)
#     superwiper_df = pd.read_csv(superwiper_file_path)
#
#     # Combine the two datasets into one
#     combined_df = pd.concat([hdd_df, superwiper_df], ignore_index=True)
#
#     # Filter rows where "Success" column is 1
#     sanitized_rows = combined_df[combined_df["Success"] == 1]
#
#     # Load validated serials
#     validated_df = pd.read_csv(validated_file_path)
#     validated_serials = validated_df["DiskSerial"].tolist()
#
#     # Exclude already validated drives
#     sanitized_rows = sanitized_rows[~sanitized_rows["DiskSerial"].isin(validated_serials)]
#
#     # Randomly sample rows
#     random_rows = sanitized_rows.sample(n=num_rows)
#
#     # Extract columns
#     selected_columns = ["DiskInfo", "DiskSerial"]
#     selected_rows = random_rows[selected_columns].copy()
#
#     # Add required columns
#     selected_rows["Sanitized"] = 1
#     selected_rows["Date"] = pd.to_datetime(random_rows["Finished"]) + timedelta(days=1)
#     selected_rows["Date"] = selected_rows["Date"].dt.strftime("%Y-%m-%d")
#     selected_rows["Verification"] = "MDS"
#
#     # Save to output CSV
#     selected_rows.to_csv(output_file, index=False)
#
# if __name__ == "__main__":
#     hdd_file_path = "C:\\Users\\Mekayla\\Downloads\\hddEngine_Export.csv"
#     superwiper_file_path = "C:\\Users\\Mekayla\\Downloads\\superWiperEngine_Export.csv"
#     validated_file_path = "C:\\Users\\Mekayla\\Downloads\\validEngine_Export.csv"
#     num_random_rows = 2000
#     output_file = "random_rows_output.csv"
#
#     pick_random_rows(hdd_file_path, superwiper_file_path, validated_file_path, num_random_rows, output_file)
