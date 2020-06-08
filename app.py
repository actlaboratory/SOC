# -*- coding: utf-8 -*-
# Soc Main

import accessible_output2.outputs.auto
import sys
import ConfigManager
import gettext
import logging
import os
import wx
import _locale
import locale
import win32api
import pathlib
import datetime
from logging import getLogger, FileHandler, Formatter
from simpleDialog import *
import views.langDialog as langDialog
import constants
import DefaultSettings
import errorCodes
import CredentialManager
from views import main
import update
import webbrowser

class Main(wx.App):
	def initialize(self):
		"""アプリを初期化する。"""
		#実行環境の取得(exeファイルorインタプリタ)
		self.frozen=hasattr(sys,"frozen")
		self.InitLogger()
		self.LoadSettings()
		country=_locale._getdefaultlocale()[0]
		_locale._getdefaultlocale = (lambda *args: ([country,'utf8']))
		locale.setlocale(locale.LC_TIME,self.config["general"]["locale"])
		self.SetTimeZone()
		self.InitTranslation()
		for s in os.getcwd():
			if ord(s) >= 128:
				errorDialog(_("アプリケーションが全角文字の入ったディレクトリに置かれているため軌道することができません。"))
				return false

		# 音声読み上げの準備
		reader=self.config["speech"]["reader"]
		if(reader=="PCTK"):
			self.log.info("use reader 'PCTalker'")
			self.speech=accessible_output2.outputs.pc_talker.PCTalker()
		elif(reader=="NVDA"):
			self.log.info("use reader 'NVDA'")
			self.speech=accessible_output2.outputs.nvda.NVDA()
		#SAPI4はバグってるっぽいので無効にしておく
#		elif(reader=="SAPI4"):
#			self.log.info("use reader 'SAPI4'")
#			self.speech=accessible_output2.outputs.sapi4.Sapi4()
		elif(reader=="SAPI5"):
			self.log.info("use reader 'SAPI5'")
			self.speech=accessible_output2.outputs.sapi5.SAPI5()
		elif(reader=="AUTO"):
			self.log.info("use reader 'AUTO'")
			self.speech=accessible_output2.outputs.auto.Auto()
		else:
			self.config.set("speech","reader","AUTO")
			self.log.warning("Setting missed! speech.reader reset to 'AUTO'")
			self.speech=accessible_output2.outputs.auto.Auto()

		# googleのCredentialを準備
		self.credentialManager=CredentialManager.CredentialManager()
		# update関係を準備
		self.update = update.update()
		if self.config.getboolean("general", "update"):
			self.autoUpdate()
		# メインビューを表示
		self.hMainView=main.MainView()
		self.addFileList(sys.argv[1:])
		self.hMainView.Show()
		return True

	def InitLogger(self):
		"""ログ機能を初期化して準備する。"""
		self.hLogHandler=FileHandler(constants.APP_NAME+".log", mode="w", encoding="UTF-8")
		self.hLogHandler.setLevel(logging.DEBUG)
		self.hLogFormatter=Formatter("%(name)s - %(levelname)s - %(message)s (%(asctime)s)")
		self.hLogHandler.setFormatter(self.hLogFormatter)
		self.log=getLogger("Soc")
		self.log.setLevel(logging.DEBUG)
		self.log.addHandler(self.hLogHandler)
		r="executable" if self.frozen else "interpreter"
		self.log.info("Starting"+constants.APP_NAME+" as %s!" % r)

	def LoadSettings(self):
		"""設定ファイルを読み込む。なければデフォルト設定を適用し、設定ファイルを書く。"""
		self.config = DefaultSettings.DefaultSettings.get()
		self.config.read(constants.SETTING_FILE_NAME)
		self.config.write()

	def InitTranslation(self):
		"""翻訳を初期化する。"""
		lang=self.config.getstring("general","language","",constants.SUPPORTING_LANGUAGE)
		if lang == "":
			if locale.getdefaultlocale()[0] == "ja_JP":
				self.config["general"]["language"] = "ja-JP"
			elif locale.getdefaultlocale()[0] == "en_US":
				self.config["general"]["language"] = "en-US"
			else:
				# 言語選択を表示
				dialog("please select language.", "information")
				langSelect = langDialog.langDialog()
				langSelect.Initialize()
				langSelect.Show()
				self.config["general"]["language"] = langSelect.GetValue()
			lang = self.config["general"]["language"]
		self.translator=gettext.translation("messages","locale", languages=[lang], fallback=True)
		self.translator.install()

	def GetFrozenStatus(self):
		"""コンパイル済みのexeで実行されている場合はTrue、インタプリタで実行されている場合はFalseを帰す。"""
		return self.frozen

	def say(self,s):
		"""スクリーンリーダーでしゃべらせる。"""
		self.speech.speak(s)
	def OnExit(self):
		return wx.App.OnExit(self)

	def autoUpdate(self):
		code = self.update.check(constants.APP_NAME, constants.APP_VERSION, constants.UPDATE_URL)
		if code == errorCodes.NET_ERROR:
			dialog(_("サーバーとの通信に失敗しました。"), _("アップデート"))
			return
		if code == errorCodes.UPDATER_NEED_UPDATE:
			result = qDialog(_("バージョン%sにアップデートすることができます。%sアップデートを開始しますか？" % (self.update.version, self.update.description)), _("アップデート"))
			if result == wx.ID_NO:
				return
			self.update.run("")
		if code == errorCodes.UPDATER_VISIT_SITE:
			URL = self.update.URL
			if qDialog(_("緊急のお知らせがあります。\nタイトル:%s\n詳細をブラウザーで開きますか？"% (self.update.description))) == wx.ID_NO:
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

	def SetTimeZone(self):
		bias=win32api.GetTimeZoneInformation(True)[1][0]*-1
		hours=bias//60
		minutes=bias%60
		self.timezone=datetime.timezone(datetime.timedelta(hours=hours,minutes=minutes))
