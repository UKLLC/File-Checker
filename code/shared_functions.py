import os
from tkinter import *
from tkinter import filedialog as fd
from datetime import datetime

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


def reduce_output_list(lst):
    '''
    takes lists longer than 10 items and returns 10 items with an elipsis appended
    '''
    if len(lst) > 10:
        return lst[:10] + ["..."]
    return lst


def error_output(out_filename, error_type = "Error", message = "Unable to verify file", affected_lines = [] ):
    '''
    Create dialog window for error processing file
    Write txt ouptut of details
    '''
    if affected_lines != []: #if the list of affected lines is not null
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
    f.close(), 1