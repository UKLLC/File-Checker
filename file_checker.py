from tkinter import *
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import csv
import ctypes 
from datetime import datetime
import os
import re
import time

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

    return data


def load_unlabelled_file(filename):
    '''
    Loads a CSV file. Assume formatted as in specification. Formats each line as a dictionary. Saves dictionaries in a list.
    '''
    data = [] # setup to store csv contents as list of dictionaries
    with open(filename) as csv_file:    
        csv_reader = csv.DictReader(csv_file, fieldnames = FILE_FORMAT, restkey="Overflow", restval="Underflow")
        line_count = 0

        overflow = {}
        underflow = {}
        for row in csv_reader:
            line_count += 1
            data.append(row)
            # Check if row contains expected number of variables
            if "Overflow" in row:
                overflow[str(line_count)] = len(row["Overflow"])+len(FILE_FORMAT)
            if "Underflow" in row.values():
                underflow[str(line_count)] = len([item for item in row.values() if item != "Underflow"])+len(FILE_FORMAT)

        print(f'File contains {line_count} entries.')            

        if overflow != {}:
            lines = list(overflow.keys())
            sizes = list(overflow.values())
            error_output("Format Error", "Unexpected number of fields. Expected {}, present {}.".format(len(FILE_FORMAT), reduce_output_list(sizes)), lines)

        if underflow != {}:
            lines = list(underflow.keys())
            sizes = list(underflow.values())
            error_output("Format Error", "Unexpected number of fields. Expected {}, present {}.".format(len(FILE_FORMAT), reduce_output_list(sizes)), lines)

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

# ------------------------------------- 
# Checker functions

def get_primary_rows(input_data):
    '''
    Reduce data to rows where ROW_STATUS == "C" (primary row per participant)
    '''
    return [row for row in input_data if row["ROW_STATUS"].lower() == "c"] 

def verify_date_format(date):
    '''
    Non-valid Date formats (must be DD/MM/YYYY)
    '''
    date_format = '%d/%m/%Y'
    try:
        date_obj = datetime.strptime(date, date_format)
        return True
    except ValueError:
        return False
    
def verify_varchar(var, length, nullAllowed = True):
    '''
    Check variable (string) is of a certain length
    '''
    if (len(var) <= length and len(var)>0) or (nullAllowed and len(var) == 0):
        return True
    return False

def verify_char(var, legal_chars = [], nullAllowed = True):
    '''
    Check variable is a character and of legal permutations
    '''
    if (len(var) == 1 and var in legal_chars) or (nullAllowed and len(var) == 0):
        return True
    else:
        return False 


def check_studyID(input_data):
    '''
    Duplicate cases (STUDY_ID should be unique where ROW_STATUS="C")
    '''
    studyIDs = [item["STUDY_ID"] for item in get_primary_rows(input_data)]
    problem_ids = []
    for id in studyIDs:
        if studyIDs.count(id) > 1:
            problem_ids.append(id)
    if problem_ids:
        error_output("Duplicate Current Record", "File contains multiple rows where ROW_STATUS = 'C' for STUDY_ID(s) {}.".format(reduce_output_list(list(set(problem_ids)))))

def check_current_case(input_data):
    '''
    No current case (each STUDY_ID needs one row where ROW_STATUS="C")
    '''
    primary_studyIDs = [item["STUDY_ID"] for item in get_primary_rows(input_data)]
    all_studyIDs = set([row["STUDY_ID"] for row in input_data])

    problem_ids = []
    for id in all_studyIDs:
        if id not in primary_studyIDs:
            problem_ids.append(id)
    error_output("No Current Record", "File contains no current record for STUDY_ID(s) {}".format(reduce_output_list(list(set(problem_ids)))))

def check_NHS_number(input_data):
    '''
    Make sure NHS number conforms to requirements:
        precisely 10 digits or null
        no spaces
    '''
    NHS_numbers = [row["NHS_NUMBER"] for row in input_data]
    problem_lines = []
    for i in range(len(NHS_numbers)):
        number = NHS_numbers[i]
        if number:
            if len(number) != 10 and len(number) != 0 and len(number.split(" ")) == 1:
                problem_lines.append(i +1)
    if problem_lines:
        error_output("NHS Number Format Error", "NHS number of unexpected length. Please ensure NHS numbers include 10 characters and no spaces", problem_lines)

