import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import font
from datetime import datetime
import shared_functions as sf
import UK_LLC_File_1_Checker as f1
import threading
import constants
import json
import threading
import os


class MainUI:        
    def load_file1(self):
        '''
        Open file dialog, save filename, reset UI and check for valid study code in the filename
        '''
        self.filename = sf.file_dialog()
        if self.filename == "": # if file dialog is aborted
            return

        # wipe file 1 doc entries
        self.reset_doc_entries()

        self.set_loaded_filename(self.filename)

        # Wipe outputs
        self.reset_progress_bar()
        self.reset_output()
        # disable save button until checks are done
        self.b2["state"] = "disabled"
        self.error_text.config(text = "")

        #wipe progress text
        self.reset_progress()
        self.documentation["File Name"][2].insert(0, self.filename.split("/")[-1])
        # Insert LPS into field if matching
        all_lps_ids = constants.UK_LLC_STUDY_CODES + constants.ACCEPTABLE_STUDY_CODES
        for code in all_lps_ids:
            if code in self.filename:
                self.documentation["LPS"][2].insert(0, code)
                break  

    def start_checks(self):
        '''
        Setup UI for checks and detatch thread
        '''
        self.reset_output()
        self.error_text.config(text = "")
        if not self.filename: # If user has not yet loaded a file
            self.load_file1()
        if self.filename == "": # If file selection is cancelled
            return
        try:
            p = threading.Thread(target = self.check_staging).start()
        except FileNotFoundError:
            print("File not loaded")
        self.check_in_progress_txt()
        self.b2["state"] = "normal"

    def check_staging(self):
        '''
        launch checks and update UI when done
        '''
        f1.load_file(self.filename, self)
        self.check_complete_txt()

    def show_output(self, out_file):
        '''
        Load the file checker output and write to UI text field
        '''
        content = open(out_file, mode="r").read()
        self.check_text.insert(tk.END, content)
        print(content)
        if content == "File passed all checks.":
            self.file_passed_checks = 1
        else:
            self.file_passed_checks = 0
            self.error_text.config(text = "Warning: automated checks detected problems with the file. \nOnly save and submit if you are certain the file is correct.")

    def update_progress_bar(self):
        '''
        increment progress bar (1/12th at a time)
        '''
        self.root.update_idletasks()
        self.pb1['value'] += (100/12) + 0.001

    def get_loaded_filename(self):
        return self.loaded_filename

    def update_row_counts(self, row_count, included_participants):
        '''
        Auto fill 'Row Count' and 'Total Included' fields
        '''
        self.reset_doc_entry("Row Count")
        self.reset_doc_entry("Total Included")
        self.documentation["Row Count"][2].insert(0, row_count)
        self.documentation["Total Included"][2].insert(0, included_participants)
        

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

    def reset_doc_entries(self):
        for key in self.documentation.keys():
            if key != "Date": # Skip reseting date 
                self.documentation[key][2].delete(0, "end")

    def reset_doc_entry(self, key):
        self.documentation[key][2].delete(0, "end")

    ######################################################
    def set_loaded_filename(self, filename):
        '''
        Display filename to UI. File paths are long, so cut middle parts until it fits.
        '''
        self.loaded_filename = filename
        # Reduce name down to fit in window
        while len(filename) > 70: # Make the filename less than 70 characters. 70 characters is arbitrary
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
        self.loaded_file_txt.config(text = "loaded '{}'".format(filename))
        print("updated filename: {}".format(filename))

    def check_in_progress_txt(self):
        self.checks_progress_txt.config(text = "Checks in progress. Please wait.")

    def check_complete_txt(self):
        self.checks_progress_txt.config(text = "Checks completed.")

    def separator(self, parent):
        '''
        Insert line across UI
        '''
        sep = ttk.Separator(parent, orient='horizontal')
        sep.pack(fill='x', side = tk.TOP)
        return sep

    def doc_block(self, bold_txt, reg_txt = False):
        '''
        Insert row of description and entry field into UI
        '''
        row = tk.Frame(self.nested_frame)
        desc1 = tk.Label(row, text = bold_txt,wraplength=self.window_width-160, justify=tk.LEFT, font=(self.default_font_family,9,'bold'))
        if reg_txt:
            row2 = tk.Frame(self.nested_frame)
            desc2 = tk.Label(row2, text = reg_txt,wraplength=self.window_width-160, justify=tk.LEFT)
        else:
            desc2 = None
        inpt = tk.Entry(row)
        
        row.pack(side = tk.TOP, fill = tk.X, padx=10, pady=3)
        inpt.pack(side = tk.RIGHT)
        desc1.pack(side = tk.LEFT)
        if reg_txt:
            row2.pack(side = tk.TOP, fill = tk.X, padx=10, pady=2)
            desc2.pack(side = tk.LEFT)

        self.separators.append(self.separator(self.nested_frame))
        return [row, desc1, inpt, desc2]
    
    #######################

    def LPS_check(self):
        '''
        Find out if entered LPS code is recognised (in constants)
        '''
        lps = self.documentation["LPS"][2].get().upper()
        if lps in constants.UK_LLC_STUDY_CODES or lps in constants.ACCEPTABLE_STUDY_CODES:
            return True
        else:
            return False

    def sum_check(self):
        '''
        check if sum(exclusions) + sum(inclusions) = total cohort participants
        '''
        # Error handle target
        target = self.documentation["Total Participants"][2].get().strip()
        if target == "":
            target = 0
        else:
            target = int(target)
        # Error handle excluded
        excluded = 0
        for key in self.documentation.keys():
            if "Exclusion" in key:
                # If field is empty, assume 0
                val = self.documentation[key][2].get().strip()
                if val == "":
                    val = 0
                excluded += int(val)
        # Error handle included
        included = int(self.documentation["Total Included"][2].get().strip())
        if included == "":
            included == 0
        else:
            included = int(included)
        if excluded + included == target:
            return True, excluded, included, target
        else:
            return False, excluded, included, target

    def prep_save(self):
        '''
        Pre save checks - determine whether ready to continue
        '''
        self.continue_save = True
        self.warning_save = False
        # Input checking 
        # 1. Is the LPS valid? (warning)
        txt1, txt2 = "", ""
        lps_check = self.LPS_check()
        if not lps_check:
            lps = self.documentation["LPS"][2].get().strip()
            if lps == "":
                lps = "[None]"
            txt1 = "Study name {} not recognised. Please make sure you have entered the agreed study identifier.".format(lps)

        # 2. Is do the exclusions and count add up?
        try:
            sum_check, exc, inc, tar = self.sum_check()
            if not sum_check:
                txt2 = "Exclusions ({}) and inclusions ({}) do not sum to study participants (sum is {}, should be {}). Please make sure the values are correct.".format(exc, inc, exc+inc, tar)
        except ValueError:
            messagebox.showerror("Input error", "Participant input(s) can not be converted to integer. Please make sure input fields 1-9 are only numerical.")
            return
        
        # If any checks failed, show warning window
        if not lps_check and not sum_check:
            self.lock = True
            self.messagebox_warning("1: {}\n\n2: {}".format(txt1, txt2))
        elif not lps_check:
            self.messagebox_warning("1: {}".format(txt1))
        elif not sum_check:
            self.messagebox_warning("1: {}".format(txt2))
        else:
            self.save()


    def save(self):            
        '''
        Set up user entry fields and checker output as a dictionary and write to json.
        '''
        
        if self.continue_save:
            out_dict = {}
            # user entry fields
            for key, value in self.documentation.items():
                out_dict[key] = value[2].get()
            # if file checker errors
            if self.file_passed_checks == 0: 
                out_dict["valid file"] = "0"
                out_dict["checker_output"] = self.check_text.get("1.0", "end")
            # if file checker no errors
            else:
                out_dict["valid file"] = "1"
                out_dict["checker_output"] = ""

            # check if saved with warning
            if self.warning_save:
                out_dict["saved with warning"] = "1"
            else:
                out_dict["saved with warning"] = "0"


            save_name = 'File1_Doc_{}.json'.format((self.filename.split(".")[0]).split("/")[-1])
            curpath = os.path.abspath(os.curdir)
            if "outputs" in os.listdir(curpath): # If running from root (same level as outputs folder)
                out_filename = os.path.join(curpath, "outputs", save_name)
            else:
                out_filename = os.path.join(curpath, "..", "outputs", save_name)
            print(out_filename)
            print(os.listdir(curpath))
            with open(out_filename, 'w') as f:
                json.dump(out_dict, f)
            
            messagebox.showinfo("Saved", "File 1 documentation saved as {}".format(save_name))
            print("Saved file {}".format(save_name))

    #######################

    def warning_continue(self):
        self.win.destroy()
        print("Continuing save")
        self.warning_save = True
        self.save()

    def warning_cancel(self):
        self.win.destroy()
        print("Cancelling save")

    def messagebox_warning(self, message):
        '''
        Custom warning window with button to continue save or cancel
        '''
        self.win = tk.Toplevel()
        self.win.geometry("+200+200")
        self.win.resizable(False,False)
        self.win.title("Input Warning")
        ttk.Separator(self.win,orient='horizontal').pack(fill='x', side = tk.TOP)
        tk.Label(self.win, text = message, wraplength = 300, justify=tk.LEFT, padx=5).pack()
        
        button_row = tk.Frame(self.win)
        ttk.Separator(self.win,orient='horizontal').pack(fill='x', side = tk.TOP)
        button_row.pack(side = tk.TOP, fill= tk.X)
        tk.Button(button_row, text='Save Anyway', command=self.warning_continue).pack(side = tk.RIGHT, padx=5, pady=5)
        tk.Button(button_row, text='Return', command=self.warning_cancel).pack(side = tk.RIGHT, padx=5, pady=5)

    #######################

    def __init__(self):
        self.window_width = 700
        self.filename = None
        self.separators = []

        self.root = tk.Tk()
        self.root.geometry("{}x700".format(self.window_width))
        self.root.resizable(False, True)

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
        self.default_font_family = default_font.actual()["family"]

        # Setup rows of checker section
        header = tk.Frame(self.nested_frame)
        row0 = tk.Frame(self.nested_frame)
        row1 = tk.Frame(self.nested_frame)
        row2 = tk.Frame(self.nested_frame)
        row3 = tk.Frame(self.nested_frame)
        row4 = tk.Frame(self.nested_frame)

        # Title row
        header_txt = tk.Label(header, text = "File 1 Integrity Checks",font=(self.default_font_family,12,'bold'))
        header.pack(side=tk.TOP, fill=tk.X,padx=5)
        header_txt.pack(side=tk.LEFT, padx=5)

        self.separators.append(self.separator(self.nested_frame))

        # Load file button section
        intro_txt = tk.Label(row0, text="Please select your File 1. The file must be in CSV format.", justify=tk.LEFT)
        row0.pack(side=tk.TOP, fill=tk.X, padx=5)
        intro_txt.pack(side = tk.LEFT, padx=5)

        b1 = tk.Button(row1, text = "Load File 1", command = self.load_file1, width = 15)
        self.loaded_file_txt = tk.Label(row1, text = "")
        
        row1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=3)
        b1.pack(side=tk.LEFT, padx=5, pady=2)
        self.loaded_file_txt.pack(side = tk.RIGHT, padx=5)

        self.separators.append(self.separator(self.nested_frame))

        # Start checks section
        auto_checks_txt = tk.Label(row2, text="Click 'Start' to begin automated file 1 integrity checks.\nPlease wait until the automated checks are completed before filling out the File 1 documentation section", justify=tk.LEFT)
        row2.pack(side=tk.TOP, fill=tk.X, padx=5)
        auto_checks_txt.pack(side = tk.LEFT, padx=5)

        # Start button for auto checks
        b4 = tk.Button(row3, text = "Start", width = 15, command = self.start_checks)
        
        # # Adding progress bar
        sub_row3 = tk.Frame(row3)
        self.pb1 = ttk.Progressbar(sub_row3, orient=tk.HORIZONTAL, length=350, mode='determinate')

        # Add text for auto checks progress
        self.checks_progress_txt = tk.Label(row3, text = "")
        
        row3.pack(side=tk.TOP, fill=tk.X, padx=5, pady =5)
        b4.pack(side=tk.LEFT, padx=5, pady=2)
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

        self.documentation = {}

        #Documentation
        doc_header_row = tk.Frame(self.nested_frame)
        doc_desc_row = tk.Frame(self.nested_frame)

        doc_header_txt = tk.Label(doc_header_row, text = "File 1 Documentation",font=(self.default_font_family,12,'bold'))
        doc_header_row.pack(side=tk.TOP, fill=tk.X,padx=5)
        doc_header_txt.pack(side=tk.LEFT, padx=5)

        sep1 = ttk.Separator(self.nested_frame,orient='horizontal')
        sep1.pack(fill='x')

        doc_desc1 = tk.Label(doc_desc_row, text = "Please fill in the following fields regarding your loaded file 1. Some fields have been automatically filled where possible.", justify = tk.LEFT, wraplength=self.window_width-22)
        doc_desc1 = tk.Label(doc_desc_row, text = "Please make certain the number of participants included in the sample and excluded from the sample add up to the total number of participants in the cohort. If you are unable to categorise exclusions, please include them in field 8: 'other'.", justify = tk.LEFT, wraplength=self.window_width-22)
        doc_desc_row.pack(side=tk.TOP, fill=tk.X,padx=5)
        doc_desc1.pack(side=tk.LEFT, fill = tk.X)


        # We are going to explicitly specify each question in turn. No clever loops this time. 
        sep2 = ttk.Separator(self.nested_frame, orient='horizontal')
        sep2.pack(fill='x', side = tk.TOP)

        # Entry field rows:
        self.documentation["Date"] = self.doc_block("Date:")
        self.documentation["Date"][2].insert(0, (datetime.now()).strftime("%d/%m/%Y"))
        self.documentation["File Name"] = self.doc_block("File name:")
        self.documentation["LPS"] = self.doc_block("Study name:")
        self.documentation["Row Count"] = self.doc_block("Row count:")
        self.documentation["Upload Date"] = self.doc_block("Expected date File 1 uploaded to DHCW:")
        self.documentation["Total Participants"] = self.doc_block("1. Please enter the total number of participants (n) in the cohort (enrolled sample/headline denominator)")
        self.documentation["Exclusions1"] = self.doc_block("2. Please enter the number of participants (n) excluded because they died on or before 31/12/2019", "i.e. participants who died and whose death is not likely to be related to COVID 19. We would expect this number to be 0 because these participants can have their data flow to the UK LLC, unless there is specific study policy precluding them.")
        self.documentation["Exclusions2"] = self.doc_block("3. Please enter the number of participants (n) excluded because they died on or after 01/01/2020", "It is essential that data for participants who have died during the COVID 19 pandemic (on or after 01/01/2020) continue to flow to the UK LLC TRE, unless this directly violates Study policy. Therefore, we would expect this number to be 0.")
        self.documentation["Exclusions3"] = self.doc_block("4. Please enter the number of participants (n) excluded because they have withdrawn from the LPS")
        self.documentation["Exclusions4"] = self.doc_block("5. Please enter the number of participants (n) excluded because they have specifically dissented to the use of their data in the UK LLC TRE")
        self.documentation["Exclusions5"] = self.doc_block("6. Please enter the number of participants (n) excluded because they have dissented to record linkage (i.e. NHS Digital)", "While it is up to LPS whether they send data for participants who have dissented to record linkage (i.e. NHS Digital), please be aware that these participants can be sent to UK LLC with permissions set accordingly. Dissenting to record linkage does not preclude participants from the UK LLC resource, where study-collected data can be provided.")
        self.documentation["Exclusions6"] = self.doc_block("7. Please enter the number of participants (n) excluded because appropriate governance has not been established")
        self.documentation["Exclusions7"] = self.doc_block("8. Please enter the number of participants (n) excluded for 'other' reasons")
        self.documentation["Total Included"] = self.doc_block("9. The number of participants (n) included in the sample uploaded to NHS DHCW (i.e the number in your File 1 where UK LLC status (UKLLC_STATUS) is equal to 1 and Row_Status is equal to 'C')")

        # Save section
        button_row = tk.Frame(self.nested_frame)
        self.error_text = tk.Label(button_row, text = "", justify = tk.LEFT, wraplength=self.window_width-50)
        self.b2 = tk.Button(button_row, text='Save & submit', font=(self.default_font_family,10), command=self.prep_save)
        self.b2["state"] = "disabled" # disable at first, enable later once file has been checked
        button_row.pack(side = tk.TOP, fill = tk.X, padx=5, pady=5)
        self.error_text.pack(side=tk.LEFT, padx=5, pady=5)
        self.b2.pack(side=tk.RIGHT, padx=5, pady=5)

        # Bottom padding to keep content onscreen when window is fullscreen
        self.separators.append(self.separator(self.nested_frame))
        bottom_padding = tk.Frame(self.nested_frame)
        bottom_text = tk.Label(bottom_padding, text ="")
        bottom_padding.pack(side = tk.TOP, fill = tk.X, pady = 5)
        bottom_text.pack(side=tk.BOTTOM, pady=5)
        self.separators.append(self.separator(self.nested_frame))

        self.root.mainloop()


if __name__ == "__main__":
    ui = MainUI()