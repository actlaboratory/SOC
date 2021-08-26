from pdf2image import convert_from_path
from .base import converterBase
from jobObjects import item
import constants

class pdf2image(converterBase):
	_SUPPORTED_FORMATS = constants.FORMAT_PDF_ALL
	_CONVERTABLE_FORMATS = constants.FORMAT_BMP | constants.FORMAT_PNG | constants.FORMAT_GIF | constants.FORMAT_JPEG

	def convert(self, job, target_format):
		images = convert_from_path(job.getFileName,dpi=400)
		for image in images:
			if target_format == constants.FORMAT_BMP:
				path = self.getTmpFilePath(".bmp")
			elif target_format == constants.FORMAT_PNG:
				path = self.getTmpFilePath(".png")
			elif target_format == constants.FORMAT_GIF:
				path = self.getTmpFilePath(".gif")
			elif target_format == constants.FORMAT_JPEG:
				if image.mode != "RGB":
					image = image.convert("RGB")
				path = self.getTmpFilePath(".jpg")
			image.save(path)
			job.appendItem(item(path))
		self.log.info("pdf converted")

