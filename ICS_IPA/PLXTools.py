import json

class PLXFile:
	def __init__(self):
		self.plx =  { "Version": "1.0.0", "Plotly" : {}}
		self.plx["Plotly"]["data"] = []
		self.plx["Plotly"]["layout"] = {}
		self.plx["Plotly"]["frames"] = {}
		self.plx["Plotly"]["config"] = {}

	def AddAttribute(self, attribute, plyclass : str, key  = None, keylist : list = None) -> None:
		if keylist != None:
			currentLocation = self.plx["Plotly"][plyclass]
			for index in range(len(keylist) - 1):
				if type(currentLocation) is dict:
					currentLocation = currentLocation.get(keylist[index])
				elif type(currentLocation) is list:
					currentLocation = currentLocation[keylist[index]]
				else:
					raise TypeError("Location is not list or dictionary, please review key/keylist")
				currentLocation[keylist[-1]] = attribute
		else:
			currentLocation = self.plx["Plotly"][plyclass]
			if type(currentLocation) is dict:
				currentLocation[key] = attribute
			elif type(currentLocation) is list:
				currentLocation.append(attribute)
			else:
				raise TypeError("Location is not list or dictionary, please review key/keylist")
	def UpdateDict(self, updateDictionary, plyclass : str, keylist : list = None) -> None:
		if keylist == None:
			self.plx["Plotly"][plyclass].update(updateDictionary)
		else:
			currentLocation = self.plx["Plotly"][plyclass]
			for index in range(len(keylist) - 1):
				currentLocation = currentLocation.get(keylist[index])
			currentLocation[keylist[-1]].update(updateDictionary)

	
	def RemoveAttribute(self, plyclass : str, key : str = None, keylist : list = None) -> None:
		if key == None and keylist == None:
			raise KeyError("No key or key list given")
		elif key != None:
			del self.plx["Plotly"][plyclass][key]
		else:
			currentLocation = self.plx["Plotly"][plyclass]
			for index in range(len(keylist) - 1):
				currentLocation = currentLocation.get(keylist[index])
			del currentLocation[keylist[-1]]
		
	def save(self, filename : str) -> None:
		fname = filename + ".plx"
		with open(fname, 'w') as outfile:
			json.dump(self.plx, outfile, sort_keys=True, indent=4)

class SubPlotAxisLayout:
	def __init__(self, number_of_signals):
		#use dict.update() on layout when you return [self.xaxes, self.yaxes]
		self.signalcount = number_of_signals
		self.xaxes = {"xaxis" : {}}
		self.yaxes = {"yaxis" : {}}
		for sig_num in range(1, self.signalcount):
			self.xaxes[('xaxis' + str(sig_num + 1))] = {}
			self.yaxes[('yaxis' + str(sig_num + 1))] = {}
		#set domains
		if self.signalcount <= 3:
			region = 1 / self.signalcount
			region = round(region, 3)
			current_location = 0
			for axis in self.xaxes:
				if current_location + region <= 1:
					self.xaxes[axis]["domain"] = [current_location, current_location + region - .05]
				else:
					self.xaxes[axis]["domain"] = [current_location, 1]
				current_location += region + .05
			num = 0
			for axis in self.yaxes:
				self.yaxes[axis]["domain"] = [0, 1]
				if num >= 1:
					self.yaxes[axis]["anchor"] = 'x' + str(num + 1)
				num += 1
		elif self.signalcount == 4:
			current_location = 0
			num = 0
			for axis in self.xaxes:
				self.xaxes[axis]["domain"] = [current_location, current_location + .45]
				current_location += .55
				if num >= 2:
					self.xaxes[axis]["anchor"] = 'y' + str(num + 1)
				if num == 1:
					current_location = 0
				num += 1	
			current_location = 0
			num = 0
			for axis in self.yaxes:
				self.yaxes[axis]["domain"] = [current_location, current_location + .4]
				if num == 1:
					current_location += .6
				if num == 1 or num == 3:
					self.yaxes[axis]["anchor"] = 'x' + str(num + 1)
				num += 1
		elif self.signalcount <= 6:
			region = 1/3
			region = round(region, 3)
			current_location = 0
			num = 0
			for axis in self.xaxes:
				if current_location + region <= 1:
					self.xaxes[axis]["domain"] = [current_location, current_location + region - .025]
				else:
					self.xaxes[axis]["domain"] = [current_location, 1]
				current_location += region + .025
				if current_location >= 1:
					current_location = 0
					region = 1 / (self.signalcount - 3)	
					region = round(region, 3) 
				if num >= 3 or num == 1:
					self.xaxes[axis]["anchor"] = 'y' + str(num + 1)
				num += 1	
			current_location = 0
			num = 0
			for axis in self.yaxes:
				self.yaxes[axis]["domain"] = [current_location, current_location + .35]
				if num == 2:
					current_location = .65
				if num >= 1 and num != 3:
					self.yaxes[axis]["anchor"] = 'x' + str(num + 1)
				num += 1
				

	def AddLabels(self, xLabels : list = None, yLabels : list = None):
		if xLabels != None:
			self.xaxes['xaxis']['title'] = xLabels[0]
			if len(xLabels) > 1:
				for index in range(1, len(xLabels)):
					axis = 'xaxis' + str(index + 1)
					self.xaxes[axis]['title'] = xLabels[index]
		if yLabels != None:
			self.yaxes['yaxis']['title'] = yLabels[0]
			if len(yLabels) > 1:
				for index in range(1, len(yLabels)):
					axis = 'yaxis' + str(index + 1)
					self.yaxes[axis]['title'] = yLabels[index]
	def GetXDictionary(self) -> dict:
		return self.xaxes
	def GetYDictionary(self) -> dict:
		return self.yaxes




