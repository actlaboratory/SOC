from logging import getLogger
import globalVars
import uuid
import os

class converterBase():
	_SUPPORTED_FORMATS = 0
	_CONVERTABLE_FORMATS = 0

	def __init__(self):
		if not os.path.exists(os.path.join(globalVars.app.getTmpDir(), "convertFiles")):
			os.mkdir(os.path.join(globalVars.app.getTmpDir(), "convertFiles"))
		self.log = getLogger("SOC.converter")

	@classmethod
	def getSupportedFormats(cls):
		return cls._SUPPORTED_FORMATS

	@classmethod
	def getConvertableFormats(cls):
		return cls._CONVERTABLE_FORMATS

	def convert(self, item, target_format):
		raise NotImplementedError()

	def getTmpFilePath(self, ext):
		basePath = os.path.join(globalVars.app.getTmpDir(), "convertFiles", str(uuid.uuid4()))
		return basePath+ext


