import sys
import os
import numpy as np
import pprint
import json
from ICS_IPA.DataFileIOLibraryInterface import *

class ICSDataFile:
	def __init__(self, dbFile, jsonFileName, AutoCleanUpTempFiles = True):
		self.UsingTempFile = False
		if "path" not in dbFile:
			raise ValueError('invalid dbFile')
		dbFileName = dbFile["path"]
		if len(dbFileName) > 0:
			name, extension = os.path.splitext(dbFileName)
			if extension.lower() != ".db":
				if not os.path.isfile(name + ".db"):
					CreateDatabaseForSignals(dbFileName, jsonFileName, name + ".db")
					self.UsingTempFile = True
				dbFileName = name + ".db"

		self.dbFile = dbFile
		self.dbFileName = dbFileName
		self.jsonFileName = jsonFileName
		self.AutoCleanUpTempFiles = AutoCleanUpTempFiles
		self.measStart, self.points, self.timestamps = OpenDataFile(self.dbFileName, self.jsonFileName)
		self.RecordTimestamp = -1

		with open(jsonFileName) as data_file:  
			data = json.load(data_file)
			self.nameToIndex = { channel["name"]: index for index, channel in enumerate(data["Channels"])}
			self.indexToName = { index: channel["name"] for index, channel in enumerate(data["Channels"])}
		
	def __getitem__(self, key):
		''' this method of retrieving data is slower then simply asking for the timestamp and points array'''
		if type(key) == str and key in self.nameToIndex:
			index = self.nameToIndex[key]
			return {"name": key, "index": index, "point": self.points[index], "time": self.timestamps[index]}
		elif type(key) == int and key in self.indexToName:
			return {"name": self.indexToName[key], "index": key, "point": self.points[key], "time": self.timestamps[key]}
		else:
			{}

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		CloseDataFile(self.points)
		if self.UsingTempFile and self.AutoCleanUpTempFiles:
			os.remove(self.dbFileName)

	def indexOfSignal(self, sigName):
		return self.nameToIndex[sigName] if sigName in self.nameToIndex else -1

	def __del__(self):
		CloseDataFile(self.points)
		if self.UsingTempFile and self.AutoCleanUpTempFiles:
			os.remove(self.dbFileName)

	def GetNumChannels(self):
		return GetNumChannels(self.jsonFileName)

	def GetMeasurementStart(self):
		return self.measStart

	def GetPoints(self):
		return self.points

	def GetTimeStamps(self):
		return self.timestamps

	def SetActiveMask(self, mask):
		""" Allows the user to position the time cursor just before or at the specified
		 *  time value.  This call updates the channel values and timestamps.  If only some 
		 *  channels are active, the nearest active channel's timestamp is used.
		 *  
		 *  If an error ocurred, the return value is DBL_MAX
		 *
		 *  Timestamps represent the number of seconds since January 1, 2007.  The decimals 
		 *  represent fractions of seconds.
		 *
		 *  @param dTime         The timestamp to jump to
		 *  @return The actual timestamp the cursor is on
		 """
		return SetActiveMask(self.points, mask)	

	def JumpAfterTimestamp(self, timestamp):
		""" Allows the user to position the time cursor just after or at the specified
		 *  time value.  This call updates the channel values and timestamps.  The first
		 *  timestamp where all channels have a value and which is at or after the requested
		 *  time.  If only some channels are active, the nearest active channel's timestamp is
		 *  used.
		 *  
		 *  If an error ocurred, the return value is DBL_MAX
		 *
		 *  Timestamps represent the number of seconds since January 1, 2007.  The decimals 
		 *  represent fractions of seconds.
		 *
		 *  @param dTime         The timestamp to jump to
		 *  @return The actual timestamp the cursor is on
		 """
		self.RecordTimestamp = JumpAfterTimestamp(self.points, timestamp) 
		return self.RecordTimestamp

	def JumpBeforeTimestamp(self, timestamp):
		""" Allows the user to position the time cursor just before or at the specified
		 *  time value.  This call updates the channel values and timestamps.  The first
		 *  timestamp where all channels have a value and which is at or after the requested
		 *  time.  If only some channels are active, the nearest active channel's timestamp is
		 *  used.
		 *  
		 *  If an error ocurred, the return value is DBL_MAX
		 *
		 *  Timestamps represent the number of seconds since January 1, 2007.  The decimals 
		 *  represent fractions of seconds.
		 *
		 *  @param indatapointer The datapointer value received from the OpenDataFile call
		 *  @param n             The number of channels (size of the datapointer array)
		 *  @param dTime         The timestamp to jump to
		 *  @return The actual timestamp the cursor is on
		"""
		self.RecordTimestamp = JumpBeforeTimestamp(self.points, timestamp)
		return self.RecordTimestamp

	def GetNextRecord(self):
		""" Advances the cursor to the next timestamp.  This call updates the channel
		 *  values and timestamps.  If only some channels are active, the next timestamp of
		 *  an active channel is the one returned.
		 *  
		 *  If an error ocurred, the return value is DBL_MAX
		 *
		 *  Timestamps represent the number of seconds since January 1, 2007.  The decimals 
		 *  represent fractions of seconds.
		 *
		 *  @param indatapointer The datapointer value received from the OpenDataFile call
		 *  @param n             The number of channels (size of the datapointer array)
		 *  @return The actual timestamp the cursor is on
		"""
		self.RecordTimestamp = GetNextRecord(self.points)
		return self.RecordTimestamp


	def GetMeasurementTimeBounds(self):
		""" Returns the start and end or measurement times found in the file.
		 *  
		 *  If an error ocurred, the return value is 0.
		 *
		 *  Timestamps used throughout represent the number of seconds since
		 *  January 1, 2007.  The decimals represent fractions of seconds.
		 *
		 *  @param pMask         A string of size n containing the character '1' for active
		 *                       channels and '0' for non-active channels.  Please note that
		 *                       only '0' and '1' are valid values.
		 *  @return 1 for success, 0 for error, -1 for licensing issues
		"""
		return GetMeasurementTimeBounds(self.points) 	

