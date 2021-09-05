# -*- coding: utf-8 -*-
# Soc Main

import proxyUtil
import AppBase
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
import threading
import ocrManager

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		"""アプリを初期化する。"""
		# プロキシの設定を適用
		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		self.setProxyEnviron()
		# googleのCredentialを準備
		self.credentialManager=CredentialManager.CredentialManager()
		self.setGlobalVars()
		self.installThreadExcepthook()
		# update関係を準備
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		self.SetDefaultEncoding()
		if not os.path.exists(self.getTmpDir()):
			os.mkdir(self.getTmpDir())
		#popplerにパスを通す
		os.environ["PATH"] += os.pathsep + os.getcwd() + "/poppler/bin"
		#managerの開始
		globalVars.manager.start()
		# メインビューを表示
		from views import main
		self.hMainView=main.MainView()
		self.fileList = []
		self.addFileList(sys.argv[1:])
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		return True

	def setProxyEnviron(self):
		if self.config.getboolean("proxy", "usemanualsetting", False) == True:
			self.proxyEnviron.set_environ(self.config["proxy"]["server"], self.config.getint("proxy", "port", 8080, 0, 65535))
		else:
			self.proxyEnviron.set_environ()

	#windows標準のコードページではなくUTF-8を強制するHack
	def SetDefaultEncoding(self):
		country=_locale._getdefaultlocale()[0]
		_locale._getdefaultlocale = (lambda *args: ([country,'utf8']))

	def setGlobalVars(self):
		globalVars.update = update.update()
		globalVars.manager = ocrManager.manager()
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
				if file in self.fileList:
					continue
				self.fileList.append(file)
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

		# アップデート
		globalVars.update.runUpdate()
		
		#戻り値は無視される
		return 0

	def installThreadExcepthook(self):
		_init = threading.Thread.__init__

		def init(self, *args, **kwargs):
			_init(self, *args, **kwargs)
			_run = self.run

			def run(*args, **kwargs):
				try:
					_run(*args, **kwargs)
				except:
					sys.excepthook(*sys.exc_info())
			self.run = run

		threading.Thread.__init__ = init

