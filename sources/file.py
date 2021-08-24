from .base import sourceBase
from jobObjects import job
import errorCodes

class fileSource(sourceBase):
	def __init__(self, fileList):
		super().__init__("fileSource")
		self.fileList = fileList
		self.log.info("%d files was stored" % len(flieList))


	def _internal_get_item(self):
		if len(self.fileList) == 0:
			return
		fileName = self.fileList[0]
		del self.fileList[0]
		return job(fileName, temporally=False)

