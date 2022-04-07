from typing import TypeVar

import sys
import os
import numpy as np
import pprint
import json
import logging
import time

from ICS_IPA.DataFileIOLibraryInterface import *
from ICS_IPA import IPAInterfaceLibrary

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# create a file handler
outputDir = os.getcwd()

if IPAInterfaceLibrary.is_running_on_wivi_server() and os.path.splitext(sys.argv[1])[1].lower() == '.json':
	outputDir = json.load(open(sys.argv[1]))["output_dir"]

fh = logging.FileHandler(os.path.join(outputDir, "IPA.log"))
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)


ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
#logger.addHandler(ch)

class ICSDataFile:
	def __init__(self, dbFile: TypeVar('T', str, dict), slFilePath: str, AutoCleanUpTempFiles:bool = True):
		'''
		@param dbFile this can ether be a MDF or a db file generated from an MDF
		@param slFilePath this can ether be a sl file or an asl file
		@param AutoCleanUpTempFiles determins whether the generated files will be deleted 
		'''	
		try :
			t0 = time.time()
			self.slFilePath = slFilePath
			self.IsOpen = True
			self.UsingTempDBFile = False
			self.UsingTempSLFile = False
			self.AutoCleanUpTempFiles = AutoCleanUpTempFiles

			if isinstance(dbFile, str):
				dbFile = {"path": dbFile}
			elif "path" in dbFile:
				pass
			else:
				raise ValueError('invalid db/mdf File Path')
			self.dbFile = dbFile

			logger.info("Start Reading " + os.path.basename(dbFile["path"]))
			if os.path.splitext(slFilePath)[1] == '.asl' or IPAInterfaceLibrary.is_running_on_wivi_server():
				self.slFilePath = self.__ResolveAliases(
					dbFile["path"], 
					slFilePath,
					os.path.join(outputDir, "config.sl") if IPAInterfaceLibrary.is_running_on_wivi_server() else None
				)
				logger.debug("Aliases Resolved")

			self.dbFileName = self.__GetDBFilePath(dbFile["path"], self.slFilePath)
			logger.debug("DB Created")

			self.__OpenDataFile(self.dbFileName, self.slFilePath)
			logger.debug("DB Opened")

			self.__SetupIndexOperator(self.slFilePath)
			logger.debug("Index Operator initialization complete")

			self.RecordTimestamp = -1
			logger.info("Finished Reading " + os.path.basename(dbFile["path"]) + " Time Taken " + str(time.time() - t0))
		except ValueError as e:
			logger.error(str(e))
			raise e

	def __del__(self):
		self.__close()

	def __getitem__(self, key: TypeVar('A', str, bytes)):
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
		self.__close()

	def __close(self):
		if not self.IsOpen:
			return
		self.IsOpen = False
		try:
			CloseDataFile(self.points)
		except:
			pass
		if self.UsingTempDBFile and self.AutoCleanUpTempFiles and os.path.isfile(self.dbFileName):
			os.remove(self.dbFileName)
			self.dbFileName = ''
		if self.UsingTempSLFile and self.AutoCleanUpTempFiles and os.path.isfile(self.slFilePath):
			os.remove(self.slFilePath)
			self.slFilePath = ''
	
	def __GetDBFilePath(self, dbFileName: str, slFilePath: str) -> str:
		''' 
		Called by the constructor to create/verify db file. 
		The db file is created if the filename given is not a db file 
		'''
		if len(dbFileName) > 0:
			name, extension = os.path.splitext(dbFileName)
			if extension.lower() != ".db":
				if not os.path.isfile(name + ".db"):
					val = CreateDatabaseForSignals(dbFileName, slFilePath, name + ".db")
					if val == 0:
						logger.warning("Create Database for Signals error")
					elif val == -1:
						raise ValueError('The Data Spy license is invalid')
					self.UsingTempDBFile = True
				dbFileName = name + ".db"
		return dbFileName

	def __OpenDataFile(self, dbFileName: str, slFilePath: str):
		self.measStart, self.points, self.timestamps = OpenDataFile(dbFileName, slFilePath)
		if self.measStart == 0:
			logger.warning("The number of data channels found does not match the number of channels in the JSON file")
		elif self.measStart == -1:
			raise ValueError('The Data Spy license is invalid')
		elif self.measStart == -2:
			raise ValueError('The Data file is invalid')
		elif self.measStart == -3:
			raise ValueError('The JSON file is invalid')

	def __SetupIndexOperator(self, slFilePath: str):
		with open(slFilePath) as data_file:
			data = json.load(data_file)
			self.nameToIndex = { channel["name"]: index for index, channel in enumerate(data["Channels"])}
			self.indexToName = { index: channel["name"] for index, channel in enumerate(data["Channels"])}

	def __ResolveAliases(self, dbFilePath: str, aslFilePath: str, outpath = None):
		'''
		@param dbFilePath is the database file that you would like to open
		@parama slFilePath is the presumed JSON file with aliases

		@returns JSON file with resolved aliaces if file is valid,
				if file is invalid or does not contain aliases returns 
				aslFilePath 
		'''
		newpath = outpath
		if newpath is None:
			path, filename = os.path.split(aslFilePath)
			filename, extension = os.path.splitext(filename)
			newfilename = '%s%s' % (filename,  ".sl")
			newpath = os.path.join(path, newfilename)
			self.numChannels = ValidateSignals(dbFilePath, aslFilePath, newpath)
		else:
			
			self.numChannels = ValidateSignals(dbFilePath, aslFilePath, newpath)

		if self.numChannels <= 0:
			newpath = aslFilePath
		else:
			self.UsingTempSLFile = True
		if self.numChannels == 0:
			logger.warning("The number of data channels found does not match the number of channels in the JSON file")
		elif self.numChannels == -1:
			raise ValueError('The Data Spy license is invalid')
		elif self.numChannels == -2:
			raise ValueError('The Data file is invalid')
		elif self.numChannels == -3:
			raise ValueError('The JSON file is invalid')
		return newpath
	
	def indexOfSignal(self, sigName: str):
		return self.nameToIndex[sigName] if sigName in self.nameToIndex else -1

	def GetNumChannels(self):
		return GetNumChannels(self.slFilePath)

	def GetMeasurementStart(self):
		return self.measStart

	def GetPoints(self):
		return self.points

	def GetTimeStamps(self):
		"""
		Returns an numpy array containing the timestamp for each signal at 
		"""
		return self.timestamps

	def SetCursorsToStart(self):
		self.RecordTimestamp = SetCursorsToStart(self.points)
		return RecordTimestamp

	def SetActiveMask(self, mask: str):
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

	def JumpAfterTimestamp(self, timestamp: TypeVar('A', float, int)) -> float:
		""" Allows the user to position the time cursor just after or at the specified
		*  time value.  This call updates the channel values and timestamps.  The first
		*  timestamp where all channels have a value and which is at or after the requested
		*  time.  If only some channels are active, the nearest active channel's timestamp is
		*  used.
		*  
		*  If an error ocurred, the return value is DBL_MAX
		*
		*  Timestamps represent the number of seconds since start of measurement.  The decimals 
		*  represent fractions of seconds.
		*
		*  @param dTime         The timestamp to jump to
		*  @return The actual timestamp the cursor is on
		"""
		self.RecordTimestamp = JumpAfterTimestamp(self.points, timestamp) 
		return self.RecordTimestamp

	def JumpBeforeTimestamp(self, timestamp: TypeVar('A', float, int)) -> float:
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
		 *  @param timestamp         The timestamp to jump to
		 *  @return The actual timestamp the cursor is on
		"""
		self.RecordTimestamp = JumpBeforeTimestamp(self.points, timestamp) 
		return self.RecordTimestamp

	def GetNextRecord(self) -> float:
		""" Advances the cursor to the next timestamp.  This call updates the channel
		 *  values and timestamps.  If only some channels are active, the next timestamp of
		 *  an active channel is the one returned.
		 *  
		 *  If an error ocurred, the return value is DBL_MAX
		 *
		 *  @return The actual timestamp the cursor is on
		"""
		self.RecordTimestamp = GetNextRecord(self.points)
		return self.RecordTimestamp

	def GetNextChangedRecord(self) -> float:
		""" Advances the cursor to the next record with changed signal values.
		*  This call updates the channel values and timestamps.  If only some channels are 
		*  active, the next timestamp of an active channel is the one returned.
		*  
		*  If an error ocurred, the return value is DBL_MAX
		*
		*  @return The actual timestamp the cursor is on
		"""
		self.RecordTimestamp = GetNextChangedRecord(self.points)
		return self.RecordTimestamp

	def GetNextValidRecord(self) -> float:
		""" Advances the cursor to the next timestamp.  This call updates the channel
		 *  values and timestamps.  If only some channels are active, the next timestamp of
		 *  an active channel is the one returned.
		 *  
		 *  If an error ocurred, the return value is DBL_MAX
		 *
		 *  @return The actual timestamp the cursor is on
		"""
		self.RecordTimestamp = GetNextValidRecord(self.points)
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
	root.focus_force()
	root.wm_attributes('-topmost', 1)
	dbFileName = filedialog.askopenfilename(parent=root, filetypes = (("db files", "*.db"), ("All files", "*.*")))
	jsonFileName = filedialog.askopenfilename(parent=root, filetypes = (("Lookup files", "*.sl;*.asl"), ("Signal Lookup files", "*.sl"),  ("Aliased Signal Lookup files", "*.asl"), ("All files", "*.*")))
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

if __name__ == "__main__":
	test()

# This file is compatible with both classic and new-style classes.

# This file is compatible with both classic and new-style classes.

