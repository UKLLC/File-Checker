import os
from tkinter import *
from tkinter import filedialog as fd
from datetime import datetime
import re

def file_dialog():
    '''
    Opens file dialog to find appropriate files
    '''
    root = Tk()
    root.withdraw()
    
    filetypes = (
        ('csv files', '*.csv'),
        ('text files', '*.txt')
    )
    
    filename = fd.askopenfilename(
        title='Open a file',
        initialdir=os.getcwd(),
        filetypes=filetypes)

    return filename

def verify_date_format_DDMMYYYY(date):
    '''
    Non-valid Date formats (must be DD/MM/YYYY)
    '''
    date_format = '%d/%m/%Y'
    try:
        date_obj = datetime.strptime(date, date_format)
        return True
    except ValueError:
        # Though 00/00/[year] is not strictly a valid date, it is acceptable. 
        pattern = "00\/00\/[1,2][0-9]{3}|00\/[0,1][0-9]\/[1,2][0-9]{3}"
        if re.search(pattern, date):
            return True
        else:
            return False

def verify_date_format_YYYYMMDD(date):
    '''
    Non-valid Date formats (must be YYYY/MM/DD)
    '''
    date_format = '%Y%m%d'
    try:
        date_obj = datetime.strptime(date, date_format)
        return True
    except ValueError:
        return False


def reduce_output_list(lst):
    '''
    takes lists longer than 10 items and returns 10 items with an elipsis appended
    '''
    if len(lst) > 10:
        return lst[:10] + ["..."]
    return lst

def handle_Nones(data, outfile):
    '''
    Note if values are None and replace (for further checking)
    '''
    problem_lines = []
    for line in range(len(data)):
        for key, val in dict(data[line]).items():
            if val == None:
                data[line][key] = ""
                problem_lines.append(line)
    if len(problem_lines) > 0:

        error_output(outfile, "Warning: None value(s) in data", "None values should be represented by empty string ''. This warning could be indicative of short rows.", problem_lines)
    return data


def error_output(out_filename, error_type = "Error", message = "Unable to verify file", affected_lines = [] ):
    '''
    Create dialog window for error processing file
    Write txt ouptut of details
    '''
    if affected_lines != []: #if the list of affected lines is not null
        message = message + "\nLine(s) (ignoring header) "+ ", ".join(map(str,reduce_output_list(affected_lines)))

    message = message +"\n"

    if not os.path.exists(out_filename):
        open(out_filename, "w")

    f = open( out_filename, "a")

    f.write(error_type)
    f.write("\n")
    try:
        f.write(message)
    except UnicodeEncodeError:
        print("Encountered an error attempting to write '{}' to file due to an unrecognised character.".format(message))
        #encode() method
        print(message.encode(encoding="ascii", errors="replace").decode())
        cleaned_message = message.encode(encoding="ascii", errors="replace").decode()
        f.write(cleaned_message)
    f.write("--------------------\n")
    f.close()