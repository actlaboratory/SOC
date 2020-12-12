import errorCodes
class container:
	def __init__(self, fileName):
		self.done = False
		self.canceled = False
		self.errorCode = errorCodes.OK
		self.status = errorCodes.STATUS_RUNNING
		self.text = ""
		self.onDone = None
		self.fileName = fileName

	def setOnDoneCallBack(self, callBack):
		self.onDone = callBack

	def isDone(self):
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

class sourceBase:
	def get(self):
		raise NotImplementedError()

	def isEmpty(self):
		raise NotImplementedError()


class fileSource(sourceBase):
	def __init__(self, fileList):
		super().__init__()
		self.fileList = fileList

	def get(self):
		if len(self.fileList) == 0:
			return
		fileName = self.fileList[0]
		del self.fileList[0]
		return container(fileName)

	def isEmpty(self):
		if len(self.fileList) == 0:
			return True
		return False
