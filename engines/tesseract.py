# tesseract OCR engine

import pyocr

import constants
import globalVars
import views.engines.tesseractSettingsDialog

from .base import engineBase
from PIL import Image

class tesseractEngine(engineBase):
	def __init__(self, ):
		super().__init__("tesseract")

	def _init(self):
		tools = pyocr.get_available_tools()
		self.tesseract = tools[0]

	def getSupportedFormats(self):
		return constants.FORMAT_JPEG | constants.FORMAT_PNG | constants.FORMAT_BMP

	def _recognize(self, item):
		lang = globalVars.app.config.getstring("tesseract", "mode", "jpn", self.tesseract.get_available_languages())
		self.log.info("lang=%s" % lang)
		text = self.tesseract.image_to_string(
			Image.open(item.getPath()),
			lang = lang,
			builder = pyocr.builders.TextBuilder()
		)
		item.setText(text)

	@classmethod
	def getName(cls):
		return _("tesseract (ローカル)")

	@classmethod
	def getSettingDialog(cls):
		return views.engines.tesseractSettingsDialog.Dialog
