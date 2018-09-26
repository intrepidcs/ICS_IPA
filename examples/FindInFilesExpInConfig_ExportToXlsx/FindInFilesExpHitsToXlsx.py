##########################################################################################################################################################################################################################################
#	Script Description:
#		This script searches for a list of events among a list of input files. The events and the signals referenced in the events are defined in the script config file 
# 		ConfigForSampleDataFileExpInConfigExportToXlsx.asl. Each event has a Description, StartExpression, and EndExpression. The script generates a report file that lists 
# 		the StartTime and EndTime of each event in each file. In addition to outputing the dsr report, this script also generates a *.xlsx file with the data from all of 
# 		events in a single file. 
#		
###########################################################################################################################################################################################################################################
#	Script Inputs: (when you run this script you will be prompted with 2 file open dialog windows. The first asks for a config file with extension *.asl; the second asks 
# 	for a list of one or more data files (*.db, *.mf4, *.dat))
#		
# 		Script config file ConfigForSampleDataFileExpInConfigExportToXlsx.asl is a JSON file used to configure the script. This file has the following keys:
# 			
# 			SignalListForUseInTimeBasis - list of the key signals that you want the script to use as time basis. When you call the GetNextRecord() function, the virtual 
# 			time cursor will be moved to the next chronological data point among the signals in this list. If you only inlcude 1 signal that is updated at 1Hz then 
# 			GetNextRecord() will step through the file at 1Hz matching the time stamps from this signal.
#			
# 			Channels - List of channels that your script will reference in the EventDefinitions
#
#			EventDefinitions - list of named events that script is searching for. Each event has a Description, StartExpression, and EndExpression (see sample *.asl file). 
# 			Script looks through input file list for the StartExpression to toggle from False to True. If found, it logs the time that it occurred in the file and then 
# 			starts looking for the EndExpression. If found, it logs the Start and End times to the dsr file. 
#
#			MaxNumberOfRowsInExcelFile - Maximum number of records to output to Excel file. This limit protects against generating an output file that is too large to open.
#
#		Sample Data File(s) list. Script can be run on one or more copies of the sample data file
#			
# 			DataSpySampleDataFileAllSignals1.db
#
##########################################################################################################################################################################################################################################
#	Script Outputs:
#		
# 		*.dsr file which stands for DataSpyReport. This file is a json file that lists all of occurrances of events found in the input data file set. 
#		The output filename starts wtih FindInFiles_ followed by a timestamp with the time ths report was created ie: FindInFiles_09-05-18_11-24-32.dsr
#
#		*.xlsx file with the raw data from each event found in the search. All of the signals in the Channels list from the config file are included in the output file. 
#		The timestamps in the output file come from the signals listed in the SignalListForUseInTimeBasis from the config file. The filename starts wtih ResultsFile 
# 		followed by a timestamp with the time the report was created ie: ResultsFile_09-11-18_06-59-37.xlsx.
#
##########################################################################################################################################################################################################################################

import numpy as np
import datetime
import pprint
import enum
import sys
import os
import logging
import json
import re
import xlsxwriter

