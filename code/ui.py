from re import L
import tkinter as tk
from tkinter import Label, ttk
from tkinter import font
from datetime import datetime
from turtle import bgcolor, width
import shared_functions as sf
import UK_LLC_File_1_Checker as f1
import threading


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

    def separator(self, parent):
        sep = ttk.Separator(parent, orient='horizontal')
        sep.pack(fill='x', side = tk.TOP)
        return sep

    def doc_block(self, txt):

        row = tk.Frame(self.nested_frame)
        desc = tk.Label(row, text = txt,wraplength=self.window_width-150, justify=tk.LEFT)
        inpt = tk.Entry(row)
        
        row.pack(side = tk.TOP, fill = tk.X, padx=10, pady=2)
        desc.pack(side = tk.LEFT)
        inpt.pack(side = tk.RIGHT)

        self.separators.append(self.separator(self.nested_frame))
        return [row, desc, inpt]
    
    #######################


    def __init__(self):

        self.window_width = 700
        # init filename to None
        self.filename = None

        self.separators = []

        self.root = tk.Tk()
        #TODO make y dimensions scre
        # en size & insert scroll bar on window
        self.root.geometry("{}x700".format(self.window_width))
        self.root.resizable(False, True)
        print(self.root.winfo_width())

        self.root.title('UKLLC File 1 Checker and Documentation')

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand = 1)

        # Create A Canvas
        window_canvas = tk.Canvas(main_frame)
        window_canvas.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

        # Add A Scrollbars to Canvas
        y_scrollbar = ttk.Scrollbar(main_frame,orient=tk.VERTICAL,command=window_canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT,fill=tk.Y)

        # Configure the canvas
        window_canvas.configure(yscrollcommand=y_scrollbar.set)
        window_canvas.bind("<Configure>",lambda e: window_canvas.config(scrollregion = window_canvas.bbox(tk.ALL))) 

        # Create Another Frame INSIDE the Canvas
        self.nested_frame = tk.Frame(window_canvas)

        # Add that New Frame a Window In The Canvas
        window_canvas.create_window((0,0),window= self.nested_frame, anchor="nw")


        default_font = font.nametofont("TkDefaultFont")  # Get default font value into Font object
        default_font_family = default_font.actual()["family"]

        header = tk.Frame(self.nested_frame)
        row0 = tk.Frame(self.nested_frame)
        row1 = tk.Frame(self.nested_frame)
        row2 = tk.Frame(self.nested_frame)
        row3 = tk.Frame(self.nested_frame)
        row4 = tk.Frame(self.nested_frame)

        header_txt = tk.Label(header, text = "File 1 Integrity Checks",font=(default_font_family,12,'bold'))
        header.pack(side=tk.TOP, fill=tk.X,padx=5)
        header_txt.pack(side=tk.LEFT, padx=5)

        self.separators.append(self.separator(self.nested_frame))

        intro_txt = tk.Label(row0, text="Please select your File 1. The file must be in CSV format.", justify=tk.LEFT)
        row0.pack(side=tk.TOP, fill=tk.X, padx=5)
        intro_txt.pack(side = tk.LEFT, padx=5)

        b1 = tk.Button(row1, text = "Load File 1", command = self.load_file1, width = 15)
        self.loaded_file_txt = tk.Label(row1, text = "")
        
        row1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        self.loaded_file_txt.pack(side = tk.RIGHT, padx=5)

        self.separators.append(self.separator(self.nested_frame))

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
        text_frame = tk.Frame(self.nested_frame, borderwidth=2)
        text_frame.pack(side=tk.TOP,pady=5, padx=10)

        # adding scrollbars 
        ver_sb = tk.Scrollbar(text_frame, orient=tk.VERTICAL )
        ver_sb.pack(side=tk.RIGHT, fill=tk.BOTH)

        hor_sb = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL)
        hor_sb.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # adding writing space
        self.check_text = tk.Text(text_frame, height=15)
        self.check_text.pack(side=tk.LEFT)

        # binding scrollbar with text area
        self.check_text.config(yscrollcommand=ver_sb.set)
        ver_sb.config(command=self.check_text.yview)

        self.check_text.config(xscrollcommand=hor_sb.set)
        hor_sb.config(command=self.check_text.xview)

        #############################################

        documentation = {}

        #Documentation
        doc_header_row = tk.Frame(self.nested_frame)
        doc_desc_row = tk.Frame(self.nested_frame)
        doc_actions_row = tk.Frame(self.nested_frame)

        doc_header_txt = tk.Label(doc_header_row, text = "File 1 Documentation",font=(default_font_family,12,'bold'))
        doc_header_row.pack(side=tk.TOP, fill=tk.X,padx=5)
        doc_header_txt.pack(side=tk.LEFT, padx=5)

        sep1 = ttk.Separator(self.nested_frame,orient='horizontal')
        sep1.pack(fill='x')

        doc_desc = tk.Label(doc_desc_row, text = "Placeholder text explaining what to do with file 1 documentation. It will probably be quite long, hence why i'm padding this debugging message out for size. Probably longer than this still. So lets chuck some more characters in. Is this enough yet? Nearly.", justify = tk.LEFT, wraplength=self.window_width-22)
        doc_desc_row.pack(side=tk.TOP, fill=tk.X,padx=5)
        doc_desc.pack(side=tk.LEFT, fill = tk.X)
        # TODO insert first 4 automatic fields as text blocks.
        question_fields = [
            "Date File Uploaded to DHCW",
            "1. Please enter the total number of participants (n) in the cohort (enrolled sample/headline denominator)",
            "2. Please enter the number of participants (n) excluded because they died on or before 31/12/2019",
            "3. Please enter the number of participants (n) excluded because they died on or after 01/01/2020",
            "4. Please "
        ]
        # Insert user fill fields
        #ents = self.make_entries(self.nested_frame, ["1", "2", "3"])

        # We are going to explicitly specify each question in turn. No clever loops this time. 
        sep2 = ttk.Separator(self.nested_frame, orient='horizontal')
        sep2.pack(fill='x', side = tk.TOP)
        # 1. Date - auto filled
        documentation["Date"] = self.doc_block("Date:")

        # 2. File name - auto filled
        documentation["File Name"] = self.doc_block("File Name:")

        # 3. LPS - auto filled from file name? check if any LPS from the constants list is in the filename, if so add. 
        #    NOTE: check entered val is in constants list.
        documentation["LPS"] = self.doc_block("LPS:")

        # 4. Row count - auto filled
        documentation["Row Count"] = self.doc_block("Row Count:")

        # 5. date file uploaded to DHCW - user filled, format checked (or date select box?)
        documentation["Upload Date"] = self.doc_block("Date File Uploaded to DHCW:")

        # 6. ...
        documentation["Total Participants"] = self.doc_block("1. Please enter the total number of participants (n) in the cohort (enrolled sample/headline denominator)")

        # 7. ...
        documentation["Exclusions1"] = self.doc_block("2. Please enter the number of participants (n) excluded because they died on or before 31/12/2019 (i.e. participants who died and whose death is not likely to be related to COVID 19. We would expect this number to be 0 because these participants can have their data flow to the UK LLC, unless there is specific study policy precluding them.)")

        # 8. ...
        documentation["Exclusions2"] = self.doc_block("3. Please enter the number of participants (n) excluded because they died on or after 01/01/2020 (It is essential that data for participants who have died during the COVID 19 pandemic (on or after 01/01/2020) continue to flow to the UK LLC TRE, unless this directly violates Study policy. Therefore, we would expect this number to be 0)")

        # 9. ...
        documentation["Exclusions3"] = self.doc_block("4. Please enter the number of participants (n) excluded because they have withdrawn from the LPS")

        # 10. ...
        documentation["Exclusions4"] = self.doc_block("5. Please enter the number of participants (n) excluded because they have specifically dissented to the use of their data in the UK LLC TRE")

        # 11.
        documentation["Exclusions5"] = self.doc_block("6. Please enter the number of participants (n) excluded because they have dissented to record linkage (i.e. NHS Digital) (While it is up to LPS whether they send data for participants who have dissented to record linkage (i.e. NHS Digital), please be aware that these participants can be sent to UK LLC with permissions set accordingly. Dissenting to record linkage does not preclude participants from the UK LLC resource, where study-collected data can be provided. )")

        # 12. ...
        documentation["Exclusions6"] = self.doc_block("7. Please enter the number of participants (n) excluded because appropriate governance has not been established")

        # 13. ...
        documentation["Exclusions7"] = self.doc_block("8. Please enter the number of participants (n) excluded for 'other' reasons")

        #14. ...
        documentation["Total Included"] = self.doc_block("9. The number of participants (n) included in the sample uploaded to NHS DHCW (i.e the number in your File 1 where UK LLC status (UKLLC_STATUS) is equal to 1 and Row_Status is equal to 'C')")

        # TODO differentiate bold and reg text in doc_block
        #      Buttons and controls for submitting the docs
        #      Entry fields locking and unlocking (and when to do so)

        #TODO insert 9.

        b2 = tk.Button(self.nested_frame, text='Save')
        b2.pack(side=tk.LEFT, padx=5, pady=5)
        b3 = tk.Button(self.nested_frame, text='Quit', command=self.root.quit)
        b3.pack(side=tk.LEFT, padx=5, pady=5)


        self.root.mainloop()


if __name__ == "__main__":
    ui = MainUI()