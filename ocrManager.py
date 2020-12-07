import errorCodes

def type_to_constant(type):
	elif type.lower() == ".jpg":
		return errorCodes.TYPE_JPG
	elif type.lower() == ".png":
		return errorCodes.TYPE_PNG
	elif type.lower() == ".gif":
		return errorCodes.TYPE_GIF
	elif type.lower() == ".pdf":
		return errorCodes.TYPE_PDF_ALL
	elif type.lower() == ".bmp":
		return errorCodes.TYPE_BMP
	else:
		return errorCodes.TYPE_UNKNOWN

class statusContainer:
	def __init__(self):
		self.done = False
		self.canceled = False
		self.errorCode = errorCodes.OK
		self.status = errorCodes.STATUS_RUNNING
		self.text = ""

	isDone(self):
		return self.done

	def getStatus(self):
		return self.status

	def getError(self):
		return self.errorCode

	def isCanceled(self):
		return self.canceled

	def success(self, text):
		self.text = text
		self.done = True
		self.status = errorCodes.STATUS_SUCCESS

	def getText(self):
		return self.text

	def cancel(self):
		self.canceled = True
		self.status = errorCodes.STATUS_CANCELED
		self.errorCode = errorCodes.CANCELED
		self.done = True

	def error(self, code):
		self.status = errorCodes.STATUS_ERROR
		self.errorCode = code
		self.done = True

class manager:
	def __init__(self, 