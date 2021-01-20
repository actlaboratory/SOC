from sources import base
from fileContainer import container
import errorCodes

class fileSource(base.sourceBase):
	def __init__(self, fileList):
		super().__init__()
		self.fileList = fileList

	def get(self):
		if len(self.fileList) == 0:
			return
		fileName = self.fileList[0]
		del self.fileList[0]
		return container(fileName)

	def getStatus(self):
		status = 0
		if len(self.fileList) > 0:
			status |= errorCodes.STATUS_SOURCE_QUEUED
		else:
			status |= errorCodes.STATUS_SOURCE_EMPTY
		if self.error:
			status |= errorCodes.STATUS_SOURCE_ERROR
		return status


	def getStatusString(self):
		if len(self.fileList) > 0:
			return _("残りファイル数: %d") % (len(self.fileList))
		else:
			return _("ファイル無し")
