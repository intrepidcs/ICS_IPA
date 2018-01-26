import numpy as np
import datetime
import pprint
import enum
import sys
import os
import logging
import time 

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

logger.addHandler(ch)

from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary

slFilePath = IPAInterfaceLibrary.get_config_file()
dbFilePaths = IPAInterfaceLibrary.get_input_file_list()



#------------------------------------------------------------------------------------------------------------------
dsr = icsDSR.DSRFile()
#there are multiple methods to save to a dsr file.

t0 = time.time()
for dbFilePath in dbFilePaths:
	try :
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:

			accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
			transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")
			
			curTimestamp = data.JumpAfterTimestamp(0)
			dataPoints = data.GetPoints()
			dsr.Begin(data)
			while curTimestamp != sys.float_info.max:
				dsr.IncludeCurrentRecord(dataPoints[accelpedalPostionIndex] > 80 and dataPoints[transOutputSpeedIndex] < 1600)
				curTimestamp = data.GetNextRecord()
			dsr.End()
	except ValueError as e :
		print(str(e))
logger.info("Finished DSR  Time Taken " + str(time.time() - t0)) 
#------------------------------------------------------------------------------------------------------------------


t0 = time.time()
for dbFilePath in dbFilePaths:
	try :
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:

			accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
			transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")
			#the first is using lambdas, you can think of lambdas as functions without a name 
			#the following lambda has two parameters v and t. v for values and t for time
			#the AddToDSR function takes a function with two paramaters as an argument
			#The AddToDSR calls the function for every data point it iterates though to determan if it should be included in the DSR file
			#The following two calls do the same thing in two diffrent ways the first uses a lambda

			dsr.Add(data, lambda v, t: v[accelpedalPostionIndex] > 80 and v[transOutputSpeedIndex] < 1600)
	except ValueError as e :
		print(str(e))
logger.info("Finished DSR  Time Taken " + str(time.time() - t0)) 

#------------------------------------------------------------------------------------------------------------------
#The second simply passes a function

t0 = time.time()
def checkFullThrotel (values, timestamp):
	return values[0] > 80 and values[1] < 1600

for dbFilePath in dbFilePaths:
	try :
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:	
			dsr.Add(data, checkFullThrotel, "Full Throtel hit")

	except ValueError as e :
		print(str(e))
logger.info("Finished DSR  Time Taken " + str(time.time() - t0)) 

#------------------------------------------------------------------------------------------------------------------
#The Third method uses a class
t0 = time.time()
class dataCheck:
	def __init__(self, data):
		self.AccelPedalPositionMax = 80
		self.TransOutputSpeedMin = 1600		
		self.accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
		self.transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")

	def __call__(self, values, timestamp): #this is the required callback function for the class
		return values[self.accelpedalPostionIndex] > self.AccelPedalPositionMax and values[self.transOutputSpeedIndex] < self.TransOutputSpeedMin


for dbFilePath in dbFilePaths:
	try :
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:	
			dc = dataCheck(data)
			dsr.Add(data, dc, hitDiscretion = "Class Example hit")
	except ValueError as e :
		print(str(e))
logger.info("Finished DSR  Time Taken " + str(time.time() - t0)) 

#------------------------------------------------------------------------------------------------------------------

t0 = time.time()
class AdvancedDataCheck:
	def __init__(self):
		self.previousAccelPedalPosition = None
		self.TransOutputSpeedMin = 1600
		self.accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")

	def __call__(self, values, timestamp): #this is the required callback function for the class
		if self.previousAccelPedalPosition is None:
			return False			
		returnval =  self.accelpedalPostionIndex > values[self.accelpedalPostionIndex] + 10 
		self.previousAccelPedalPosition = values[self.accelpedalPostionIndex]
		return returnval

for dbFilePath in dbFilePaths:
	try :
		with icsFI.ICSDataFile(dbFilePath, slFilePath) as data:
			dsr.Add(data, dataCheck(data), hitDiscretion = "Class Example hit")
	except ValueError as e :
		print(str(e))
logger.info("Finished DSR  Time Taken " + str(time.time() - t0)) 

#------------------------------------------------------------------------------------------------------------------
dsr.save("Example.dsr")