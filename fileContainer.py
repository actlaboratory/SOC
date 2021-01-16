import errorCodes

class container:
	def __init__(self, fileName):
		self.done = False
		self.success = False
		self.interrupt = False
		self.error = False
		self.running = True
		self.text = ""
		self.onDone = None
		self.fileName = fileName

	def setOnDoneCallBack(self, callBack):
		self.onDone = callBack

	def isDone(self):
		return self.done

	def getStatus(self):
		status = 0
		if self.running:
			status |= errorCodes.STATUS_ENGINE_RUNNING
		if self.success:
			status |= errorCodes.STATUS_ENGINE_SUCCESS
		if self.interrupt:
			status |= errorCodes.STATUS_ENGINE_INTERRUPT
		if self.error:
			status |= errorCodes.STATUS_ENGINE_ERROR
		return status

	def getErrorString(self):
		if not self.error:
			return ""
		return self.errorMessage

	def isInterrupted(self):
		return self.interrupt

	def setSuccess(self, text):
		self.text = text
		self.done = True
		self.success = True

	def getText(self):
		return self.text

	def setInterrupt(self):
		self.interrupt = True
		self.running = False
		self.done = True

	def setError(self, message):
		self.error = True
		self.errorMessage = message
		self.done = True
