# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Copyright (C) 2020 guredora <contact@guredora.com>

import logging
import os
import sys
import wx
import re
import ctypes
import pywintypes
import pathlib
import time
import win32com.client
import clipboard
import threading
import webbrowser
import constants
import errorCodes
import pdfUtil
import globalVars
import menuItemsStore
import keymap
from logging import getLogger
from .base import *
from simpleDialog import *
import Ocr
import views.convert
import views.converted
from views import authorizing
class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		self.OcrManager = Ocr.OcrManager()
		super().Initialize(
			title,
			640,
			500,
			self.app.config.getint(self.identifier,"positionX"),
			self.app.config.getint(self.identifier,"positionY"),
			style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.BORDER_STATIC
		)

		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(),wx.HORIZONTAL)
		vCreator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,creator.GetSizer(),wx.VERTICAL)
		self.filebox, self.list = vCreator.listbox(_("ファイル一覧"), (), None,-1,0,(450,200))
		fileListKeymap = keymap.KeymapHandler(defaultKeymap.defaultKeymap)
		acceleratorTable = fileListKeymap.GetTable("fileList")
		self.filebox.SetAcceleratorTable(acceleratorTable)
		self.filebox.SetDropTarget(DropTarget(self))	#D&Dの受け入れ

		vCreator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,creator.GetSizer(),wx.VERTICAL,20)
		self.open = vCreator.button(_("追加"), self.events.open)
		self.delete = vCreator.button(_("削除"), self.events.delete)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(),views.ViewCreator.FlexGridSizer,10, 2)
		self.engine, self.engineStatic = creator.combobox(_("OCRエンジン"), (_("google (インターネット)"), _("tesseract (ローカル)")), self.events.engine)
		self.tesseract, self.tesseractStatic = creator.combobox(_("モード"), (_("横書き通常"), _("横書き低負荷版"), _("縦書き通常"), _("縦書き低負荷版")), self.events.tesseract_mode)
		self.tesseract.Disable()

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(),wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.convert = creator.button(_("変換"), self.events.convert)
		self.exit = creator.button(_("終了"), self.events.Exit)

# D&D受入関連
class DropTarget(wx.DropTarget):
	def __init__(self,parent):
		super().__init__(wx.FileDataObject())
		self.parent=parent			#mainViewオブジェクトが入る

	#マウスオーバー時に呼ばれる
	#まだマウスを放していない
	def OnDragOver(self,x,y,defResult):
		return defResult

	#ドロップされずにマウスが外に出た
	#戻り値不要
	def OnLeave(self):
		pass

	#マウスが放されたら呼ばれる
	#現在データの受け入れが可能ならTrue
	def OnDrop(self,x,y):
		return True

	#データを受け入れ、結果を返す
	def OnData(self,x,y,defResult):
		self.GetData()
		globalVars.app.addFileList(self.DataObject.GetFilenames())
		return defResult		#推奨されたとおりに返しておく


class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""
		#メニューの大項目を作る
		self.hFileMenu = wx.Menu()
		self.hToolMenu=wx.Menu()
		self.hHelpMenu = wx.Menu()
		#ファイルメニューの中身
		self.open = self.RegisterMenuCommand(self.hFileMenu, "OPEN", _("変換ファイルの追加(&o)"))#ファイルリストの追加
		self.exit = self.RegisterMenuCommand(self.hFileMenu, "EXIT", _("終了(&x)"))#プログラムの終了
		#ツールメニューの中身
		self.google=self.RegisterMenuCommand(self.hToolMenu,"GOOGLE",_("Googleと連携する(&g)"))#グーグルの認証開始
		self.sendRegist = self.RegisterMenuCommand(self.hToolMenu,"SENDREGIST",_("送るメニューにショートカットを作成(&s)"))
		#ヘルプメニューの中身
		self.Page = self.RegisterMenuCommand(self.hHelpMenu, "webpage", _("actlaboratoryホームページを開く(&p)"))
		self.About = self.RegisterMenuCommand(self.hHelpMenu, "ABOUT", _("このソフトについて"))
		self.Update = self.RegisterMenuCommand(self.hHelpMenu, "UPDATE", _("最新バージョンを確認"))
		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu, _("ファイル(&f)"))
		self.hMenuBar.Append(self.hToolMenu,_("ツール(&t)"))
		self.hMenuBar.Append(self.hHelpMenu, _("ヘルプ(&h)"))
		target.SetMenuBar(self.hMenuBar)
		if globalVars.app.credentialManager.isOK():
			self.hMenuBar.Enable(menuItemsStore.getRef("GOOGLE"), False)

