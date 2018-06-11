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
from  SigEnumFile import Sig 

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

#------------------------------------------------------------------------------------------------------------------
dsr = icsDSR.DSRFile()
#there are multiple methods to save to a dsr file.

#convert expressions in syntax that can be used by eval function
with open(slFilePath) as configFile:
	config = json.load(configFile)

ScriptChannels = config["Channels"]
NumberOfSignals = len(ScriptChannels)
Sig_list = [Channel['name_in_script'] for Channel in ScriptChannels]
Events = config["EventDefinitions"]
NumberOfExpressions = len(Events)
SearchExpState = [False] * NumberOfExpressions
EventActive = [False] * NumberOfExpressions
EventActivePrev = [False] * NumberOfExpressions
SearchExpStartTime = [0.0] * NumberOfExpressions
SearchExpEndTime = [0.0] * NumberOfExpressions
TimeFromExpressionStart = [0.0] * NumberOfExpressions

EventDescription_list = [Event['Description'] for Event in Events]
StartExpression_list = [Event['StartExpression'] for Event in Events]

StartExpressionEval = []
for expression in StartExpression_list:
	ConvertedExpression = expression
	for signal in Sig_list:
		ConvertedExpression = re.sub(r'\b' + signal + r"\b", 'dataPoints[Sig.'+ signal + ']', ConvertedExpression)
	#now check for Prev__ indicating a desire to reference previous loop values
	PrevRecList = re.findall(r'\b' +'Prev__'+r'\w+', ConvertedExpression)
	for PrevRecSig in PrevRecList:
		ConvertedExpression = re.sub(PrevRecSig, 'dataPointsPrev[Sig.'+ PrevRecSig[6-len(PrevRecSig):] + ']', ConvertedExpression, count=1)
	StartExpressionEval.append(ConvertedExpression)


EndExpression_list = [Event['EndExpression'] for Event in Events]
EndExpressionEval = []
for expression in EndExpression_list:
	ConvertedExpression = expression
	for signal in Sig_list:
		ConvertedExpression = re.sub(signal, 'dataPoints[Sig.'+ signal + ']', ConvertedExpression)
	#now check for Prev__ indicating a desire to reference previous loop values
	PrevRecList = re.findall(r'\b' +'Prev__'+r'\w+', ConvertedExpression)
	for PrevRecSig in PrevRecList:
		ConvertedExpression = re.sub(PrevRecSig, 'dataPointsPrev[Sig.'+ PrevRecSig[6-len(PrevRecSig):] + ']', ConvertedExpression, count=1)
	ConvertedExpression = re.sub('TimeFromExpStart', 'TimeFromExpressionStart[i]', ConvertedExpression)
	EndExpressionEval.append(ConvertedExpression)

#now create a string for SetActiveMask with only first signal active
SetActiveMaskString = ''
NumberOrSignals = 0
for signal in Sig_list:
	if signal == "AccelPedalPosition":
		SetActiveMaskString = SetActiveMaskString + '1'
	else:
		SetActiveMaskString = SetActiveMaskString + '0'
	NumberOrSignals = NumberOrSignals + 1

for dbFilePath in dbFilePaths:
	try:
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
			curTimestamp = data.JumpBeforeTimestamp(0)
			dataPoints = data.GetPoints()
			dataPointsPrev = dataPoints.copy()
			ActiveMaskResult = data.SetActiveMask(SetActiveMaskString)
			#initialize event based arrays
			for i, expressionStart in enumerate(StartExpressionEval):
				EventActive[i] = False
				EventActivePrev[i] = False
				SearchExpState[i] = False
			while curTimestamp != sys.float_info.max:
				for i, expressionStart in enumerate(StartExpressionEval):
					if EventActive[i] == False:
						SearchExpState[i] = eval(expressionStart)	
					else:
						SearchExpState[i] = eval(EndExpressionEval[i])
					if EventActive[i] == False and SearchExpState[i] == True:
						SearchExpStartTime[i] = curTimestamp
						EventActive[i] = True
						TimeFromExpressionStart[i] = 0
					if EventActive[i] and EventActivePrev[i]:
						if SearchExpState[i] == True:
							SearchExpEndTime[i] = curTimestamp
							dsr.IncludeHit(data, SearchExpStartTime[i], SearchExpEndTime[i], EventDescription_list[i])
							EventActive[i] = False
							TimeFromExpressionStart[i] = - 1
						else:
							TimeFromExpressionStart[i] = curTimestamp - SearchExpStartTime[i]
					EventActivePrev[i] = EventActive[i]
				dataPointsPrev = dataPoints.copy()# copy previous loops record array to new array
				curTimestamp = data.GetNextRecord()
				#log.info(str(curTimestamp))
			#if any events are active at the end of file, log the last time stamp as the end of hit
			for i, expressionStart in enumerate(StartExpressionEval):
				if EventActive[i]:
					dsr.IncludeHit(data, SearchExpStartTime[i], data.GetMeasurementTimeBounds()[2] - data.GetMeasurementTimeBounds()[1], EventDescription_list[i])
	except ValueError as e :
		print(str(e))

#------------------------------------------------------------------------------------------------------------------
ReportGenTimeStamp = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
DSRFilename = "FindInFiles_" + ReportGenTimeStamp + ".dsr" 
#------------------------------------------------------------------------------------------------------------------

# now combine the signal list and hit list to a new JSON file and output to an mdf file
SignalListWithHitList = {"SpacingBetweenHitsInOuputFile" : 1}
SignalListWithHitList.update(config)
SignalListWithHitList.update(dsr.dsr)#["HitList"])suggestiong from Zaid
OutputJSONFileNameAndPath = os.getcwd() + "\OutputHitList_" + ReportGenTimeStamp + ".json"
with open(OutputJSONFileNameAndPath, 'w') as outfile:
	json.dump(SignalListWithHitList, outfile, sort_keys=True, indent=4)
MDFOutputFileNameAndPath = os.getcwd() + "\MDFSubset_" + ReportGenTimeStamp + ".mf4"

OutputHitsResult = icsFI.OutputHitsToFile(OutputJSONFileNameAndPath, MDFOutputFileNameAndPath)

log.info("Good Bye")

dsr.save(DSRFilename)