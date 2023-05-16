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
import pandas as pd

if __name__ == "__main__":
    target_file = sf.file_dialog()

    csv_file = pd.read_csv(target_file, encoding="utf-8")
    print([col for col in csv_file.columns])
    csv_file.columns = [str(col).encode('ascii', 'ignore').decode('ascii') for col in csv_file.columns]
    for column in csv_file.columns:
        csv_file[column] = [str(col).encode('ascii', 'ignore').decode('ascii') for col in csv_file[column]]
        
    new_name = target_file.split(".")[0] + "_cleaned2.csv"
    csv_file.to_csv(new_name, encoding="ascii", index = False)

    print(csv_file.columns)
