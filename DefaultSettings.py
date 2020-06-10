# -*- coding: utf-8 -*-
#default config

from ConfigManager import *
import locale

class DefaultSettings:
	def get():
		config = ConfigManager()
		loc = locale.getdefaultlocale()[0].replace("_", "-")
		if loc == "en-US":
			font = "Bold 'times new roman' 22 windows-1252"
		if loc == "ja-JP":
			font = "bold 'ＭＳ ゴシック' 22 windows-932"
		config["general"]={
			"language": "",
			"fileVersion": "100",
			"locale": loc,
			"update": True
		}
		config["view"]={
			"font": font,
			"colorMode":1
		}
		config["speech"]={
			"reader" : "AUTO"
		}
		config["mainView"]={

		}
		return config
