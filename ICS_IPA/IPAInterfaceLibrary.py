import sys  #allows access to command line
import glob #allows searching for files
import os
import json #comes with python 3.4

import tkinter as tk #library with file open dialog
from tkinter import filedialog

from ICS_IPA import DataFileIOLibrary

selected_file = ""

def get_input_file_list(autoConvertToDB = False):
    if len(sys.argv) > 1:
        filenames = glob.glob(sys.argv[1] + '/*.db')
    else:
        filenames = []

    if len(filenames) == 0:
        root = tk.Tk()
        root.withdraw()
        root.focus_force()
        root.wm_attributes('-topmost', 1)
        filenames = list(filedialog.askopenfilenames(filetypes = (("Data files", "*.dat;*.log;*.mdf;*.mf4;*.db"), ("All files", "*.*"))))
    if autoConvertToDB and len(filenames) > 0:
        for idx, file_name in enumerate(filenames):
            selected_file = file_name
            name, extension = os.path.splitext(file_name)
            if extension.lower() != ".db":
                if not os.path.isfile(name + ".db"):
                    DataFileIOLibrary.CreateDatabase(file_name, name + ".db")
                filenames[idx] = name + ".db"
    return [dict(("path", item ) for item in filenames)]

def get_config_file():
    root = tk.Tk()
    root.withdraw()
    root.focus_force()
    root.wm_attributes('-topmost', 1)
    fileName = filedialog.askopenfilename(filetypes = (("JSON files", "*.json"), ("All files", "*.*")))
    return fileName

def get_config_data():
    fileName = get_config_file()
    if len(fileName) > 0:
        json_data = open(fileName).read()
        return json.loads(json_data)
    else:
        return ""

def get_output_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    elif len(selected_file) > 0:
        return os.path.dirname(selected_file)
    else:
        os.getcwd()

def update_progress(percent, message):
    if len(message):
        sys.stderr.write(message + "\n")
    sys.stderr.write("Percent done: {}\n".format(percent))

def is_running_on_wivi_server():
    return False
