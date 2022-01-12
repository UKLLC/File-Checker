from tkinter import *
from tkinter import filedialog as fd
import os
import csv
from datetime import datetime

def error_output(out_filename, error_type = "Error", message = "Unable to verify file"):
    '''
    Create dialog window for error processing file
    Write txt ouptut of details
    '''
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


def main():
    # Load file
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

    out_filename = ("{}_Output_Log".format(os.path.split(filename)[1].split(".")[0]))+datetime.now().strftime("%H%M%S")+".txt"

    '''
    Try to read a file, line by line, without specifying encoding. Raise warning if can't be read
    '''
    bad_encoding = False
    error = None
    line_count = 0
    with open(filename) as csv_file:
        try:
            csv_reader = csv.DictReader(csv_file)
            for _ in csv_reader:
                line_count += 1
        except UnicodeDecodeError as err:
            error = err
            bad_encoding = True
    
    with open(filename, encoding="utf-8") as csv_file:
        try:
            csv_reader = csv.DictReader(csv_file)
            for _ in csv_reader:
                line_count += 1
        except UnicodeDecodeError as err:
            error = err
            bad_encoding = True

    if bad_encoding:
        print("Encoding Error. File cannot be read by certain functions. This is likely caused by unrecognised characters. The following error will help you identify the location of the first problematic character. The position refers to the index of the character in the entire file.\n Python Error: {}".format(error))
        error_output(out_filename, "File Encoding Error", "File cannot be read by certain functions. This is likely caused by unrecognised characters. The following error will help you identify the location of the first problematic character. The position refers to the index of the character in the entire file.\nPython Error: {}".format(error))
        error_output(out_filename, "", "Often the unrecognised characters will not be clear, appearing to be regular spaces or quotation marks. You can narrow down the location of the characters by copying the file, removing sections and repeatedly running this check, observing how the position referenced in the error changes." )
    else:
        print("File loaded without issue")
        if not os.path.exists(out_filename):
            f = open( out_filename, "w")
            f.write("File loaded without issue.")

    input("\nPress enter to close...")

if __name__ == "__main__":
    main()