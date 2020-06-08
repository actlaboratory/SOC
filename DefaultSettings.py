# -*- coding: utf-8 -*-
#default config

from ConfigManager import *
import locale

class DefaultSettings:
	def get():
		config = ConfigManager()
		loc = locale.getdefaultlocale()[0].replace("_", "-")
		config["general"]={
			"language": "",
			"fileVersion": "100",
			"locale": loc,
			"update": True
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
