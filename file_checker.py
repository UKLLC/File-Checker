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
    "NHS_S_Linkage_Permission",
    "NHS_S_Study_Number",
    "NHS_W_Linkage_Permission",
    "NHS_NI_Linkage_Permission",
    "NHS_NI_Study_Number",
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


def load_labelled_file(filename):
    '''
    Loads a CSV file. Read formatting. Formats each line as a dictionary. Saves dictionaries in a list.
    '''
    data = [] # setup to store csv contents as list of dictionaries
    with open(filename) as csv_file:    
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            line_count += 1
            data.append(row)

        print(f'File contains {line_count} entries.')            
    ''' Debugging
    for item in data:
        print(item)
    '''
    return data


def load_unlabelled_file(filename):
    '''
    Loads a CSV file. Assume formatted as in specification. Formats each line as a dictionary. Saves dictionaries in a list.
    '''
    data = [] # setup to store csv contents as list of dictionaries
    with open(filename) as csv_file:    
        csv_reader = csv.DictReader(csv_file, fieldnames = FILE_FORMAT, restkey="Overflow", restval="Underflow")
        line_count = 0
        for row in csv_reader:
            line_count += 1
            data.append(row)
            # Check if row contains expected number of variables
            if "Overflow" in row:
                error_output("Format Error", "Unexpected number of fields. Expected {}, present {}.".format(len(FILE_FORMAT), len(row["Overflow"])+len(FILE_FORMAT)), str(line_count))
            if "Underflow" in row.values():
                error_output("Format Error", "Unexpected number of fields. Expected {}, present {}.".format(len(FILE_FORMAT), len([item for item in row.values() if item != "Underflow"])), str(line_count))

        print(f'File contains {line_count} entries.')            

    ''' Debugging
    for item in data:
        print(item)
    '''
    return data

def load_file(filename = False):
    '''
    Get filename from dialog. Check headers of columns.
    If all variable names are as expected, load in given format.
    If some variable names are as expected, error and inform of bad naming
    If no variable names are present, load assuming format as in specification.

    '''

    if not filename: # if filename has not been passed (would only be for debugging/testing)
        filename = file_dialog()

    global out_filename
    out_filename = ("out\\{}_Output_Log".format(filename.split("\\")[-1].split(".")[0]))+STR_TIME
    
    try:
        with open(filename) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            headers = csv_reader.fieldnames

            # 1. All headers are the same
            difference = [x for x in headers if x not in FILE_FORMAT]
            if difference == [] and len(headers) == len(FILE_FORMAT):
                data = load_labelled_file(filename)

            # 2. No headers are the same (ie column names not included)
            elif len(difference) == len(headers):
                print("Headers not included")
                data = load_unlabelled_file(filename)
                error_output("Warning: field names not provided", "Column field names are not explicitly stated. Field name is assumed from position.", [0])

            # 3. Some headers are the same (ie some column names have likely been misnamed)
            else:
                print(len(difference), len(FILE_FORMAT), len(headers))
                error_output("Unrecognised field names", "Column field name(s) {} are not as expected. Unable to continue.".format(", ".join(difference)), [0])
                # Do not continue program
                return

    except OSError as e:
        error_output("Load Error", "Unable to read file")
        return

    content_checker(data)


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

def content_checker(input_data):
    check_studyID(input_data)


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

    if not os.path.exists(out_filename):
        open(out_filename, "w")

    f = open( out_filename, "a")


    f.write(error_type)
    f.write("\n")
    f.write(message)
    f.write("--------------------")
    f.close()


if __name__ == "__main__":
    # TODO - uncomment and remove debugging loop
    #STR_TIME = datetime.now().strftime("%H%M%S")+".txt"

    # Debugging:
    # List test cases to run sequentially (avoids file dialog for sake of speed)
    test_files = ["Good.csv","Good_unlabelled.csv","Bad_field_names.csv",
            "EXCEED_FILE1_v1_20210514.csv","UnderVals.csv","OverVals.csv",
            "StudyID_1.csv", "NullROW_STATUS_1.csv", "NullROW_STATUS_2.csv"]

    for filename in test_files:
        print("Testing file {}".format(filename))
        STR_TIME = datetime.now().strftime("%H%M%S")+".txt"
        input_data = load_file(filename)

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
        8.  Check expected number of columns (file 1)

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
    - Format tests
        Good.csv                        Column names correct - should pass
        Good_unlabelled.csv             No listed column names, correct ordering - should pass with warning
        Bad_field_names.csv             selection of incorrect field names - should fail to load
        EXCEED_FILE1_v1_20210514.csv    Proper file name - should be only file to pass with no errors (others will log errors from bad file name)
        UnderVals.csv                   (unlabelled) Too few columns - should fail to input
        OverVals.csv                    (unlabelled) Too many columns - should fail to input


    - Content tests 
        Good.csv                All in order - should pass
        StudyID_1.csv           Line 6,7 studyID duplicated (and both lines ROW_STATUS = "c") - should fail, more than one row with C
        NullROW_STATUS_1.csv    Line 6,7 ROW_STATUS = "H" - should fail, no row with C
        NullROW_STATUS_2.csv    Lines 1,2 and 6,7 ROW_STATUS = "H" - should fail, 2 cases of no row with C
'''