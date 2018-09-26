class CheckEvalExpression:
	def __init__(self, Signal_list):
		self.tokenInWhiteList = False
		self.Signal_list = Signal_list
		self.ListOfKeywords = { \
			'and', \
			'or',  \
			'not', \
			'(',   \
			')',   \
			'==',  \
			'!=',  \
			'<>',  \
			'>',   \
			'>=',  \
			'<',   \
			'<=',  \
			',',   \
			'.',   \
			':',   \
			'+',   \
			'-',   \
			'*',   \
			'/',   \
			'**',  \
			'%',   \
			'&',   \
			'|',   \
			'TimeFromExpStart'}

	def IsTokenInWhiteList(self, token):
		self.tokenInWhiteList = False
		#Check to see if token is a number
		if self.IsTokenANumber(token) == True:
			self.tokenInWhiteList = True
			return self.tokenInWhiteList
		else:
			for Keyword in self.ListOfKeywords:
				if token == Keyword:
					self.tokenInWhiteList = True
			for sig in self.Signal_list:
				if (token == sig) or (token == 'Prev__' + sig):
					self.tokenInWhiteList = True
			return self.tokenInWhiteList

	def IsTokenANumber(self, token):
		try:
			complex(token) # for int, long, float and complex
		except ValueError:
			return False
		return True
