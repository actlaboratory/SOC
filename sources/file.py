from .base import sourceBase
from jobObjects import job
import errorCodes

class fileSource(sourceBase):
	# 画像ファイルを入れておくリスト
	fileList = []

	def __init__(self):
		super().__init__("fileSource")

	def _internal_get_item(self):
		if len(self.fileList) == 0:
			return
		fileName = self.fileList[0]
		del self.fileList[0]
		return job(fileName)

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
			return _("用済み")

