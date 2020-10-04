# -*- coding: utf-8 -*-
# Soc Main

import AppBase
from views import main
import CredentialManager
import sys
import locale
import _locale
import update
import constants
import pathlib
import errorCodes
from simpleDialog import *
import util
import os
import globalVars

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		"""アプリを初期化する。"""
		# googleのCredentialを準備
		self.credentialManager=CredentialManager.CredentialManager()
		self.setGlobalVars()
		# update関係を準備
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		self.SetDefaultEncoding()
		self.tmpdir = self.config.getstring("ocr", "tmpdir", os.path.join(os.environ["TEMP"], "soc"), None)
		# メインビューを表示
		self.hMainView=main.MainView()
		self.addFileList(sys.argv[1:])
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		return True

	#windows標準のコードページではなくUTF-8を強制するHack
	def SetDefaultEncoding(self):
		country=_locale._getdefaultlocale()[0]
		_locale._getdefaultlocale = (lambda *args: ([country,'utf8']))

	def setGlobalVars(self):
		globalVars.update = update.update()
		return

	def addFileList(self, files):
		error = False
		add = False
		for file in files:
			path = pathlib.Path(file)
			suffix = path.suffix.lower()
			if path.is_dir():
				error=True
				continue
			if suffix in constants.AVAILABLE_FORMATS:
				if path in self.hMainView.OcrManager.OcrList:
					continue
				self.hMainView.OcrManager.OcrList.append(path)
				self.hMainView.filebox.Append(path.name)
				add = True
			else:
				error = True
		if error:
			if add:
				errorDialog(_("対応していないフォーマットのファイルは除外され、一部のファイルのみ追加されました。"))
			else:
				errorDialog(_("このフォーマットのファイルには対応していないため、追加できませんでした。"))

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。
		if os.path.exists(self.tmpdir):
			util.allDelete(self.tmpdir)

		#戻り値は無視される
		return 0
