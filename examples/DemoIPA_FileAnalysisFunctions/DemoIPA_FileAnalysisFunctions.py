##########################################################################################################################################################################################################################################
#	Script Description:
#		This script does not produce any output. It is designed to excercise several of the IPA wrapper class functions. New script authors can set breakpoints in this 
# 		script and step through it using the sample data file DataSpySampleDataFileAllSignals1.db while having the same file loaded in DataSpy and they can switch back 
# 		and forth between the debug watch windown and DataSpy to understand what the functions do.
#		
##########################################################################################################################################################################################################################################
#	Script Inputs: (when you run this script you will be prompted with 2 file open dialog windows. The first asks for a config file with extension *.als; the second 
# 	asks for one or more data files (*.db, *.mf4, *.dat))
#
#		Script config file ConfigForSampleDataFileExpInConfig.asl
#			SignalListForUseInTimeBasis
#			Channels
#			EventDefinitions
#
#		Sample Data File(s) list. Script can be run on one or more copies of the sample data file
#			DataSpySampleDataFileAllSignals1.db
#
#		SigEnumFile.py is a simple python class that lists the index for all of the signals in the config file corresponding to their position in the dataPoints array. 
# 		It allows user to 
#
##########################################################################################################################################################################################################################################
#	Script OUtputs:
#		This script has no outputs
#
##########################################################################################################################################################################################################################################
#	Wrapper class functions referenced in script: 
# 		Wrapper class is called DataFileIOLibrary and is included in the ICS_IPA library. The instance of this class used in this script is called data.
#		The data object is instantiated with the config file and 1 data file. The constructor opens the file and sets up the numpy ndarray that tracks
#		the values of the signals in the config at the time corresponding to the virtual cursor. 
#
# 		JumpBeforeTimestamp(TimeInFileInSeconds)
#			This function positions the virtual time cursor within the file at the time stamp that is the nearest time preceeding TimeInFileInSeconds.
#			The virtual time cursor is always placed at an exact timestamp corresponding to the Active siganls defined with the SetActiveMask function.
#			This function returns the exact time stamp of the virtual time cursor. If TimeInFileInSeconds is less than the first time stamp it will 
#			jump to the first record in the file. If TimeInFileInSeconds is greater than the length of the file it will jump to the last record. 
#
# 		GetNextRecord()
#			This function moves the virtual time cursor to the next record in the file corresponding to exact time stamps of the Active signals. 
#			Whenever the virtual time curor is moved, the dataPoints array is updated for all signals with the values corresponding the nearest time
#			preceeding the virtual time cursor position. All signals values are updated regardless of whether they are active or not. 
#
#			This function returns the time for the new position of the time cursor. If this function is called with the cursor at the last record in the
#			file, it returns max double. 
#		
# 		GetNextChangedRecord()
#			This function moves the virtual time cursor to the next record in the file corresponding to exact time stamps of the Active signals where
# 			at least one signal value has changed from the value at the current virtual time cursor position. This function allows you to jump over 
# 			sections of data where the values aren't changing.
#  
#			Whenever the virtual time curor is moved, the dataPoints array is updated for all signals with the values corresponding the nearest time
#			preceeding the virtual time cursor position. All signals values are updated regardless of whether they are active or not. 
#
#			This function returns the time for the new position of the time cursor. If this function is called with the cursor at the last record in the
#			file, it returns max double.
#
#  		GetPoints()
#			This function returns a reference to the numpy ndarray that holds the values of all of the siganls referenced in the config file at the time
# 			in the file matching the virtual time cursor. Since it is a reference to an array, you don't need to copy the values to a new array every
#			time you reposition the virtual time cursor. 
#
# 			The order of the signals values in this array match the order of the signals in the config file channels key.
#
# 		GetTimeStamps()
#			This function returns a reference to the numpy ndarray that holds the exact time stamps of all of the siganls referenced in the config file at 
# 			the time in the file that is the nearest time preceeding the virtual time cursor. Since it is a reference to an array, you don't need to copy 
# 			the values to a new array every time you reposition the virtual time cursor. 
#
# 			The order of the signals time stamps in this array match the order of the signals in the config file channels key.
#		
#		SetActiveMask(SetActiveMaskString)
#			This function controls which signals in the config file are used for the time basis during file navigation. When you jump to a timestamp or
# 			call GetNextRecord, the DataFileIOLibrary only checks timestamps in the file that correspond to signals described in the SetActiveMaskString.
#			The SetActiveMaskString is a string of ones and zeros with length matching the number of channels in the config file. 
#
#########################################################################################################################################################################################################################################

import numpy as np
import datetime
import pprint
import enum
import sys
import os
import logging
import json
import re 

from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary
from FindInFilesEventClass import FindInFilesEvents
from  SigEnumFile import Sig

def SetTimeBasisSignals(SigListFromConfigFile, TimeBasisSignalList):
	SetActiveMaskString = ''
	for signal in SigListFromConfigFile:
		NumberOfTimeBasisSignals = len(TimeBasisSignalList)
		CurrentSignalInTimeBasisList = False
		for i in range(NumberOfTimeBasisSignals):
			if signal == TimeBasisSignalList[i]:
				CurrentSignalInTimeBasisList = True
		if CurrentSignalInTimeBasisList:
			SetActiveMaskString = SetActiveMaskString + '1'
		else:
			SetActiveMaskString = SetActiveMaskString + '0'
	return SetActiveMaskString


logging.basicConfig(level=logging.INFO)
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

#now go through each file, look for hits and log hits to dsr file
FileNumber = 0
for dbFilePath in dbFilePaths:
	try:
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
			ActiveMaskResult = data.SetActiveMask(SetActiveMaskString)
			curTimestamp = data.JumpBeforeTimestamp(0)
			dataPoints = data.GetPoints()
			#dataPoints[Sig.TransOutputSpeed]
			#dataPoints[Sig.TransTurbineSpeed]
			#dataPoints[Sig.EngineSpeed]
			#dataPoints[Sig.AccelPedalPosition]
			#dataPoints[Sig.EngineStateVariable1]
			
			timeStamps = data.GetTimeStamps()
			#timeStamps[Sig.TransOutputSpeed]
			#timeStamps[Sig.TransTurbineSpeed]
			#timeStamps[Sig.EngineSpeed]
			#timeStamps[Sig.AccelPedalPosition]
			#timeStamps[Sig.EngineStateVariable1]
			dataPointsPrev = dataPoints.copy()

			#initialize event based arrays
			RecordIncludesExpressionEndEvent = False
			AlreadyJumped = False
			while curTimestamp < sys.float_info.max:
				if curTimestamp < 0.5:
					curTimestamp = data.GetNextRecord()
				elif (curTimestamp >= 0.5):
					TimeBasisSigList = ['TransTurbineSpeed', 'TransOutputSpeed']
					SetActiveMaskString = SetTimeBasisSignals(Sig_list, TimeBasisSigList)
					ActiveMaskResult = data.SetActiveMask(SetActiveMaskString)
					if AlreadyJumped == False:
						curTimestamp = data.JumpBeforeTimestamp(5)
						AlreadyJumped = True
					curTimestamp = data.GetNextChangedRecord()
				dataPointsPrev = dataPoints.copy()# copy previous loops record array to new array				
				#log.info(str(curTimestamp))
	
	except ValueError as e :
		print(str(e))

log.info("Good Bye")
