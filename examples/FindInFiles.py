import numpy as np
import datetime
import pprint
import enum
import sys
import os

from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary
from  SigEnumFile import Sig 

slFilePath = IPAInterfaceLibrary.get_config_file()
dbFilePaths = IPAInterfaceLibrary.get_input_file_list()

#------------------------------------------------------------------------------------------------------------------
dsr = icsDSR.DSRFile()
#there are multiple methods to save to a dsr file.

for dbFilePath in dbFilePaths:
	try :
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
			
			curTimestamp = data.JumpAfterTimestamp(0)
			dataPoints = data.GetPoints()
			dsr.Begin(data)
			while curTimestamp != sys.float_info.max:
				dsr.IncludeCurrentRecord(dataPoints[Sig.AccelPedalPosition] > 80 and dataPoints[Sig.TransOutputSpeed] < 1600)
				curTimestamp = data.GetNextRecord()
			dsr.End()
	except ValueError as e :
		print(str(e))
 
#------------------------------------------------------------------------------------------------------------------
ReportGenTimeStamp = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
DSRFilename = "FindInFiles_" + ReportGenTimeStamp + ".dsr" 
#------------------------------------------------------------------------------------------------------------------
dsr.save(DSRFilename)