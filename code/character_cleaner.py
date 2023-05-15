##################################
# Created by Matt Crane 15/05/2023
# Purpose: quick solution to files containing unrecognised characters that cannot be fixed by manual means
# Process:
# 1. Select the file
# 2. Read the file into pandas with UTF-8 encoding
# 3. Save the file with a new name
##################################


import csv
import shared_functions as sf

if __name__ == "__main__":
    target_file = sf.file_dialog()
    rows = []
    with open(target_file, encoding="utf-8", errors="ignore") as csv_file: 
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            rows.append(",".join(row).encode(encoding="ascii", errors="ignore").decode())

    new_name = target_file.split(".")[0] + "_cleaned.csv"
    with open(new_name, "w", newline = "") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter =',')
        for row in rows:
            row_list = row.split(",")
            csv_writer.writerow(row_list)
    #file1.to_csv(new_name)
