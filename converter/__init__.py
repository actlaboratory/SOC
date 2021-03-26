from . import pillow
import constants

converter_list = [pillow.pillow]

def convert(item, engine_supported_formats):
	if item.getFormat() & engine_supported_formats != 0:
		return
	for converter in converter_list:
		if converter.getSupportedFormats() & item.getFormat() != item.getFormat():
			continue
		for format in constants.IMAGE_FORMAT_LIST:
			if converter.getConvertableFormats() & format == format & engine_supported_formats & format == format:
				c = converter()
				c.convert(item, format)
				return
	#ここに対応してない場合のエラー処理



