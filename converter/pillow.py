from .base import converterBase
from jobObjects import item
from PIL import Image, ImageSequence
import constants
import util

class pillow(converterBase):
	_SUPPORTED_FORMATS = constants.FORMAT_BMP | constants.FORMAT_PNG | constants.FORMAT_GIF | constants.FORMAT_JPEG | constants.FORMAT_TIFF
	_CONVERTABLE_FORMATS = constants.FORMAT_BMP | constants.FORMAT_PNG | constants.FORMAT_GIF | constants.FORMAT_JPEG

	def convert(self, target_format):
		self.log.info("running converter...")
		item_list = []
		for img in ImageSequence.Iterator(Image.open(self.item.getPath())):
			if target_format == constants.FORMAT_BMP:
				path = util.getTmpFilePath(".bmp")
			elif target_format == constants.FORMAT_PNG:
				path = util.getTmpFilePath(".png")
			elif target_format == constants.FORMAT_GIF:
				path = util.getTmpFilePath(".gif")
			elif target_format == constants.FORMAT_JPEG:
				if img.mode != "RGB":
					img = img.convert("RGB")
				path = util.getTmpFilePath(".jpg")
			img.save(path)
			item_list.append(item(path))
		self.log.info("convert done!")
		return item_list

def convertGrayScale(convert_item: item):
	if not convert_item.getFormat() & pillow.getSupportedFormats():
		return
	img = Image.open(convert_item.getPath()).convert("L")
	target_format = convert_item.getFormat()
	if target_format == constants.FORMAT_BMP:
		path = util.getTmpFilePath(".bmp")
	elif target_format == constants.FORMAT_PNG:
		path = util.getTmpFilePath(".png")
	elif target_format == constants.FORMAT_GIF:
		path = util.getTmpFilePath(".gif")
	elif target_format == constants.FORMAT_JPEG:
		path = util.getTmpFilePath(".jpg")
	img.save(path)
	convert_item.setGrayScaleFile(path)
	return True
