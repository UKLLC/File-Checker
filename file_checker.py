from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import csv


FILE_FORMAT = [
    "STUDY_ID",
    "ROW_STATUS",
    "NHS_NUMBER",
    "SURNAME",
    "FORENAME",
    "MIDDLENAMES",
    "ADDRESS_1",
    "ADDRESS_2",
    "ADDRESS_3",
    "ADDRESS_4",
    "ADDRESS_5",
    "POSTCODE",
    "ADDRESS_START_DATE",
    "ADDRESS_END_DATE",
    "DATE_OF_BIRTH",
    "GENDER_CD",
    "CREATE_DATE",
    "UKLLC_STATUS",
    "NHS_E_Linkage_Permission",
    "NHS_Digital_Study_Number",
    "NHS_S_Linkage Permission",
    "NHS_S_Study_Number",
    "NHS_W_Linkage_Permission",
    "NHS_NI_Linkage_Permission",
    "NHS_NI_Study Number",
    "Geocoding_Permission",
    "ZoeSymptomTracker_Permission",
    "Multiple_Birth",
    "National_Opt_Out",
]

def file_dialog():
    '''
    Opens file dialog to find appropriate files
    '''
    filetypes = (
        ('text files', '*.txt'),
        ('csv files', '*.csv')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    showinfo(
        title='Selected File',
        message=filename
    )
    return filename


def load_file():
    '''
    Loads a CSV file. Formats each line as a dictionary. Saves dictionaries in a list.
    
    '''

    filename = file_dialog()
    #filename = "Good File.csv" # debugging, hard coded file name (must be in same folder)

    data = [] # setup to store csv contents as list of dictionaries

    try:
        with open(filename) as csv_file:
            
            csv_reader = csv.DictReader(csv_file, fieldnames = FILE_FORMAT)
            line_count = 0
            for row in csv_reader:
       
                line_count += 1
                data.append(row)

            print(f'File contains {line_count} entries.')

    except OSError as e:
        print(e)

    print(data)
    return data


def check_studyID(input_data):
    '''
    Duplicate cases (STUDY_ID should be unique where ROW_STATUS="C")
    '''
    reduced_data = [] 
    # include only rows where ROW_STATUS == c
    for row in input_data:
        if row["ROW_STATUS"].lower() == "c":
            reduced_data.append(row)
    
    studyIDs = [item["STUDY_ID"] for item in reduced_data]
    
    if len(studyIDs) != len(set(studyIDs)):
        print("dupes")
        # TODO
        # Raise custom exception
        # identify lines? 
    else:
        print("Study_ID pass")


def check_current_case(input_data):
    '''
    No current case (each STUDY_ID needs one row where ROW_STATUS="C")
    '''
    pass


def check_valid_var_names(input_data):
    '''
    Non-valid variable names (note these are case sensitive in File 1)
    '''
    pass


def check_missing_var_names(input_data):
    '''
    Missing variable names (against File 1 spec)
    '''
    pass


def check_date_formats(input_data):
    '''
    Non-valid Date formats (must be DD/MM/YYYY)
    '''
    pass


def check_out_of_range(input_data):
    '''
    Out of range values (for constrained fields)
    '''
    pass


def check_max_variables(input_data):
    '''
    Max 1024 variables per File (only applicable to File 2)
    '''
    pass



if __name__ == "__main__":
    input_data = load_file()

    '''
    TODO list
    - Make check function:
        1.	Duplicate cases (STUDY_ID should be unique where ROW_STATUS="C")
        2.	No current case (each STUDY_ID needs one row where ROW_STATUS="C")
        3.	Non-valid variable names (note these are case sensitive in File 1)
        4.	Missing variable names (against File 1 spec)
        5.	Non-valid Date formats (must be DD/MM/YYYY)
        6.	Out of range values (for constrained fields)
        7.	Max 1024 variables per File (only applicable to File 2)

    - Make custom exception for "bad file"
    
    '''

    # 1:
    check_studyID(input_data)