# import random
# import pandas as pd
# from datetime import datetime, timedelta
#
# def pick_random_rows(file_path, num_rows, output_file):
#     df = pd.read_csv(file_path)  # Assuming you have a CSV file named "hddEngine_Export.csv"
#
#     # Filter rows where "Success" column is 1
#     sanitized_rows = df[df["Success"] == 1]
#
#     # Randomly sample rows
#     random_rows = sanitized_rows.sample(n=num_rows)
#
#     # Extract columns
#     selected_columns = ["DiskInfo", "DiskSerial"]
#     selected_rows = random_rows[selected_columns].copy()
#
#     # Convert "Success" column values to True/False based on the value
#     selected_rows["Sanitized"] = True
#
#     # Convert "Finished" column to datetime and add 1 day
#     selected_rows["Date"] = pd.to_datetime(random_rows["Finished"]) + timedelta(days=1)
#
#     # Extract only the date part without the timestamp
#     selected_rows["Date"] = selected_rows["Date"].dt.strftime("%Y-%m-%d")
#
#     selected_rows.to_csv(output_file, index=False)  # Write to CSV file
#
# if __name__ == "__main__":
#     csv_file_path = "C:\\Users\\Mekayla\\Downloads\\hddEngine_Export.csv"  # Update with your CSV file path
#     num_random_rows = 240  # Number of random rows to pick
#     output_file = "random_rows_output.csv"  # Output file name
#
#     pick_random_rows(csv_file_path, num_random_rows, output_file)
#



