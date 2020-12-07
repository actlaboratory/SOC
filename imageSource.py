import errorCodes
class sourceBase:
	def get(self):
		raise NotImplementedError()

class fileSource(sourceBase):
	def __init__(self, fileList):
		super().__init__()
		self.fileList = fileList
		self.index = -1

	def get(self):
		self.index += 1
		if self.index + 1 < len(self.fileList):
			return errorCodes.SOURCE_ALL_LOADED
		return self.fileList[self.index]

