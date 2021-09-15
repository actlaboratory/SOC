from logging import getLogger
import globalVars
import uuid

class converterBase():
	_SUPPORTED_FORMATS = 0
	_CONVERTABLE_FORMATS = 0

	def __init__(self, item):
		self.log = getLogger("SOC.converter")
		self.log.info("initialized")
		self.item = item

	@classmethod
	def getSupportedFormats(cls):
		return cls._SUPPORTED_FORMATS

	@classmethod
	def getConvertableFormats(cls):
		return cls._CONVERTABLE_FORMATS

	def convert(self, target_format):
		raise NotImplementedError()

	def getTmpFilePath(self, ext):
		basePath = os.path.join(globalVars.app.getTmpDir(), str(uuid.uuid4()))
		return basePath+ext


