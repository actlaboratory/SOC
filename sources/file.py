from .base import sourceBase, sourceAskEvent
import jobObjects
import errorCodes
from .constants import sourceStatus
import time

class fileSource(sourceBase):
	def __init__(self, fileList):
		super().__init__("fileSource")
		self.fileList = fileList
		self.log.info("%d files was stored" % len(fileList))

	def _run(self):
		for file in self.fileList:
			job = jobObjects.job(file, False)
			self.onJobCreated(job)
			item = jobObjects.item(file)
			job.addCreatedItem(item)
			job.endSource()
			self.ask(testAskEvent)
		return

class testAskEvent(sourceAskEvent):
	_TEST_OK = 1
	_message = "ファイルを追加しました。"
	_selection_to_result = {
		"ok": _TEST_OK
	}