#the following test function is simply here to test a basic example
def test():
	print("Start of Test")
	import tkinter as tk
	from tkinter import filedialog
	root = tk.Tk()
	root.withdraw()
	dbFileName = filedialog.askopenfilename(parent=root, filetypes = (("db files", "*.db"), ("All files", "*.*")))
	jsonFileName = filedialog.askopenfilename(parent=root, filetypes = (("json files", "*.json"), ("All files", "*.*")))
	data = ICSDataFile(dbFileName, jsonFileName)
	curTimestamp = data.JumpAfterTimestamp(0)
	minarray = np.copy(data.GetPoints())
	maxarray = np.copy(data.GetPoints())

	while curTimestamp != sys.float_info.max:
		np.minimum(minarray, data.GetPoints(), out=minarray)
		np.maximum(maxarray, data.GetPoints(), out=maxarray)		
		curTimestamp = data.GetNextRecord()

	print(minarray)
	print(maxarray)
	print("End of Test")

def test2():
	from  SigEnumFile import Sig 
	def cheekfullThrotel (values, timestamp):
		return values[Sig.AccelPedalPosition] > 80 and values[Sig.TransOutputSpeed] < 1600

	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
	from Libraries import IPAInterfaceLibrary

	jsonFileName = IPAInterfaceLibrary.get_config_file()
	filenames = IPAInterfaceLibrary.get_input_file_list()
	dsr = CreateDSR()

	for filename in filenames:
		data = ICSDataFile(filename, jsonFileName)

		accelpedalPostionIndex = data.indexOfSignal("AccelPedalPosition")
		transOutputSpeedndex = data.indexOfSignal("TransOutputSpeed") 

		dsr.AppendToDSR(data, lambda p, t: p[accelpedalPostionIndex] > 80 and p[transOutputSpeedndex] < 1600)
		dsr.AppendToDSR(data, cheekfullThrotel, "Full Throtel hit")

	dsr.save()

if __name__ == "__main__":
	test2()

# This file is compatible with both classic and new-style classes.

# This file is compatible with both classic and new-style classes.


