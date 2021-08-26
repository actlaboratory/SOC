from .base import converterBase
from jobObjects import item
from PIL import Image, ImageSequence
import constants

class pillow(converterBase):
	_SUPPORTED_FORMATS = constants.FORMAT_BMP | constants.FORMAT_PNG | constants.FORMAT_GIF | constants.FORMAT_JPEG | constants.FORMAT_TIFF
	_CONVERTABLE_FORMATS = constants.FORMAT_BMP | constants.FORMAT_PNG | constants.FORMAT_GIF | constants.FORMAT_JPEG

	def convert(self, job, target_format):
		self.log.info("running converter...")
		for img in ImageSequence.Iterator(Image.open(job.getFileName())):
			if target_format == constants.FORMAT_BMP:
				path = self.getTmpFilePath(".bmp")
			elif target_format == constants.FORMAT_PNG:
				path = self.getTmpFilePath(".png")
			elif target_format == constants.FORMAT_GIF:
				path = self.getTmpFilePath(".gif")
			elif target_format == constants.FORMAT_JPEG:
				if img.mode != "RGB":
					img = img.convert("RGB")
				path = self.getTmpFilePath(".jpg")
			img.save(path)
			job.appendItem(item(path))
		self.log.info("convert done!")
