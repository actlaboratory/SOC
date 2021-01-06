import errorCodes
import globalVars
import time
import os
import shutil
import dtwain

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
	def initialize(self):
		return

	def get(self):
		raise NotImplementedError()

	def isEmpty(self):
		raise NotImplementedError()

	def close(self):
		"""ソースを閉じるときの処理"""
		return None#必要な場合はオーバーライドする。

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

class scannerSource(sourceBase):
	def __init__(self, scannerName, resolution = 300, blankPageDetect = False):
		self.scannerName = scannerName
		self.resolution = resolution
		self.blankPageDetect = blankPageDetect
		#self.dtwain_source.raiseDeviceOffline()
		self.image_tmp = os.path.join(globalVars.app.tmpdir, "acquiredImage")
		if os.path.exists(self.image_tmp):
			shutil.rmtree(self.image_tmp)
		os.mkdir(self.image_tmp)
		self.fileName = os.path.join(self.image_tmp, "test.png")

	def initialize(self):
		self.dtwain = dtwain.dtwain()
		self.dtwain_source = self.dtwain.getSourceByName(self.scannerName)
		self.dtwain_source.setResolution(self.resolution)
		if self.blankPageDetect:
			self.dtwain_source.setBlankPageDetection(99.5)

	def get(self):
		if self.dtwain_source.isFeederLoaded():
			self.dtwain_source.acquireFile(self.fileName, dtwain.DTWAIN_PNG)
			return container(self.fileName)
		return None

	def isEmpty(self):
		if self.dtwain_source.isFeederLoaded():
			return False
		else:
			return True

	def close(self):
		self.dtwain_source.close()
