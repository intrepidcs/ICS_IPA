import numpy as np
import datetime
import pprint
import enum
import sys
import os
import logging 

from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary
from SigEnumFile import Sig 

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
handler = logging.FileHandler('IPA.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

slFilePath = IPAInterfaceLibrary.get_config_file()
dbFilePaths = IPAInterfaceLibrary.get_input_file_list()

log.info("Hello")

#------------------------------------------------------------------------------------------------------------------
dsr = icsDSR.DSRFile()
#there are multiple methods to save to a dsr file.
a = 0
for dbFilePath in dbFilePaths:
	MaskString = ""
	with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
		curTimestamp = data.JumpBeforeTimestamp(0)
		dataPoints = data.GetPoints() 		# dataPoints[Sig.TransOutputSpeed], dataPoints[Sig.TransTurbineSpeed], dataPoints[Sig.EngineSpeed], dataPoints[Sig.AccelPedalPosition]
		timeStamps = data.GetTimeStamps()	# timeStamps[Sig.TransOutputSpeed], timeStamps[Sig.TransTurbineSpeed], timeStamps[Sig.EngineSpeed], timeStamps[Sig.AccelPedalPosition]
		dsr.Begin(data)
		for i in range (0, Sig.MaxIndexInSigClass):
			if i == Sig.AccelPedalPosition:
				MaskString = MaskString + "1"
			else:
				MaskString = MaskString + "0"
		ActiveMaskResult = data.SetActiveMask(MaskString)
		while curTimestamp != sys.float_info.max: #curTimestamp set to max double once end of file reached
			dsr.IncludeCurrentRecord(dataPoints[Sig.EngineSpeed] > 4000 and dataPoints[Sig.AccelPedalPosition] < 40)
			curTimestamp = data.GetNextChangedRecord()
			if curTimestamp > 363:
				a = a
		dsr.End()

#------------------------------------------------------------------------------------------------------------------
ReportGenTimeStamp = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
DSRFilename = "FindInFiles_" + ReportGenTimeStamp + ".dsr" 
#------------------------------------------------------------------------------------------------------------------
log.info("Good Bye")

dsr.save(DSRFilename)