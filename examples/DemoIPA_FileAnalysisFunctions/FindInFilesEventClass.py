import re
import nltk
#from nltk.tokenize import WordPunctTokenizer
from nltk.tokenize import TreebankWordTokenizer
from EvalExpressionWhiteListCheckClass import CheckEvalExpression

class FindInFilesEvents:
	def __init__(self, config):
		self.ScriptChannels = config["Channels"]
		self.Sig_list = [Channel['name_in_script'] for Channel in self.ScriptChannels]
		self.EventDefs = config["EventDefinitions"]
		self.NumberOfEvents = len(self.EventDefs)
		self.EventDescriptions = [""] * self.NumberOfEvents
		self.StartExpression = [""] * self.NumberOfEvents
		self.StartExpressionFormattedForEval = [""] * self.NumberOfEvents
		self.TokensInStartExpression = [""] * self.NumberOfEvents
		self.FirstBlackTokenInStartExpression = ["N/A"] * self.NumberOfEvents
		self.StartExpressionTokensAreInWhiteList = [False] * self.NumberOfEvents
		self.EndExpression = [""] * self.NumberOfEvents
		self.EndExpressionFormattedForEval = [""] * self.NumberOfEvents
		self.TokensInEndExpression = [""] * self.NumberOfEvents
		self.FirstBlackTokenInEndExpression = ["N/A"] * self.NumberOfEvents
		self.EndExpressionTokensAreInWhiteList = [False] * self.NumberOfEvents
		self.SearchExpState = [False] * self.NumberOfEvents
		self.EventActive = [False] * self.NumberOfEvents
		self.EventActivePrev = [False] * self.NumberOfEvents
		self.SearchExpStartTime = [0.0]* self.NumberOfEvents
		self.SearchExpEndTime = [0.0]* self.NumberOfEvents
		self.TimeFromExpressionStart = [0.0]* self.NumberOfEvents
		#instantiate token white list checker object
		self.ExpressionTokenWhiteListChecker = CheckEvalExpression(self.Sig_list)

		for i, Event in enumerate(self.EventDefs):
			self.EventDescriptions[i] = Event['Description']
			self.StartExpression[i] = Event['StartExpression']
			self.StartExpressionFormattedForEval[i] = Event['StartExpression']
			self.StartExpressionTokensAreInWhiteList[i] = False
			#self.FirstBlackTokenInStartExpression[i] = ""
			self.EndExpression[i] = Event['EndExpression']
			self.EndExpressionFormattedForEval[i] = Event['EndExpression']
			self.EndExpressionTokensAreInWhiteList[i] = False
			#self.FirstBlackTokenInEndExpression[i] = ""
			self.SearchExpState[i] = False
			self.EventActive[i] = False
			self.EventActivePrev[i] = False
			self.SearchExpStartTime[i] = 0.0
			self.SearchExpEndTime[i] = 0.0
			self.TimeFromExpressionStart[i] = 0.0

			#tokenize the start expression
			self.StartExpressionTokensAreInWhiteList[i] = True
			self.TokensInStartExpression[i] = TreebankWordTokenizer().tokenize(self.StartExpression[i])
			for Token in self.TokensInStartExpression[i]:
				if not(self.ExpressionTokenWhiteListChecker.IsTokenInWhiteList(Token)):
					self.StartExpressionTokensAreInWhiteList[i] = False
					self.FirstBlackTokenInStartExpression[i] = Token
			for signal in self.Sig_list:
				self.StartExpressionFormattedForEval[i] = re.sub(r'\b' + signal + r"\b", 'dataPoints[' + str(self.Sig_list.index(signal)) + ']', self.StartExpressionFormattedForEval[i])

			#now check for Prev__ indicating a desire to reference previous loop values
			PrevRecList = re.findall(r'\b' +'Prev__'+r'\w+', self.StartExpressionFormattedForEval[i])
			for PrevRecSig in PrevRecList:
				self.StartExpressionFormattedForEval[i] = re.sub(PrevRecSig, 'dataPointsPrev[' + str(self.Sig_list.index(PrevRecSig[6-len(PrevRecSig):])) + ']', self.StartExpressionFormattedForEval[i], count=1)

			#now tokenize the end expression
			self.TokensInEndExpression[i] = TreebankWordTokenizer().tokenize(self.EndExpression[i])
			self.EndExpressionTokensAreInWhiteList[i] = True
			for Token in self.TokensInEndExpression[i]:
				if not(self.ExpressionTokenWhiteListChecker.IsTokenInWhiteList(Token)):
					self.EndExpressionTokensAreInWhiteList[i] = False
					self.FirstBlackTokenInEndExpression[i] = Token
			for signal in self.Sig_list:
				self.EndExpressionFormattedForEval[i] = re.sub(r'\b' + signal + r"\b", 'dataPoints[' + str(self.Sig_list.index(signal)) + ']', self.EndExpressionFormattedForEval[i])
			#now check for Prev__ indicating a desire to reference previous loop values
			PrevRecList = re.findall(r'\b' +'Prev__'+r'\w+', self.EndExpressionFormattedForEval[i])
			for PrevRecSig in PrevRecList:
				self.EndExpressionFormattedForEval[i] = re.sub(PrevRecSig, 'dataPointsPrev['+  str(self.Sig_list.index(PrevRecSig[6-len(PrevRecSig):])) + ']', self.EndExpressionFormattedForEval[i], count=1)
			self.EndExpressionFormattedForEval[i] = re.sub('TimeFromExpStart', 'Events.TimeFromExpressionStart[i]', self.EndExpressionFormattedForEval[i])

	def initializeEventParmsForNewDataFile(self):
		for i, Event in enumerate(self.EventDefs):
			self.SearchExpState[i] = False
			self.EventActive[i] = False
			self.EventActivePrev[i] = False
			self.SearchExpStartTime[i] = 0.0
			self.SearchExpEndTime[i] = 0.0
			self.TimeFromExpressionStart[i] = 0.0

