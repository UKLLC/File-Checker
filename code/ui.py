import tkinter as tk
import csv
from datetime import datetime
import os
import re
import constants
import shared_functions as sf
import UK_LLC_File_1_Checker as f1


def load_file1():
    f1.load_file()


def make_entries(root, fields):
    entries = {}
    for field in fields:
        print(field)
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field+": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, "0")
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


def main():
    '''
    frame = tk.Tk()
    # TODO name frame
    frame.title("...")

    printButton = tk.Button(frame,
                        text = "Load file 1", 
                        command = load_file1).grid(row = 0)

    tk.Label(frame, text="Test 1").grid(row=1)
    tk.Label(frame, text="Test 2").grid(row=2)

    e1 = tk.Entry(frame)
    e2 = tk.Entry(frame)

    e1.grid(row=1, column=1)
    e2.grid(row=2, column=1)

    frame.mainloop()
    '''
    root = tk.Tk()

    b1 = tk.Button(root, text = "Load file 1", command = load_file1)

    # TODO insert first 4 automatic fields as text blocks.

    # Insert user fill fields
    ents = make_entries(root, ["1", "2", "3"])

    #TODO insert 9.

    b2 = tk.Button(root, text='Save')
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    b3 = tk.Button(root, text='Quit', command=root.quit)
    b3.pack(side=tk.LEFT, padx=5, pady=5)


    root.mainloop()


if __name__ == "__main__":
    main()