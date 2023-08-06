# PDF split Convertor

import constants
import popplerUtil
import util

from .base import converterBase
from jobObjects import item

class pdfSplit(converterBase):
	_SUPPORTED_FORMATS =  constants.FORMAT_PDF_MULTI_PAGE
	_CONVERTABLE_FORMATS = constants.FORMAT_PDF_ALL

	def convert(self, target_format):
		itm_list = []
		pages = 1
		info = popplerUtil.getInfo(self.item.getPath())
		if "Pages" in info: pages = int(info["Pages"])
		for i in range(1, pages + 1):
			path = util.getTmpFilePath(".pdf")
			popplerUtil.split(self.item.getPath(), path, i)
			itm_list.append(item(path))
		return itm_list
