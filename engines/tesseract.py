from .base import engineBase
import errorCodes
import constants
import pyocr
from PIL import Image

class tesseractEngine(engineBase):
	def __init__(self, mode):
		super().__init__("tesseract")
		self.mode = mode
		tools = pyocr.get_available_tools()
		self.tesseract = tools[0]
		self._statusString = _("大気中")

	def getSupportedFormats(self):
		return constants.FORMAT_JPEG | constants.FORMAT_PNG | constants.FORMAT_BMP

	def _recognize(self, item):
		self._statusString = _("認識開始")
		text = self.tesseract.image_to_string(
			Image.open(item.fileName),
			lang = self.mode,
			builder = pyocr.builders.TextBuilder()
		)
		item.setSuccess(text)
		self._statusString = _("大気中")

	def getStatusString(self):
		return self._statusString
