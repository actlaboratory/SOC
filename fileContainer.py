import errorCodes
import constants
import os

class container:
	def __init__(self, fileName):
		self.text = ""
		self.error = False
		self.success = False
		self.fileName = fileName

	def getFormat(self):
		ext = os.path.splitext(self.fileName)[1][1:]
		return constants.EXT_TO_FORMAT.get(ext.lower(), None)

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
