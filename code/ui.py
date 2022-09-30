import tkinter as tk
import csv
from datetime import datetime
import os
import re
import constants
import shared_functions as sf
import UK_LLC_File_1_Checker as f1
import threading



class MainUI:

    def show_output(self, out_file):
        content = open(out_file, mode="r").read()
        self.check_text.insert(tk.END, content)
        print(content)
        pass

    def load_file1(self):
        p = threading.Thread(target = f1.load_file, args=(False, self)).start()

    def update_progress_bar(self):
        pass

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
        pass

    def get_loaded_filename(self):
        return self.loaded_filename

    def make_entries(self, root, fields):
        entries = {}
        for field in fields:
            print(field)
            row = tk.Frame(root)
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


    def __init__(self):

        root = tk.Tk()

        row1 = tk.Frame(root)
        b1 = tk.Button(row1, text = "Load file 1", command = self.load_file1)
        self.loaded_file_txt = tk.Label(row1, text = "")
        
        row1.pack(side=tk.TOP, fill=tk.X, padx=5, pady =5)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        self.loaded_file_txt.pack(side = tk.RIGHT, padx=5, pady=5)

        # TODO insert first 4 automatic fields as text blocks.
        question_fields = [
            "Date File Uploaded to DHCW",
            "1. Please enter the total number of participants (n) in the cohort (enrolled sample/headline denominator)",
            "2. Please enter the number of participants (n) excluded because they died on or before 31/12/2019",
            "3. Please enter the number of participants (n) excluded because they died on or after 01/01/2020",
            "4. Please "
        ]
        # Insert user fill fields
        #ents = self.make_entries(root, ["1", "2", "3"])

        # adding frame
        frame = tk.Frame(root)
        frame.pack(pady=5, padx=10)

        # adding scrollbars 
        ver_sb = tk.Scrollbar(frame, orient=tk.VERTICAL )
        ver_sb.pack(side=tk.RIGHT, fill=tk.BOTH)

        hor_sb = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        hor_sb.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # adding writing space
        self.check_text = tk.Text(frame, width=80, height=15)
        self.check_text.pack(side=tk.LEFT)

        # binding scrollbar with text area
        self.check_text.config(yscrollcommand=ver_sb.set)
        ver_sb.config(command=self.check_text.yview)

        self.check_text.config(xscrollcommand=hor_sb.set)
        hor_sb.config(command=self.check_text.xview)

        # adding path showing box
        pathh = tk.Entry(root)
        pathh.pack(expand=True, side=tk.LEFT, fill=tk.X, padx=10)

        #TODO insert 9.

        b2 = tk.Button(root, text='Save')
        b2.pack(side=tk.LEFT, padx=5, pady=5)
        b3 = tk.Button(root, text='Quit', command=root.quit)
        b3.pack(side=tk.LEFT, padx=5, pady=5)


        root.mainloop()


if __name__ == "__main__":
    ui = MainUI()