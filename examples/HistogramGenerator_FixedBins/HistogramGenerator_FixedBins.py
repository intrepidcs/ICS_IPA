##########################################################################################################################################################################################################################################
#	Script Description:
#		This script generates a time based histogram for each of the signals listed in the script config file using bins defined for each channel in the config file. 
#		The histogram output is an Excel file with a sheet for each signal including a bar graph showing the histogram graphically. 
#
###########################################################################################################################################################################################################################################
#	Script Inputs: (when you run this script you will be prompted with 2 file open dialog windows. The first asks for a config file with extension *.asl; the second asks 
# 	for a list of one or more data files (*.db, *.mf4, *.dat))
#		
# 		Script config file IPA_HistogramConfig.asl is a JSON file used to configure the script. This file has the following keys:
# 			
# 			SignalListForUseInTimeBasis - list of the key signals that you want the script to use as time basis. When you call the GetNextRecord() function, the virtual 
# 			time cursor will be moved to the next chronological data point among the signals in this list. If you only inlcude 1 signal that is updated at 1Hz then 
# 			GetNextRecord() will step through the file at 1Hz matching the time stamps from this signal.
#			
# 			Channels - List of channels to generate histogram on including bins for each signal.
#
#		Sample Data File(s) list. Script can be run on one or more copies of the sample data file
#			
# 			DataSpySampleDataFileAllSignals1.db
#
##########################################################################################################################################################################################################################################
#	Script Outputs:
#		
# 		*.xlsx file with a sheet for each signal in the Channels list of the config file including a bar graph. Filename starts with HistogramGen and then has a time
#       stamp that indicates when the histogram was created ie: HistogramGen_09-06-18_08-55-06.xlsx.
#
##########################################################################################################################################################################################################################################

import numpy as np
import xlsxwriter
import json
import datetime
import pprint
import enum
import sys
import os
import logging 
import matplotlib
matplotlib.use('AGG')   # this option allows use of matplotlib on headless server
from matplotlib import pyplot as plt
from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary
from SetUpExcelWorksheetsForHistograms import ExcelHistogramReport

#set up access to IPA.log file in main script
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
handler = logging.FileHandler('IPA.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

# Get user input: an .asl file and one or more db files
# These next two functions are defined differently on the PC version compared to Wivi since 
# user pics files on PC but Wivi server provides input file list without GUI
slFilePath = IPAInterfaceLibrary.get_config_file()
dbFilePaths = IPAInterfaceLibrary.get_input_file_list()

log.info("Hello")

with open(slFilePath) as file:
    config = json.load(file)

signals = config["Channels"]
Sig_list = [Channel['name_in_script'] for Channel in signals]
n_signals = len(signals)
bins_list = [sig['bins'] for sig in signals]

time_tallys = [[0.0]*(len(bins_list[sig_num])+1) for sig_num in range(n_signals)]

#now create a string for SetActiveMask 
SetActiveMaskString = ''
for signal in Sig_list:
	NumberOfTimeBasisSignals = len(config["SignalListForUseInTimeBasis"])
	CurrentSignalInTimeBasisList = False
	for i in range(NumberOfTimeBasisSignals):
		if signal == config["SignalListForUseInTimeBasis"][i]:
			CurrentSignalInTimeBasisList = True
	if CurrentSignalInTimeBasisList:
		SetActiveMaskString = SetActiveMaskString + '1'
	else:
		SetActiveMaskString = SetActiveMaskString + '0'

for dbFilePath in dbFilePaths:
    try:
        with icsFI.ICSDataFile(dbFilePath, slFilePath) as db:
            ActiveMaskResult = db.SetActiveMask(SetActiveMaskString)
            #db.SetActiveMask('1' * n_signals)   # capture all signals
            prevTimestamp = 0.0
            curTimestamp = db.JumpAfterTimestamp(0)
            dataPoints = db.GetPoints()
            while curTimestamp != sys.float_info.max:
                for sig_num in range(n_signals):
                    datum = dataPoints[sig_num]
                    # find which bin datum belongs to
                    bin_num = np.digitize([datum], bins_list[sig_num], right=True)[0]
                    delta_time = curTimestamp - prevTimestamp
                    time_tallys[sig_num][bin_num] += delta_time
                prevTimestamp = curTimestamp
                curTimestamp = db.GetNextRecord()
    except ValueError as e :
        print(str(e))

#  Create a workbook and insert one worksheet for each signal.
xlHistWorkbook = ExcelHistogramReport()
for sig_num in range(n_signals):
    sig_info = signals[sig_num]
    xlHistWorkbook.add_sig_worksheet(sig_info, time_tallys[sig_num])

xlHistWorkbook.AddFileInfoListSheet(dbFilePaths, IPAInterfaceLibrary.is_running_on_wivi_server())
xlHistWorkbook.CloseWorkbook()
log.info("Goodbye")
