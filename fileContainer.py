import errorCodes

class container:
	def __init__(self, fileName):
		self.text = ""
		self.error = False
		self.success = False
		self.fileName = fileName


	def getErrorString(self):
		if not self.error:
			return ""
		return self.errorMessage

	def setSuccess(self, text):
		self.text = text
		self.success = True

	def getText(self):
		return self.text

	def setError(self, message):
		self.error = True
		self.errorMessage = message
		self.done = True
