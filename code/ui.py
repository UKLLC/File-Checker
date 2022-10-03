from re import L
import tkinter as tk
from tkinter import ttk
from tkinter import font
from datetime import datetime
from turtle import bgcolor
import shared_functions as sf
import UK_LLC_File_1_Checker as f1
import threading

class WrappingLabel(tk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        tk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))



class MainUI:
    def show_output(self, out_file):
        content = open(out_file, mode="r").read()
        self.check_text.insert(tk.END, content)
        print(content)
        
    def load_file1(self):
        self.filename = sf.file_dialog()
        if self.filename == "":
            return
        self.set_loaded_filename(self.filename)

        self.reset_progress_bar()
        self.reset_output()
        # TODO
        #wipe progress text
        self.reset_progress()
        # wipe file 1 doc entries

    def start_checks(self):
        if not self.filename: # If user has not yet loaded a file
            self.load_file1()
        if self.filename == "": # If file selection is cancelled
            return
        try:
            p = threading.Thread(target = self.check_staging).start()
        except FileNotFoundError:
            print("File not loaded")
        self.check_in_progress_txt()

    def check_staging(self):
        f1.load_file(self.filename, self)
        self.check_complete_txt()


    def show_output(self, out_file):
        content = open(out_file, mode="r").read()
        self.check_text.insert(tk.END, content)
        print(content)


    def update_progress_bar(self):
        self.root.update_idletasks()
        self.pb1['value'] += (100/12) + 0.001


    def get_loaded_filename(self):
        return self.loaded_filename

    def make_entries(self, fields):
        entries = {}
        for field in fields:
            print(field)
            row = tk.Frame(self.root)
            lab = tk.Label(row, width=22, text=field+": ", anchor='w')
            ent = tk.Entry(row)
            row.pack(side=tk.TOP, 
                    fill=tk.X, 
                    padx=5, 
                    pady=5)
            lab.pack(side=tk.LEFT)
            ent.pack(side=tk.RIGHT, 
                    expand=tk.YES, 
                    fill=tk.X)
            entries[field] = ent
        return entries

    ######################################################
    # reset processes
    ######################################################
    def reset_progress_bar(self):
        self.root.update_idletasks()
        self.pb1['value'] = 0

    def reset_output(self):
        self.check_text.delete(1.0, tk.END)

    def reset_progress(self):
        self.checks_progress_txt.config(text = "")

    def reset_doc(self):
        pass

    ######################################################
    def set_loaded_filename(self, filename):
        self.loaded_filename = filename
        # Reduce name down to fit in window
        while len(filename) > 70: # 70 characters is arbitrary
            parts = filename.split("/")
            mid = int(len(parts)/2)
            if mid % 2 == 1:
                while parts[mid] == "...":
                    mid = mid - 1
            else:
                while parts[mid] == "...":
                    mid = mid + 1
            del parts[mid]
            if not "..." in parts:
                parts.insert(mid, "...")
            filename = "/".join(parts)
            print(filename)
        self.loaded_file_txt.config(text = "loaded '{}'".format(filename))
        print("updated filename: {}".format(filename))


    def check_in_progress_txt(self):
        self.checks_progress_txt.config(text = "Checks in progress. Please wait.")

    def check_complete_txt(self):
        self.checks_progress_txt.config(text = "Checks completed.")
    #######################


    def __init__(self):

        # init filename to None
        self.filename = None

        self.root = tk.Tk()
        self.root.geometry("600x800")

        
        self.root.title('UKLLC File 1 Checker and Documentation')

        default_font = font.nametofont("TkDefaultFont")  # Get default font value into Font object
        default_font_family = default_font.actual()["family"]

        header = tk.Frame(self.root)
        row0 = tk.Frame(self.root)
        row1 = tk.Frame(self.root)
        row2 = tk.Frame(self.root)
        row3 = tk.Frame(self.root)
        row4 = tk.Frame(self.root)

        header_txt = tk.Label(header, text = "File 1 Integrity Checks",font=(default_font_family,12,'bold'))
        header.pack(side=tk.TOP, fill=tk.X,padx=5)
        header_txt.pack(side=tk.LEFT, padx=5)

        sep1 = ttk.Separator(self.root,orient='horizontal')
        sep1.pack(fill='x')

        intro_txt = tk.Label(row0, text="Please select your File 1. The file must be in CSV format.", justify=tk.LEFT)
        row0.pack(side=tk.TOP, fill=tk.X, padx=5)
        intro_txt.pack(side = tk.LEFT, padx=5)

        b1 = tk.Button(row1, text = "Load File 1", command = self.load_file1, width = 15)
        self.loaded_file_txt = tk.Label(row1, text = "")
        
        row1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        self.loaded_file_txt.pack(side = tk.RIGHT, padx=5)

        sep2 = ttk.Separator(self.root,orient='horizontal')
        sep2.pack(fill='x')

        auto_checks_txt = tk.Label(row2, text="Click 'Start' to begin automated file 1 integrity checks.\nPlease wait until the automated checks are completed before filling out the File 1 documentation section", justify=tk.LEFT)
        row2.pack(side=tk.TOP, fill=tk.X, padx=5)
        auto_checks_txt.pack(side = tk.LEFT, padx=5)

        # Start button for auto checks
        b4 = tk.Button(row3, text = "Start", width = 15, command = self.start_checks)
        
        # # Adding progress bar
        sub_row3 = tk.Frame(row3)
        self.pb1 = ttk.Progressbar(sub_row3, orient=tk.HORIZONTAL, length=200, mode='determinate')

        # Add text for auto checks progress
        self.checks_progress_txt = tk.Label(row3, text = "")
        
        row3.pack(side=tk.TOP, fill=tk.X, padx=5, pady =5)
        b4.pack(side=tk.LEFT, padx=5, pady=5)
        sub_row3.pack(side=tk.LEFT, fill=tk.X, padx=2)
        
        self.pb1.pack(side=tk.LEFT,expand=True)
        self.checks_progress_txt.pack(side=tk.LEFT, padx=5, pady=5)
        
        text_desc = tk.Label(row4, text = "Integrity checks output:", justify=tk.LEFT)
        row4.pack(side=tk.TOP, fill=tk.X, padx=5)
        text_desc.pack(side = tk.LEFT, padx=5)      

        # Text area output block
        # adding frame
        text_frame = tk.Frame(self.root, borderwidth=2)
        text_frame.pack(side=tk.TOP,pady=5, padx=10, expand = True, fill=tk.X)

        # adding scrollbars 
        ver_sb = tk.Scrollbar(text_frame, orient=tk.VERTICAL )
        ver_sb.pack(side=tk.RIGHT, fill=tk.BOTH)

        hor_sb = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        hor_sb.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # adding writing space
        self.check_text = tk.Text(text_frame, height=15)
        self.check_text.pack(side=tk.LEFT, expand = True, fill=tk.X)

        # binding scrollbar with text area
        self.check_text.config(yscrollcommand=ver_sb.set)
        ver_sb.config(command=self.check_text.yview)

        self.check_text.config(xscrollcommand=hor_sb.set)
        hor_sb.config(command=self.check_text.xview)

        #############################################
        #Documentation
        doc_header_row = tk.Frame(self.root)
        doc_desc_row = tk.Frame(self.root)
        doc_actions_row = tk.Frame(self.root)

        doc_header_txt = tk.Label(doc_header_row, text = "File 1 Documentation",font=(default_font_family,12,'bold'))
        doc_header_row.pack(side=tk.TOP, fill=tk.X,padx=5)
        doc_header_txt.pack(side=tk.LEFT, padx=5)

        sep1 = ttk.Separator(self.root,orient='horizontal')
        sep1.pack(fill='x')

        doc_desc = WrappingLabel(doc_desc_row, text = "Placeholder text explaining what to do with file 1 documentation. It will probably be quite long, hence why i'm padding this debugging message out for size. Probably longer than this still. So lets chuck some more characters in. Is this enough yet? Nearly.", justify = tk.LEFT)
        doc_desc_row.pack(side=tk.TOP, fill=tk.X,padx=5)
        doc_desc.pack(expand = True, fill = tk.X)
        # TODO insert first 4 automatic fields as text blocks.
        question_fields = [
            "Date File Uploaded to DHCW",
            "1. Please enter the total number of participants (n) in the cohort (enrolled sample/headline denominator)",
            "2. Please enter the number of participants (n) excluded because they died on or before 31/12/2019",
            "3. Please enter the number of participants (n) excluded because they died on or after 01/01/2020",
            "4. Please "
        ]
        # Insert user fill fields
        #ents = self.make_entries(self.root, ["1", "2", "3"])
    

        #TODO insert 9.

        b2 = tk.Button(self.root, text='Save')
        b2.pack(side=tk.LEFT, padx=5, pady=5)
        b3 = tk.Button(self.root, text='Quit', command=self.root.quit)
        b3.pack(side=tk.LEFT, padx=5, pady=5)


        self.root.mainloop()


if __name__ == "__main__":
    ui = MainUI()