def check_postcode(input_data):
    '''
    Check postcode is of one of three formats:
        4 & 3 = “YYYY ZZZ”
	    3 & 3 = “YYY  ZZZ”
        2 & 3 = “YY   ZZZ”
    '''
    postcodes = [row["POSTCODE"] for row in input_data]
    problem_lines = []
    for i in range(len(postcodes)):
        postcode = postcodes[i]
        if postcode:
            reduced_postcode = postcode.replace(" ", "")
            if not len(reduced_postcode) == len(postcode)-1:
                problem_lines.append(i + 1)
            else:
                #e.g. XX YYY
                if len(postcode) == 6:
                    pattern = re.compile("^[a-zA-Z]{1}[0-9]{2}[a-zA-Z]{2}")
                #e.g. XXX YYY
                elif len(postcode) == 7:
                    pattern = re.compile("^[a-zA-Z]{2}[0-9]{2}[a-zA-Z]{2}")
                #e.g. XXXX YYY
                elif len(postcode) == 8:
                    pattern = re.compile("^[a-zA-Z]{2}[0-9]{3}[a-zA-Z]{2}")

                if not pattern.match(reduced_postcode):
                    problem_lines.append(i + 1)

    if problem_lines:
        error_output("Postcode Format Error", "Postcode of unexpected format. Postcodes should be of the form 'YYYY ZZZ', 'YYY ZZZ' or 'YY ZZZ', including a space.", problem_lines)


def check_dates(input_data):
    '''
    Identifies fields with dates in them. Checks dates are of the format DD/MM/YYY.
    Only checks formats - does not check dates are reasonable (no assumptions made about contents)
    '''
    date_fields = [field for field in FILE_FORMAT if "DATE" in field]

    for date_field in date_fields:
        problem_rows = []
        for date_index in range(len(input_data)):
            date = input_data[date_index][date_field]
            if len(date) > 1: 
                if not verify_date_format(date):
                    problem_rows.append(date_index+1)
        if problem_rows:
            error_output("Date Format Error", "Invalid format for field {}. Date should be in the format DD/MM/YYYY".format(date_field), problem_rows)

