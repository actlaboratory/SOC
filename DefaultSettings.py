# -*- coding: utf-8 -*-
#default config

from ConfigManager import *
import locale
import os

class DefaultSettings:
	def get():
		config = ConfigManager()
		loc = locale.getdefaultlocale()[0]
		if loc == "en_US":
			font = "Bold 'times new roman' 22 windows-1252"
		if loc == "ja_JP":
			font = "bold 'ＭＳ ゴシック' 22 windows-932"
		config["general"]={
			"language": "",
			"fileVersion": "100",
			"locale": loc,
			"update": True,
			"timeout": 3
		}

		config["view"]={
			"font": font,
			"colorMode":"white"
		}
		config["speech"]={
			"reader" : "AUTO"
		}

		config["mainView"]={

		}

		config["network"]={
			"auto_proxy": True
		}

		config["ocr"] = {
			"tmpdir": os.path.join(os.environ["TEMP"], "soc"),
			"saveSourceDir": True,
			"savedir": os.path.join(os.environ["userprofile"], "Documents")
		}
		return config

initialValues={}
"""
	この辞書には、ユーザによるキーの削除が許されるが、初回起動時に組み込んでおきたい設定のデフォルト値を設定する。
	ここでの設定はユーザの環境に設定ファイルがなかった場合のみ適用され、初期値として保存される。
"""
