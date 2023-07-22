from pdf2image import convert_from_path
from .base import converterBase
from jobObjects import item
import constants
import os
import globalVars
import util

class pdf2image(converterBase):
	_SUPPORTED_FORMATS = constants.FORMAT_PDF_ALL | constants.FORMAT_PDF_MULTI_PAGE
	_CONVERTABLE_FORMATS = constants.FORMAT_BMP | constants.FORMAT_PNG | constants.FORMAT_GIF | constants.FORMAT_JPEG

	def convert(self, target_format):
		itm_list = []
		images = convert_from_path(self.item.getPath(),fmt="png",thread_count=os.cpu_count()-1,output_folder=globalVars.app.getTmpDir(),dpi=400)
		for image in images:
			if target_format == constants.FORMAT_BMP:
				path = util.getTmpFilePath(".bmp")
			elif target_format == constants.FORMAT_PNG:
				path = util.getTmpFilePath(".png")
			elif target_format == constants.FORMAT_GIF:
				path = util.getTmpFilePath(".gif")
			elif target_format == constants.FORMAT_JPEG:
				if image.mode != "RGB":
					image = image.convert("RGB")
				path = util.getTmpFilePath(".jpg")
			image.save(path)
			itm_list.append(item(path))
			image.close()
		self.log.info("pdf converted")
		return itm_list

