'''
Much simpler version of the file 1 checker:
- check for file name
- check not empty
- check vars not in excess of 1024
'''
from datetime import datetime
import os
import shared_functions as sf
import constants 
import csv
import re



def load_file(filename = False):
    '''
    Get filename from dialog. Check headers of columns.
    If all variable names are as expected, load in given format.
    If some variable names are as expected, error and inform of bad naming
    If no variable names are present, load assuming format as in specification.

    '''
    print("Opening file dialog")
    if not filename: # if filename has not been passed (would only be for debugging/testing)
        filename = sf.file_dialog()

    global out_filename
    out_filename = ("{}_Output_Log".format(os.path.split(filename)[1].split(".")[0]))+STR_TIME

    #Check filename
    check_filename(filename)
    try:
        print("Loading data from file")
        with open(filename) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            headers = csv_reader.fieldnames

            # 1. All headers are the same
    except OSError as e:
        print("Unable to read file")
        sf.error_output(out_filename, "Load Error", "Unable to read file")
        return

    content_checker(headers)


def check_filename(filename):
    '''
    Check filename abides by file 1 naming convention:
    <UK LLC Study Code>_<tablename>_<”v” & version number>_<version dateYYYYMMDD>.csv
    e.g., EXCEED_COVIDWAVE1_v0001_20210514.csv
    '''
    print("Checking filename")
    filename_sections = os.path.split(filename)[1].split("_")
    if len(filename_sections) < 4:
        sf.error_output(out_filename,"File Naming Error", "Filename does not match the naming convention. Should include at least 4 underscore separated sections.")
        return

    study_code = filename_sections[0]
    table_name = "_".join(filename_sections[1:-2])
    version = filename_sections[-2]
    creation_date = filename_sections[-1].split(".")[0]

    if not study_code in constants.UK_LLC_STUDY_CODES:
        # If no matches, check if study_code is "_" separated like (NIRHBIO_COPING) and adjust
        study_code = filename_sections[0]+"_"+filename_sections[1]
        if study_code in constants.UK_LLC_STUDY_CODES:
            # Adjust table name range
            table_name = "_".join(filename_sections[2:-2])
        else:
            sf.error_output(out_filename,"File Naming Error", "Study identifier not recognised. Make sure the leading part of the filename is among our listed recognised study identifiers.")

    if len(table_name) == 0:
        sf.error_output(out_filename,"File Naming Error", "Filename does not match the naming convention. Should include a unique table name following the study code.")

    version_format = re.compile("v[0-9]{4}")
    version_match = version_format.match(version)
    if not version_format.match(version) or len(version)!= version_match.end():
        sf.error_output(out_filename,"File Naming Error", "Filename does not match the naming convention. Should include 4 digit integer version number.")

    creation_date_format = re.compile("[0-9]{8}")
    if len(creation_date) != 8 or not creation_date_format.match(creation_date) or not sf.verify_date_format_YYYYMMDD(creation_date):
        sf.error_output(out_filename,"File Naming Error", "Filename does not match the naming convention. Should include creation date in the format YYYYMMDD.")


def content_checker(headers):
    '''
    Check number of vars < 2014
    check includes study_ID
    Study status?
    '''
    if len(headers)> 1024:
        sf.error_output(out_filename, "File Format Error", "File exceeds the permitted number of columns (Maximum: {}, present: {}).".format(1024, len(headers)))

    if not "STUDY_ID" in headers:
        sf.error_output(out_filename, "File Format Error", "File does not include 'STUDY_ID' column.")



if __name__ == "__main__":

    STR_TIME = datetime.now().strftime("%H%M%S")+".txt"

    input_data = load_file()
    #If no errors logged
    if not os.path.exists(out_filename):
        f = open( out_filename, "w")
        f.write("File passed all checks.")

'''
Record of Test Files:   
    - EXCEED_COVIDWAVE1_v0001_20210514.csv      Example 1 of acceptable file format. Should pass.
    - EXCEED_COVID_w1_v0001_20210514.csv        Example 2 of acceptable file format. Should pass.

    - EXCEED_v0001_20210514.csv                 Missing table name. Should error.
    - EXCEED_COVIDWAVE1_v01_20210514.csv        Incorrect version name. Should error.
    - EXCEED_COVID_WAVE1_20210514.csv            Missing version name. Should error.
    - EXCEED_COVIDWAVE1_v0001_14052021          Incorrect date format. Should error
    - EXCEED_COVID_WAVE1_v0001.csv               Missing date. Should error.
    - EXCED_COVIDWAVE1_v0001_20210514.csv       Incorrect study name. Should error.
    - COVIDWAVE1_v0001_20210514.csv             Missing study name. Should error.

    - all_bad.csv                               Includes 1025 columns. Does not include STUDY_ID column. Should error twice.
    - 


'''
