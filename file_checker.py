from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import csv
import ctypes 
from datetime import datetime
import os



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
    "National_Opt_Out"
]


def file_dialog():
    '''
    Opens file dialog to find appropriate files
    '''
    root = Tk()
    root.withdraw()
    
    filetypes = (
        ('text files', '*.txt'),
        ('csv files', '*.csv')
    )
    
    filename = fd.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)
    '''
    showinfo(
        title='Selected File',
        message=filename
    )
    '''
    return filename


def load_file():
    '''
    Loads a CSV file. Formats each line as a dictionary. Saves dictionaries in a list.
    
    '''

    filename = file_dialog()
    #filename = "Good.csv" # debugging, hard coded file name (must be in same folder)

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

    for item in data:
        print(item)
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


def error_output(error_type = "Error", message = "Unable to verify file", affected_lines = [] ):
    '''
    Create dialog window for error processing file
    Write txt ouptut of details
    '''
    if affected_lines: #if the list of affected lines is not null
        message = message + "\nLine(s) "+ ", ".join(map(str,affected_lines))

    message = message +"\n"
    ctypes.windll.user32.MessageBoxW(0, message, error_type, 1)

    curpath = os.path.abspath(os.curdir)


    if not os.path.exists(OUT_FILENAME):
        open(OUT_FILENAME, "w")

    f = open( OUT_FILENAME, "a")
    f.write(error_type)
    f.write("\n")
    f.write(message)
    f.close()


if __name__ == "__main__":
    OUT_FILENAME = "out\\Checker_Output_Log"+ datetime.now().strftime("%H%M%S")+".txt"

    input_data = load_file()

    # 1:
    check_studyID(input_data)

    error_output("Test Error1", "Test message1", [1,2,3])
    error_output("Test Error2", "Test message2", [4,5,6])
    '''
    TODO list
    - Make check function:
        1.	Duplicate cases (STUDY_ID should be unique where ROW_STATUS="C") _/
        2.	No current case (each STUDY_ID needs one row where ROW_STATUS="C")
        3.	Non-valid variable names (note these are case sensitive in File 1)
        4.	Missing variable names (against File 1 spec)
        5.	Non-valid Date formats (must be DD/MM/YYYY)
        6.	Out of range values (for constrained fields)
        7.	Max 1024 variables per File (only applicable to File 2)

    - Make custom exception for "bad file"

    - Make example bad files:
        - Dupe Study_ID (where rows = c) _/ 
        - Dupe Study_IDs (where only one of the dupe = c)
        - Study_ID with no status = c
        - ... bad variable names (require closer look at spec) 
        - missing var names (one for each field ideally)
        - Non-valid Date formats (test with a selection of fields)
        - out of range vals (several checks for each bounded field)
        - file with 1023 vars, 1024 vars, 1025 vars, 99999 vars
        ....

    - Output errors
        - make txt file output + alert box?
        - alert relevant to the error type and directions to fix.
    '''

    

'''
Record of test files:
    Good.csv:               All in order - should pass
    StudyID_1.csv:          Line 1 and 4 studyID duplicated (and both lines ROW_STATUS = "c") - should fail, more than one row with C
    StudyID_2.csv:          Line 1 and 4 studyID duplicated (line 4 ROW_STATUS = "C", line 1 = "H") - should pass
    StudyID_3.csv:          Line 1 and 4 studyID duplicated (line 4 ROW_STATUS = "H", line 1 = "C") - should pass
    NullROW_STATUS_1.csv    Line 2 ROW_STATUS = "H" - should fail, no row with C
    NullROW_STATUS_2.csv    Lines 1 and 4 ROW_STATUS = "H" - should fail, no row with C
'''