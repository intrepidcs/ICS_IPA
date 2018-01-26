import tkinter as tk #library with file open dialog
from tkinter import filedialog
import json
import os

root = tk.Tk()
root.withdraw()
jsonfile = filedialog.askopenfilename(parent=root, filetypes = (("json files", "*.json"), ("All files", "*.*")), title = "Select Json Signal File" )
outputDir = filedialog.askdirectory(title="Select SigEnumFile.py Destination Folder")
while len(outputDir) == 0:
	outputDir = filedialog.askdirectory(title="Select SigEnumFile.py Destination Folder")	

with open(jsonfile) as data_file: 
	js = json.load(data_file)
enumDict = {}
for i in range(len(js["Channels"])):
	enumDict[js["Channels"][i]["name"]] = i

with open( os.path.join(outputDir, 'SigEnumFile.py'), 'w') as f:
	f.write("class Sig:\n")
	for k, v in enumDict.items():
		f.write("\t"+k+" = "+str(v)+"\n")