def check_vars(input_data):
    '''
    '''
    error_dict = dict((el,[]) for el in FILE_FORMAT)
    
    for row_index in range(len(input_data)):
        # "STUDY_ID", varchar(50)
        if not verify_varchar(input_data[row_index]["STUDY_ID"], 50, nullAllowed=False):
            error_dict["STUDY_ID"].append(row_index + 1)
        # "ROW_STATUS", char(1), [C,H]
        if not verify_char(input_data[row_index]["ROW_STATUS"], ["C","H"], nullAllowed=False):
            error_dict["ROW_STATUS"].append(row_index + 1)
        # "SURNAME", varchar(255)
        if not verify_varchar(input_data[row_index]["SURNAME"], 255, nullAllowed=True):
            error_dict["SURNAME"].append(row_index + 1)
        # "FORENAME", varchar(255)
        if not verify_varchar(input_data[row_index]["FORENAME"], 255, nullAllowed=True):
            error_dict["FORENAME"].append(row_index + 1)
        # "MIDDLENAMES", varchar(255), (expecting a list of names, space deliminated)
        if not verify_varchar(input_data[row_index]["MIDDLENAMES"], 255, nullAllowed=True):
            error_dict["MIDDLENAMES"].append(row_index + 1)
        # "ADDRESS_1", varchar("255")
        if not verify_varchar(input_data[row_index]["ADDRESS_1"], 255, nullAllowed=True):
            error_dict["ADDRESS_1"].append(row_index + 1)
        # "ADDRESS_2", varchar("255")
        if not verify_varchar(input_data[row_index]["ADDRESS_2"], 255, nullAllowed=True):
            error_dict["ADDRESS_2"].append(row_index + 1)
        # "ADDRESS_3", varchar("255")
        if not verify_varchar(input_data[row_index]["ADDRESS_3"], 255, nullAllowed=True):
            error_dict["ADDRESS_3"].append(row_index + 1)
        # "ADDRESS_4", varchar("255")
        if not verify_varchar(input_data[row_index]["ADDRESS_4"], 255, nullAllowed=True):
            error_dict["ADDRESS_4"].append(row_index + 1)
        # "ADDRESS_5", varchar("255")
        if not verify_varchar(input_data[row_index]["ADDRESS_5"], 255, nullAllowed=True):
            error_dict["ADDRESS_5"].append(row_index + 1)
        # "ADDRESS_START_DATE", varchar("10")
        if not verify_varchar(input_data[row_index]["ADDRESS_START_DATE"], 10, nullAllowed=True):
            error_dict["ADDRESS_START_DATE"].append(row_index + 1)
        # "ADDRESS_END_DATE", varchar("10")
        if not verify_varchar(input_data[row_index]["ADDRESS_END_DATE"], 10, nullAllowed=True):
            error_dict["ADDRESS_END_DATE"].append(row_index + 1)
        # "DATE_OF_BIRTH", varchar("10")
        if not verify_varchar(input_data[row_index]["DATE_OF_BIRTH"], 10, nullAllowed=True):
            error_dict["DATE_OF_BIRTH"].append(row_index + 1)
        # "GENDER_CD", char(1)
        if not verify_char(input_data[row_index]["GENDER_CD"], ["1", "2", "7", "8", "9"], nullAllowed=True):
            error_dict["GENDER_CD"].append(row_index + 1)
        # "CREATE_DATE", varchar("10")
        if not verify_varchar(input_data[row_index]["CREATE_DATE"], 10, nullAllowed=True):
            error_dict["CREATE_DATE"].append(row_index + 1)
        # "UKLLC_STATUS", char(1)
        if not verify_char(input_data[row_index]["UKLLC_STATUS"], ["1", "0"], nullAllowed=True):
            error_dict["UKLLC_STATUS"].append(row_index + 1)
        # "NHS_E_Linkage_Permission", char(1)
        if not verify_char(input_data[row_index]["NHS_E_Linkage_Permission"], ["1", "0"], nullAllowed=True):
            error_dict["NHS_E_Linkage_Permission"].append(row_index + 1)
        # "NHS_Digital_Study_Number", varchar(50)
        if not verify_varchar(input_data[row_index]["NHS_Digital_Study_Number"], 50, nullAllowed=True):
            error_dict["NHS_Digital_Study_Number"].append(row_index + 1)
        # "NHS_S_Linkage_Permission", char(1)
        if not verify_char(input_data[row_index]["NHS_S_Linkage_Permission"], ["1", "0"], nullAllowed=True):
            error_dict["NHS_S_Linkage_Permission"].append(row_index + 1)
        # "NHS_S_Study_Number", varchar(50)
        if not verify_varchar(input_data[row_index]["NHS_S_Study_Number"], 50, nullAllowed=True):
            error_dict["NHS_S_Study_Number"].append(row_index + 1)
        # "NHS_W_Linkage_Permission", char(1)
        if not verify_char(input_data[row_index]["NHS_W_Linkage_Permission"], ["1", "0"], nullAllowed=True):
            error_dict["NHS_W_Linkage_Permission"].append(row_index + 1)
        # "NHS_NI_Linkage_Permission", char(1)
        if not verify_char(input_data[row_index]["NHS_NI_Linkage_Permission"], ["1", "0"], nullAllowed=True):
            error_dict["NHS_NI_Linkage_Permission"].append(row_index + 1)
        # "NHS_NI_Study_Number", varchar(50)
        if not verify_varchar(input_data[row_index]["NHS_NI_Study_Number"], 50, nullAllowed=True):
            error_dict["NHS_NI_Study_Number"].append(row_index + 1)
        # "Geocoding_Permission", char(1)
        if not verify_char(input_data[row_index]["Geocoding_Permission"], ["2","1", "0"], nullAllowed=True):
            error_dict["Geocoding_Permission"].append(row_index + 1)
        # "ZoeSymptomTracker_Permission", char(1)
        if not verify_char(input_data[row_index]["ZoeSymptomTracker_Permission"], ["1", "0"], nullAllowed=True):
            error_dict["ZoeSymptomTracker_Permission"].append(row_index + 1)
        # "Multiple_Birth", char(1)
        if not verify_char(input_data[row_index]["Multiple_Birth"], ["1", "0", "9"], nullAllowed=True):
            error_dict["Multiple_Birth"].append(row_index + 1)
        # "National_Opt_Out", char(1)
        if not verify_char(input_data[row_index]["National_Opt_Out"], ["1", "0"], nullAllowed=True):
            error_dict["National_Opt_Out"].append(row_index + 1)

    for key, value in error_dict.items():
        if error_dict[key] != []:
            error_output("Value Error",
            "Invalid value for field {}. Please refer to the specification for correct field formatting guidelines.".format(key),
            value)

    #handle NHS number, postcode separately (more requirements than other variables)
    check_NHS_number(input_data)
    check_postcode(input_data)


def check_max_variables(input_data):
    '''
    Max 1024 variables per File (only applicable to File 2)
    '''
    pass

def content_checker(input_data):
    check_studyID(input_data)
    check_current_case(input_data)
    check_dates(input_data)
    check_vars(input_data)

