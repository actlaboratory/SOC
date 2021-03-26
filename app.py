# -*- coding: utf-8 -*-
# Soc Main

import proxyUtil
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
from sources.file import fileSource

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		"""アプリを初期化する。"""
		# プロキシの設定を適用
		if self.config.getboolean("network", "auto_proxy"):
			self.proxyEnviron = proxyUtil.virtualProxyEnviron()
			self.proxyEnviron.set_environ()
		else:
			self.proxyEnviron = None
		# googleのCredentialを準備
		self.credentialManager=CredentialManager.CredentialManager()
		self.setGlobalVars()
		# update関係を準備
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		self.SetDefaultEncoding()
		if not os.path.exists(self.getTmpDir()):
			os.mkdir(self.getTmpDir())
		#popplerにパスを通す
		os.environ["PATH"] += os.pathsep + os.getcwd() + "/poppler/bin"
		# メインビューを表示
		self.hMainView=main.MainView()
		self.fileList = []
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
			suffix = os.path.splitext(file)[1][1:].lower()
			if os.path.isdir(file):
				error=True
				continue
			if suffix in constants.EXT_TO_FORMAT.keys():
				if file in fileSource.fileList:
					continue
				fileSource.fileList.append(file)
				self.hMainView.filebox.Append(os.path.basename(file))
				add = True
			else:
				error = True
		if error:
			if add:
				errorDialog(_("対応していないフォーマットのファイルは除外され、一部のファイルのみ追加されました。"))
			else:
				errorDialog(_("このフォーマットのファイルには対応していないため、追加できませんでした。"))

	def getTmpDir(self):
		return self.config.getstring("ocr", "tmpdir", os.path.join(os.environ["TEMP"], "soc"), None)

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。
		if os.path.exists(self.getTmpDir()):
			util.allDelete(self.getTmpDir())

		# プロキシの設定を元に戻す
		if self.proxyEnviron != None: self.proxyEnviron.unset_environ()
		
		#戻り値は無視される
		return 0