from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary
from ExcelWorkbookClass import ExcelWorkbook
from FindInFilesEventClass import FindInFilesEvents

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
handler = logging.FileHandler('IPA.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

log.info("Hello")

slFilePath = IPAInterfaceLibrary.get_config_file()
dbFilePaths = IPAInterfaceLibrary.get_input_file_list()
#instantiate DSR file object
dsr = icsDSR.DSRFile()

with open(slFilePath) as configFile:
	config = json.load(configFile)

ScriptChannels = config["Channels"]
MaxNumberOfRowsInExcelFile = config["MaxNumberOfRowsInExcelFile"]
NumberOfSignals = len(ScriptChannels)
Sig_list = [Channel['name_in_script'] for Channel in ScriptChannels]
EventDict = config["EventDefinitions"]
NumberOfEvents = len(EventDict)

#instantiate FindInFilesEvents object
Events = FindInFilesEvents(config)

#if any of the event expressions failed the white list check, log which token failed for each expression then exit
BlackTokenFound = False
for i in range(Events.NumberOfEvents):
	if not(Events.StartExpressionTokensAreInWhiteList[i]):
		log.info("The start expression in the event called " + Events.EventDescriptions[i] + " failed the whitelist check due to the token " + Events.FirstBlackTokenInStartExpression[i])
		BlackTokenFound = True

	if not(Events.EndExpressionTokensAreInWhiteList[i]):
		log.info("The end expression in the event called " + Events.EventDescriptions[i] + " failed the whitelist check due to the token " + Events.FirstBlackTokenInEndExpression[i])
		BlackTokenFound = True
if BlackTokenFound:
	exit()

#create Excel workbook and set up sheet for output
ReportGenTimeStamp = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
OutputExcelFileNameAndPath = os.path.join(os.getcwd(), "ResultsFile_" + ReportGenTimeStamp + ".xlsx")
xlWorkbook = ExcelWorkbook(OutputExcelFileNameAndPath)
xlWorkbook.add_worksheet("ResultsSheet1")
xlWorkbook.worksheet.write_string(0,0,"FileNumber")
xlWorkbook.worksheet.write_string(0,1,"TimeInFile")

#now create a string for SetActiveMask 
SetActiveMaskString = ''
NumberOrSignals = 0
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
	NumberOrSignals = NumberOrSignals + 1
	xlWorkbook.worksheet.write_string(0,1 + NumberOrSignals, signal)

#now go through each file, look for hits and write data to xlsx file
rownumber = 0
FileNumber = 0
for dbFilePath in dbFilePaths:
	try:
		FileNumber = FileNumber + 1
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
			ActiveMaskResult = data.SetActiveMask(SetActiveMaskString)
			curTimestamp = data.JumpBeforeTimestamp(0)
			dataPoints = data.GetPoints()
			dataPointsPrev = dataPoints.copy()
			#initialize Event State Parameters before analyzing each file
			Events.initializeEventParmsForNewDataFile()
			RecordIncludesExpressionEndEvent = False
			#loop through each record in each file
			while curTimestamp != sys.float_info.max and (rownumber < MaxNumberOfRowsInExcelFile):
				CurrentRecordHasBeenAdded = False
				for i in range(Events.NumberOfEvents):
					if Events.EventActive[i] == False:
						Events.SearchExpState[i] = eval(Events.StartExpressionFormattedForEval[i])
						RecordIncludesExpressionEndEvent = False	
					else:
						Events.SearchExpState[i] = eval(Events.EndExpressionFormattedForEval[i])
						if Events.SearchExpState[i]:
							RecordIncludesExpressionEndEvent = True
					if Events.EventActive[i] == False and Events.SearchExpState[i] == True:
						Events.SearchExpStartTime[i] = curTimestamp
						Events.EventActive[i] = True
						Events.TimeFromExpressionStart[i] = 0
					if Events.EventActive[i] and (CurrentRecordHasBeenAdded == False) and (RecordIncludesExpressionEndEvent == False):
						rownumber = rownumber + 1
						if rownumber < MaxNumberOfRowsInExcelFile:
							xlWorkbook.worksheet.write_number(rownumber, 0, FileNumber)
							xlWorkbook.worksheet.write_number(rownumber, 1, curTimestamp)
							xlWorkbook.write_row_to_worksheet(rownumber, 2, dataPoints)
							CurrentRecordHasBeenAdded = True

					if Events.EventActive[i] and Events.EventActivePrev[i]: #this is TRUE first loop with EndExpressionEval[i] = TRUE
						if Events.SearchExpState[i] == True:
							Events.SearchExpEndTime[i] = curTimestamp
							dsr.IncludeHit(data, Events.SearchExpStartTime[i], Events.SearchExpEndTime[i], Events.EventDescriptions[i])
							Events.EventActive[i] = False
							Events.TimeFromExpressionStart[i] = - 1
						else:
							Events.TimeFromExpressionStart[i] = curTimestamp - Events.SearchExpStartTime[i]
					Events.EventActivePrev[i] = Events.EventActive[i]
				dataPointsPrev = dataPoints.copy()# copy previous loops record array to new array
				curTimestamp = data.GetNextRecord()
				#log.info(str(curTimestamp))
			#if any events are active at the end of file, log the last time stamp as the end of hit
			for i in range(Events.NumberOfEvents):
				if Events.EventActive[i]:
					dsr.IncludeHit(data, Events.SearchExpStartTime[i], data.GetMeasurementTimeBounds()[2] - data.GetMeasurementTimeBounds()[1], Events.EventDescriptions[i])
	except ValueError as e :
		print(str(e))

#------------------------------------------------------------------------------------------------------------------
ReportGenTimeStamp = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
DSRFilename = "FindInFiles_" + ReportGenTimeStamp + ".dsr" 
#------------------------------------------------------------------------------------------------------------------

# now combine the signal list and hit list to a new JSON file and output to an mdf file
dsr.save(DSRFilename)

xlWorkbook.AddFileInfoListSheet(dbFilePaths, IPAInterfaceLibrary.is_running_on_wivi_server())
xlWorkbook.CloseWorkbook()

log.info("Good Bye")