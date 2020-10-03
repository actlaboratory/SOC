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
import pathlib
import util
import os

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
		# update関係を準備
		self.update = update.update()
		if self.config.getboolean("general", "update"):
			self.autoUpdate()
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

	def autoUpdate(self):
		code = self.update.check(constants.APP_NAME, constants.APP_VERSION, constants.UPDATE_URL)
		if code == errorCodes.NET_ERROR:
			dialog(_("サーバーとの通信に失敗しました。"), _("アップデート"))
			return
		if code == errorCodes.UPDATER_NEED_UPDATE:
			result = qDialog(_("バージョン%sにアップデートすることができます。%sアップデートを開始しますか？") % (self.update.version, self.update.description), _("アップデート"))
			if result == wx.ID_NO:
				return
			self.update.run("")
		if code == errorCodes.UPDATER_VISIT_SITE:
			URL = self.update.URL
			if qDialog(_("緊急のお知らせがあります。\nタイトル:%s\n詳細をブラウザーで開きますか？")% (self.update.description)) == wx.ID_NO:
				return
			webbrowser.open(URL)

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

		# プロキシの設定を元に戻す
		if self.proxyEnviron != None: self.proxyEnviron.unset_environ()
		
		#戻り値は無視される
		return 0
