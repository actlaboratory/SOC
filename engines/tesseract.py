from .base import engineBase
import errorCodes
import constants
import pyocr
from PIL import Image

class tesseractEngine(engineBase):
	def __init__(self, mode):
		super().__init__("tesseract")
		self.mode = mode

	def _init(self):
		tools = pyocr.get_available_tools()
		self.tesseract = tools[0]

	def getSupportedFormats(self):
		return constants.FORMAT_JPEG | constants.FORMAT_PNG | constants.FORMAT_BMP

	def _recognize(self, item):
		text = self.tesseract.image_to_string(
			Image.open(item.getPath()),
			lang = self.mode,
			builder = pyocr.builders.TextBuilder()
		)
		item.setText(text)
