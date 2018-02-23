import numpy as np
import xlsxwriter
import json
import datetime
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
from SigEnumFile import Sig 
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
n_signals = len(signals)
bins_list = [sig['bins'] for sig in signals]

time_tallys = [[0.0]*(len(bins_list[sig_num])+1) for sig_num in range(n_signals)]

MaskString = ""
for i in range (0, Sig.MaxIndexInSigClass):
    if i == Sig.AccelPedalPosition:
        MaskString = MaskString + "1"
    else:
        MaskString = MaskString + "0"

for dbFilePath in dbFilePaths:
    with icsFI.ICSDataFile(dbFilePath, slFilePath) as db:
        ActiveMaskResult = db.SetActiveMask(MaskString)
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

#  Create a workbook and insert one worksheet for each signal.
xlHistWorkbook = ExcelHistogramReport()
for sig_num in range(n_signals):
    sig_info = signals[sig_num]
    xlHistWorkbook.add_sig_worksheet(sig_info, time_tallys[sig_num])

xlHistWorkbook.AddFileInfoListSheet(dbFilePaths, IPAInterfaceLibrary.is_running_on_wivi_server())
xlHistWorkbook.CloseWorkbook()
log.info("Goodbye")
