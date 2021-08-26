from . import pillow
from .pdf2image import pdf2image
import constants
from jobObjects import item

converter_list = [pillow.pillow, pdf2image]

def convert(job, engine_supported_formats):
	if job.getFormat() & engine_supported_formats:
		job.appendItem(item(job.getFileName()))
		return
	for converter in converter_list:
		if not (converter.getSupportedFormats() & job.getFormat()):
			continue
		for format in constants.IMAGE_FORMAT_LIST:
			if (converter.getConvertableFormats() & format) & (engine_supported_formats & format):
				c = converter()
				c.convert(job, format)
				return
	#ここに対応してない場合のエラー処理



