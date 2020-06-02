# -*- coding: utf-8 -*-
#default config

from ConfigManager import *


class DefaultSettings:
	def get():
		config = ConfigManager()
		config["general"]={
			"language": "",
			"fileVersion": "100",
			"locale": "ja-JP"
		}
		config["view"]={
			"font": "bold 'ＭＳ ゴシック' 22 windows-932",
			"colorMode":1
		}
		config["speech"]={
			"reader" : "AUTO"
		}
		config["mainView"]={

		}
		config["ocr"] = {
			"pdf_pages":  20
		}
		return config
