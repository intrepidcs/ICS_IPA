import numpy as np
import datetime
import pprint
import enum
import sys
import os

from ICS_IPA import DataFileIOLibrary as icsFI
from ICS_IPA import DSRTools as icsDSR
from ICS_IPA import IPAInterfaceLibrary

jsonFileName = IPAInterfaceLibrary.get_config_file()
filenames = IPAInterfaceLibrary.get_input_file_list()

#------------------------------------------------------------------------------------------------------------------
dsr = icsDSR.DSRFile()
#there are multiple methods to save to a dsr file.
for filename in filenames:
	with icsFI.ICSDataFile(filename, jsonFileName) as data:

		accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
		transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")
		
		curTimestamp = data.JumpAfterTimestamp(0)
		dataPoints = data.GetPoints()
		dsr.Begin(data)
		while curTimestamp != sys.float_info.max:
			dsr.IncludeCurrentRecord(dataPoints[accelpedalPostionIndex] > 80 and dataPoints[transOutputSpeedIndex] < 1600)
			curTimestamp = data.GetNextRecord()
		dsr.End()
 
#------------------------------------------------------------------------------------------------------------------


#dsr = icsDSR.CreateDSR()
for filename in filenames:
	with icsFI.ICSDataFile(filename, jsonFileName) as data:

		accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
		transOutputSpeedIndex = data.indexOfSignal("TransOutputSpeed")
		#the first is using lambdas, you can think of lambdas as functions without a name 
		#the following lambda has two parameters v and t. v for values and t for time
		#the AddToDSR function takes a function with two paramaters as an argument
		#The AddToDSR calls the function for every data point it iterates though to determan if it should be included in the DSR file
		#The following two calls do the same thing in two diffrent ways the first uses a lambda

		dsr.Add(data, lambda v, t: v[accelpedalPostionIndex] > 80 and v[transOutputSpeedIndex] < 1600)

#------------------------------------------------------------------------------------------------------------------
#The second simply passes a function
from  SigEnumFile import Sig 

def checkFullThrotel (values, timestamp):
	return values[Sig.AccelPedalPosition] > 80 and values[Sig.TransOutputSpeed] < 1600


for filename in filenames:
	with icsFI.ICSDataFile(filename, jsonFileName) as data:
		
		dsr.Add(data, checkFullThrotel, "Full Throtel hit")

#------------------------------------------------------------------------------------------------------------------
#The Third method uses a class
class dataCheck:
	def __init__(self):
		self.AccelPedalPositionMax = 80
		self.TransOutputSpeedMin = 1600

	def __call__(self, values, timestamp): #this is the required callback function for the class
		return values[Sig.AccelPedalPosition] > self.AccelPedalPositionMax and values[Sig.TransOutputSpeed] < self.TransOutputSpeedMin

dc = dataCheck()
for filename in filenames:
	with icsFI.ICSDataFile(filename, jsonFileName) as data:
		
		dsr.Add(data, dc, hitDiscretion = "Class Example hit")

#------------------------------------------------------------------------------------------------------------------

#The Third method uses a class
class AdvancedDataCheck:
	def __init__(self):
		self.previousAccelPedalPosition = None
		self.TransOutputSpeedMin = 1600

	def __call__(self, values, timestamp): #this is the required callback function for the class
		if self.previousAccelPedalPosition is None:
			self.previousAccelPedalPosition = values[Sig.AccelPedalPosition]
			return 
		return values[Sig.AccelPedalPosition] > self.AccelPedalPositionMax and values[Sig.TransOutputSpeed] < self.TransOutputSpeedMin

dc = dataCheck()
for filename in filenames:
	with icsFI.ICSDataFile(filename, jsonFileName) as data:
		
		dsr.Add(data, dc, hitDiscretion = "Class Example hit")

#------------------------------------------------------------------------------------------------------------------
dsr.save("Example.dsr")