class Events(BaseEvents):
	def delete(self, events=None):
		index = self.parent.filebox.GetSelection()
		if index == -1:
			return
		self.parent.filebox.Delete(index)
		del self.parent.OcrManager.OcrList[index]
		self.parent.filebox.SetSelection(index-1)
		return
	def open(self, events=None):
		dialog = wx.FileDialog(None, _("画像ファイルを選択"), style=wx.FD_OPEN|wx.FD_MULTIPLE, wildcard=_("画像ファイル(*.jpg;*.png;*.gif;*.pdf) | *.jpg;*.png;*.gif;*.pdf; | すべてのファイル(*.*) | *.*"))
		if dialog.ShowModal() == wx.ID_CANCEL:
			return
		self.parent.app.addFileList(dialog.GetPaths())
		return
	def engine(self, events):
		index = self.parent.engine.GetSelection()
		self.parent.OcrManager.Engine = index
		if index == 0:
			self.parent.tesseract.Disable()
		if index == 1:
			self.parent.tesseract.Enable()
		return
	def tesseract_mode(self, event):
		self.parent.OcrManager.mode = self.parent.tesseract.GetSelection()
	def convert(self, Events):
		if self.parent.filebox.GetCount() == 0:
			errorDialog(_("変換をおこなうには最低ひとつの画像ファイルが追加されている必用があります。"))
			return
		if self.parent.engine.GetSelection() == -1:
			errorDialog(_("OCRエンジンを選択してください。"))
			return
		if self.parent.engine.GetSelection() == 1 and self.parent.tesseract.GetSelection() == -1:
			errorDialog(_("tesseract-ocrのモードが指定されていません。"))
			return
		if qDialog(_("変換を開始します。よろしいですか？"), _("確認")) == wx.ID_NO:
			return
		convertDialog = views.convert.ConvertDialog()
		convertDialog.Initialize()
		contain_text = False
		result = []
		for file in self.parent.OcrManager.OcrList:
			if self.parent.OcrManager.Engine == 0 and pdfUtil.pdfTextChecker(str(file)):
				contain_text = True
		if contain_text:
			if qDialog("pdfからテキストが検出されました。画像に変換して送信しますか？") == wx.ID_YES:
				self.parent.OcrManager.pdf_to_png = True
		ocrThread = threading.Thread(target=self.parent.OcrManager.lapped_ocr_exe, args=(convertDialog, result))
		ocrThread.start()
		convertDialog.Show(True)
		if errorCodes.CANCELED in result:
			dialog(_("キャンセルされました。"), _("結果"))
			return
		if errorCodes.FILE_NOT_FOUND in result:
			errorDialog(_("画像ファイルが存在しなかったためキャンセルされました。"))
			return
		if errorCodes.NOT_SUPPORTED in result:
			errorDialog(_("この機能は対応していません"))
			return
		if errorCodes.NOT_AUTHORIZED in result:
			errorDialog(_("この機能を使用するには事前にグーグルと連携しておく必用があります。ツールメニューより連携を行ってください。"))
			return
		if errorCodes.NET_ERROR in result:
			errorDialog(_("通信中にエラーが発生しました。ネット接続を確認するか時間をおいてから再度お試しください。"))
			return
		if errorCodes.GOOGLE_ERROR in result:
			errorDialog(_("エラーが発生しました。ファイルが画像ファイルか、ファイルが破損していないかなどを確認してください。"))
			return
		if errorCodes.UNKNOWN in result:
			errorDialog(_("何らかの理由により変換に失敗しました。errorlog.txtをご確認ください。"))
		if errorCodes.FILE_NOT_SUPPORTED in result:
			errorDialog(_("このエンジンではこのファイル形式は対応していません。"))
			return
		if errorCodes.OK in result:
			converted = views.converted.Dialog()
			converted.result = self.parent.OcrManager.SavedText
			if self.parent.OcrManager.Engine == 1:
				converted.tesseract_flag = True
				converted.list = self.parent.OcrManager.saved
			converted.Initialize()
			converted.Show()
			converted.Destroy()
			self.parent.OcrManager.SavedText = ""
			self.parent.filebox.Clear()
			self.parent.OcrManager.OcrList.clear()
		return
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る

		if selected == menuItemsStore.getRef("OPEN"):
			self.open()
		if selected == menuItemsStore.getRef("EXIT"):
			self.Exit()
		if selected == menuItemsStore.getRef("DELETE"):
			self.delete()
		if selected == menuItemsStore.getRef("PAST"):
			c=clipboard.ClipboardFile()
			pathList = c.GetFileList()
			self.parent.app.addFileList(pathList)
			return
		if selected==menuItemsStore.getRef("GOOGLE"):
			#確認ダイアログ表示
			result = qDialog(_("ブラウザを開き、認証を開始します。よろしいですか？"),_("確認"))
			if result == wx.ID_NO:
				return

			#認証プロセスの開始、認証用URL取得
			url=self.parent.app.credentialManager.MakeFlow()

			authorizeDialog = authorizing.authorizeDialog()
			authorizeDialog.Initialize()
			authorizeDialog.Show(False)
			#ブラウザの表示
			self.parent.app.say(_("ブラウザを開いています..."))

			#webView=views.web.Dialog(url,"http://localhost")
			#webView.Initialize()
			#webView.Show()
			web=wx.Process.Open("\"C:\\Program Files\\Internet Explorer\\iexplore.exe\" "+url)

			pid=web.GetPid()

			#ユーザの認証待ち
			status=errorCodes.WAITING_USER
			evt=threading.Event()
			while(status==errorCodes.WAITING_USER):
				if not wx.Process.Exists(pid):
					status=errorCodes.CANCELED
				if authorizeDialog.cancel:
					status = errorCodes.CANCELED_BY_USER
				if status==errorCodes.WAITING_USER:
					status=self.parent.app.credentialManager.getCredential()
				wx.YieldIfNeeded()
				evt.wait(0.3)
			authorizeDialog.Destroy()
			if status==errorCodes.OK:
				if web.Exists(pid):
					wx.Process.Kill(pid,wx.SIGTERM)		#修了要請
				dialog(_("認証が完了しました"),_("認証結果"))
				self.parent.menu.hMenuBar.Enable(menuItemsStore.getRef("GOOGLE"), False)
			if status == errorCodes.CANCELED_BY_USER:
				if web.Exists(pid):
					wx.Process.Kill(pid,wx.SIGTERM)		#修了要請
				dialog(_("キャンセルしました。"))
			elif status==errorCodes.IO_ERROR:
				dialog(_("認証に成功しましたが、ファイルの保存に失敗しました。ディレクトリのアクセス権限などを確認してください。"),_("認証結果"))
			elif status==errorCodes.CANCELED:
				dialog(_("ブラウザが閉じられたため、認証をキャンセルしました。"),_("認証結果"))
			elif status==errorCodes.NOT_AUTHORIZED:
				dialog(_("認証が拒否されました。"),_("認証結果"))
			else:
				dialog(_("不明なエラーが発生しました。"),_("エラー"))
			return
		if selected == menuItemsStore.getRef("webpage"):
			webbrowser.open("https://actlab.org")
			return
		if selected == menuItemsStore.getRef("SENDREGIST"):
			shortCut = os.environ["APPDATA"]+"\\Microsoft\\Windows\\SendTo\\"+_("SOCで文字認識を開始.lnk")
			ws = win32com.client.Dispatch("wscript.shell")
			scut=ws.CreateShortcut(shortCut)
			scut.TargetPath=sys.argv[0]
			scut.Save()
			dialog(_("送るメニューの登録が完了しました。送るメニューから「SOCで文字認識を開始」で実行できます。"), _("完了"))
		if selected == menuItemsStore.getRef("ABOUT"):
			dialog(_("SimpleOcrController（%s） version %s.\nCopyright (C) %s %s.\nこのソフトは公開されているOCRエンジンを使いやすくした物です。" % (constants.APP_NAME, constants.APP_VERSION, constants.APP_COPYRIGHT_YEAR, constants.APP_DEVELOPERS)), _("このソフトについて"))
		if selected == menuItemsStore.getRef("UPDATE"):
			code = self.parent.app.update.check(constants.APP_NAME, constants.APP_VERSION, constants.UPDATE_URL)
			if code == errorCodes.NET_ERROR:
				errorDialog(_("サーバーとの通信中にエラーが発生しました。"))
				return
			if code == errorCodes.UPDATER_LATEST:
				dialog(_("現在お使いのバージョンは最新です。アップデートの必要はありません。"), _("アップデート"))
				return
			if code == errorCodes.UPDATER_NEED_UPDATE:
				result = qDialog(_("バージョン%sにアップデートすることができます。%sアップデートを開始しますか？" % (self.parent.app.update.version, self.parent.app.update.description)), _("アップデート"))
				if result == wx.ID_NO:
					return
				self.parent.app.update.run("")
			if code == errorCodes.UPDATER_VISIT_SITE:
				URL = self.parent.app.update.URL
				if qDialog(_("緊急のお知らせがあります。\nタイトル:%s\n詳細をブラウザーで開きますか？"% (self.parent.app.update.description))) == wx.ID_NO:
					return
				webbrowser.open(URL)
			if code == errorCodes.UPDATER_FAILED_PARAM:
				dialog(_("リクエストパラメーターが不正です。開発者にお問い合わせください。"), _("アップデート"))
				return





