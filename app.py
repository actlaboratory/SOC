# -*- coding: utf-8 -*-
# Soc Main

import tempfile
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
import views.new

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		"""アプリを初期化する。"""
		self.tmpDir = tempfile.TemporaryDirectory()
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
		#popplerにパスを通す
		os.environ["PATH"] += os.pathsep + os.getcwd() + "/poppler/bin"
		# メインビューを表示
		from views import main
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		dialog = views.new.Dialog()
		dialog.Initialize(sys.argv[1:])
		dialog.Show()
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

	def getTmpDir(self):
		return self.tmpDir.name

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		# managerを止める
		globalVars.manager = None
		#一時ディレクトリを削除する
		self.tmpDir.cleanup()
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