#----------------------------

def reduce_output_list(lst):
    '''
    takes lists longer than 10 items and returns 10 items with an elipsis appended
    '''
    if len(lst) > 10:
        return lst[:10].append("...")
    return lst

def error_output(error_type = "Error", message = "Unable to verify file", affected_lines = [] ):
    '''
    Create dialog window for error processing file
    Write txt ouptut of details
    '''
    if affected_lines: #if the list of affected lines is not null
        message = message + "\nLine(s) "+ ", ".join(map(str,reduce_output_list(affected_lines)))

    message = message +"\n"
    # May or may not want to include message boxes. Potetentially not, unless outputs are cleaned up.
    #ctypes.windll.user32.MessageBoxW(0, message, error_type, 1)

    curpath = os.path.abspath(os.curdir)

    if not os.path.exists(out_filename):
        open(out_filename, "w")

    f = open( out_filename, "a")


    f.write(error_type)
    f.write("\n")
    f.write(message)
    f.write("--------------------\n")
    f.close()


if __name__ == "__main__":
    # TODO - uncomment and remove debugging loop
    #STR_TIME = datetime.now().strftime("%H%M%S")+".txt"

    # Debugging:
    # List test cases to run sequentially (avoids file dialog for sake of speed)
    test_files = ["Good.csv","Good_unlabelled.csv","Bad_field_names.csv",
            "EXCEED_FILE1_v1_20210514.csv","UnderVals.csv","OverVals.csv",
            "StudyID_1.csv", "NullROW_STATUS_1.csv", "NullROW_STATUS_2.csv",
            "bad_NHS_NUMBER.csv", "bad_date_format1.csv", "bad_date_format2.csv",
            "bad_date_format2.csv","bad_date_range.csv", "general_bad.csv",
            "big_bad.csv"]

    for filename in test_files:
        print("Testing file {}".format(filename))
        STR_TIME = datetime.now().strftime("%H%M%S")+".txt"
        start = time.time()
        input_data = load_file(filename)
        print("Duration: ", start - time.time())

    '''
    TODO list
    - Make check function:
        1.	Duplicate cases (STUDY_ID should be unique where ROW_STATUS="C") _/
        2.	No current case (each STUDY_ID needs one row where ROW_STATUS="C") _/
        3.	Non-valid variable names (note these are case sensitive in File 1) _/
        4.	Missing variable names (against File 1 spec) _/
        5.	Non-valid Date formats (must be DD/MM/YYYY) _/
        6.	Out of range values (for constrained fields) _/
        7.	Max 1024 variables per File (only applicable to File 2)
        8.  Check expected number of columns (file 1) _/
        9.  check null entires are correct _/
        10. Check valid variable combinations: can only have a start date if have an address
    - TODO make sure all ouputs are not line by line (too slow for big files)
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
        bad_NHS_NUMBER.csv      line 3 contains spaces, line 6 too few characters - should fail twice

        bad_date_format1.csv    Date of format YYYY/MM/DD in ADDRESS_START_DATE - should fail
        bad_date_format2.csv    1 or 2 dates of format YYYY/MM/DD in every date field - should fail twice for each date field
        bad_date_format3.csv    2 dates of format MM/DD/YYYY, one with day > 12, one with day <= 12 - should fail once, but unable to identify second
        bad_date_range.csv      1 date of format DD/MM/YYYY where DD>31, 1 date of formate DD/MM/YYYY where MM>12 - should fail
        - Note, not checking dates are reasonable, just checking format. eg, Date 01/01/1800 would be acceptable.

        general_bad.csv         At least one invalid value per field (invalid by length or illegal characters) - should error at least once per field
            STUDY_ID - 60 characters, null
            ROW_STATUS - "CH", "D", null
            NHS_NUMBER - "12345678901234567890", "123 1244 214"
            SURNAME - 256 characters
            FORENAME - ""
            MIDDLENAME - ""
            ADDRESS_1 (only) - 256+ characters
            POSTCODE - "ABC 2BA", "ABCD 3DE", "A123 4DE", "AB1 23C", "AA 1BE"
            ADDRESS_START_DATE - 01/01/20011
            (Skip other dates)
            GENDER_CD - "3", "a", "01"
            UKLLC_STATUS - "00", "3", "a"
            NHS_DIGITAL_STUDY_NUMBER - 51+ characters
            GEOCODING PERMISSION - "3", "02", "a"

    - Scalability check:
        big_bad.csv     general_bad duplicated many times to make 100,000 rows
'''