from ICS_IPA import IPAInterfaceLibrary
import sys
import json
import os

class DSRFile:
	def __init__(self):
		self.dsr =  {"HitList" : []}
		self.data_to_hitlist = {}

#--------------------------------------------------------- method 1 ------------------------------------------------------
	def Begin(self, data, hitDescription = "Hit number ", initTrigger=False):
		self.numRec = 0
		self.triggered = initTrigger
		self.hitDescription = hitDescription
		self.data = data
		if IPAInterfaceLibrary.is_running_on_wivi_server():
			filenamewithoutpath = os.path.basename(data.dbFile["path"])
			self.dsr["HitList"].append({"id": data.dbFile["id"], "startDate": data.dbFile["startDate"], "vehicle": data.dbFile["vehicle"], "Filename": filenamewithoutpath})	
		else:
			self.dsr["HitList"].append({"FilenameAndPath": data.dbFile["path"]})
		self.data_to_hitlist[data] = self.dsr["HitList"][-1]

	def IncludeCurrentRecord(self, included):
		if included:
			if not self.triggered:
				if "Hits" not in self.dsr["HitList"][-1]:
					self.dsr["HitList"][-1]["Hits"] = []
				self.dsr["HitList"][-1]["Hits"].append({"Description" : self.hitDescription + str(self.numRec), "StartTime": self.data.RecordTimestamp })
				self.numRec += 1
				self.triggered = True
		elif self.triggered:
			self.dsr["HitList"][-1]["Hits"][-1]["EndTime"] = self.data.RecordTimestamp
			self.triggered = False

	def End(self):
		if self.triggered:
			self.dsr["HitList"][-1]["Hits"][-1]["EndTime"] = self.data.GetMeasurementTimeBounds()[2] - self.data.GetMeasurementTimeBounds()[1]	

#--------------------------------------------------------- method 2 ------------------------------------------------------

	def IncludeHit(self, data, hitStartTime, hitEndTime, hitDescription = "Include Hit"):
		if data not in self.data_to_hitlist:
			self.Begin(data)
		hitlist = self.data_to_hitlist[data]
			
		if "Hits" not in hitlist:
			hitlist["Hits"] = []
		hitlist["Hits"].append({"Description" : hitDescription, "StartTime": hitStartTime, "EndTime": hitEndTime})

#--------------------------------------------------------- method 3 ------------------------------------------------------

	def Add(self, data, callback, hitDiscretion = "Hit number ", initTrigger=False):
		'''
		the Add function takes two arguments the first being ICSData class and the second being a function with two paramaters as an argument
		The Add calls the function for every data point it iterates though to determan if it should be included in the DSR file
		'''
		curTimestamp = data.JumpAfterTimestamp(0)
		self.Begin(data, hitDiscretion, initTrigger)
		points = data.GetPoints()
		timestamp = data.GetTimeStamps()
		while curTimestamp != sys.float_info.max:
			self.IncludeCurrentRecord(callback(points, timestamp))
			curTimestamp = data.GetNextRecord()
		self.End()

	def save(self, filename = "data.dsr"):
		with open(filename, 'w') as outfile:
			json.dump(self.dsr, outfile, sort_keys=True, indent=4)
