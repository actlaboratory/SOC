from engines import base
import errorCodes
import pyocr
from PIL import Image
import queue

class tesseractEngine(base.engineBase):
	def __init__(self, mode):
		super().__init__()
		self.mode = mode
		tools = pyocr.get_available_tools()
		self.tesseract = tools[0]
		self._statusString = _("大気中")

	def getSupportedType(self):
		return (errorCodes.TYPE_JPG, errorCodes.TYPE_PNG, errorCodes.TYPE_GIF, errorCodes.TYPE_BMP)

	def recognition(self, container):
		if self.interrupt:
			container.setInterrupt()
			return
		self.processingContainer.append(container)
		self._statusString = _("認識開始")
		text = self.tesseract.image_to_string(
			Image.open(container.fileName),
			lang = self.mode,
			builder = pyocr.builders.TextBuilder()
		)
		container.setSuccess(text)
		self.processingContainer.remove(container)
		self._statusString = _("大気中")

	def getStatusString(self):
		return self._statusString
