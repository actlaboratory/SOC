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
import ocrManager
from views import processingDialog
from views import authorizing
from views import settings
from views import versionDialog
from views import resultDialog
from sources import file,scanner
from engines import google, tesseract
import dtwain

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			660,
			700,
			self.app.config.getint(self.identifier,"positionX"),
			self.app.config.getint(self.identifier,"positionY"),
			style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.BORDER_STATIC
		)

		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		self.engineSelection = {
			_("google (インターネット)"): "google",
			_("tesseract (ローカル"): "tesseract"
		}
		self.tesseractModeSelection = {
			_("横書き通常"): "jpn",
			_("横書き低負荷版"): "jpn_fast",
			_("縦書き通常"): "jpn_vert",
			_("縦書き低負荷版"): "jpn_vert_fast"
		}
		#タブコントロールの作成
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(),wx.VERTICAL)
		self.tab = creator.tabCtrl("ソース選択", event=None, style=wx.NB_NOPAGETHEME | wx.NB_MULTILINE, sizerFlag=wx.ALL, proportion=0, margin=20)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,label=_("画像ファイルから読込"))
		hCreator=views.ViewCreator.ViewCreator(self.viewMode,creator.GetPanel(),creator.GetSizer(),wx.HORIZONTAL,proportion=1)
		vCreator=views.ViewCreator.ViewCreator(self.viewMode,hCreator.GetPanel(),hCreator.GetSizer(),wx.VERTICAL,style=wx.EXPAND)

		self.filebox, self.list = vCreator.listbox(_("ファイル一覧"), (), None,-1,0,(450,200),sizerFlag=wx.ALL,proportion=1,margin=10)
		fileListKeymap = keymap.KeymapHandler(defaultKeymap.defaultKeymap)
		acceleratorTable = fileListKeymap.GetTable("fileList")
		self.filebox.SetAcceleratorTable(acceleratorTable)
		self.filebox.SetDropTarget(DropTarget(self))	#D&Dの受け入れ

		vCreator=views.ViewCreator.ViewCreator(self.viewMode,hCreator.GetPanel(),hCreator.GetSizer(),wx.VERTICAL,20)
		self.open = vCreator.button(_("追加"), self.events.open)
		self.delete = vCreator.button(_("削除"), self.events.onDelete)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,label=_("スキャナから読込"))
		self.scannerList, self.scannerListStatic = creator.listCtrl(_("スキャナ一覧"), style = wx.LC_REPORT,sizerFlag=wx.EXPAND | wx.ALL)
		self.scannerList.AppendColumn(_("名前"),width=550)
		for scanner in dtwain.getSourceStringList():
			self.scannerList.Append((scanner,))

		self.isBlankPageDetect = creator.checkbox(_("白紙を検出する"))
		self.isDuplex = creator.checkbox(_("利用可能な場合両面スキャンを使用する"))
		settingAreaCreator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(),views.ViewCreator.FlexGridSizer,10, 2)
		self.engine, self.engineStatic = settingAreaCreator.combobox(_("OCRエンジン"), list(self.engineSelection.keys()), self.events.onEngineSelect, state = 0)
		self.tesseract, self.tesseractStatic = settingAreaCreator.combobox(_("モード"), list(self.tesseractModeSelection.keys()), state = 0)
		self.tesseract.Disable()
		
		buttonAreaCreator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(),wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.startButton = buttonAreaCreator.button(_("開始"), self.events.onStart)
		self.exit = buttonAreaCreator.button(_("終了"), self.events.Exit)

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
		self.hSettingMenu=wx.Menu()
		self.hHelpMenu = wx.Menu()
		#ファイルメニューの中身
		self.open = self.RegisterMenuCommand(self.hFileMenu, "OPEN", _("変換ファイルの追加(&o)"))#ファイルリストの追加
		self.exit = self.RegisterMenuCommand(self.hFileMenu, "EXIT", _("終了(&x)"))#プログラムの終了
		#設定メニューの中身
		self.google=self.RegisterMenuCommand(self.hSettingMenu,"GOOGLE",_("Googleと連携する(&g)"))#グーグルの認証開始
		self.sendRegist = self.RegisterMenuCommand(self.hSettingMenu,"SENDREGIST",_("送るメニューにショートカットを作成(&s)"))
		self.setting = self.RegisterMenuCommand(self.hSettingMenu,"SETTINGS",_("設定画面を開く(&w)"))
	
		#ヘルプメニューの中身
		self.Page = self.RegisterMenuCommand(self.hHelpMenu, "webpage", _("ACT Laboratoryのホームページを開く(&p)"))
		self.About = self.RegisterMenuCommand(self.hHelpMenu, "ABOUT", _("このソフトについて"))
		self.Update = self.RegisterMenuCommand(self.hHelpMenu, "UPDATE", _("最新バージョンを確認"))
		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu, _("ファイル(&f)"))
		self.hMenuBar.Append(self.hSettingMenu,_("設定(&s)"))
		self.hMenuBar.Append(self.hHelpMenu, _("ヘルプ(&h)"))
		target.SetMenuBar(self.hMenuBar)
		if globalVars.app.credentialManager.isOK():
			self.hMenuBar.Enable(menuItemsStore.getRef("GOOGLE"), False)

class Events(BaseEvents):
	def onDelete(self, events=None):
		index = self.parent.filebox.GetSelection()
		if index == -1:
			return
		self.parent.filebox.Delete(index)
		del globalVars.app.fileList[index]
		self.parent.filebox.SetSelection(index-1)
		return
	def open(self, events=None):
		dialog = wx.FileDialog(None, _("画像ファイルを選択"), style=wx.FD_OPEN|wx.FD_MULTIPLE, wildcard=_("画像ファイル(*.jpg;*.png;*.gif;*.pdf) | *.jpg;*.png;*.gif;*.pdf; | すべてのファイル(*.*) | *.*"))
		if dialog.ShowModal() == wx.ID_CANCEL:
			return
		self.parent.app.addFileList(dialog.GetPaths())
		return
	def onEngineSelect(self, events):
		selection = self.parent.engine.GetStringSelection()
		if self.parent.engineSelection[selection] == "google":
			self.parent.tesseract.Disable()
		if self.parent.engineSelection[selection] == "tesseract":
			self.parent.tesseract.Enable()
		return

	def onStart(self, Events):
		sourceSelection = self.parent.tab.GetSelection()
		if sourceSelection == 0 and self.parent.filebox.GetCount() == 0:
			errorDialog(_("ファイルから変換をおこなうには最低ひとつの画像ファイルが追加されている必用があります。"))
			return
		if self.parent.engine.Selection == -1:
			errorDialog(_("OCRエンジンを選択してください。"))
			return
		#エンジンの生成
		if self.parent.engineSelection[self.parent.engine.GetStringSelection()] == "google":
			e = google.googleEngine()
			if e == errorCodes.NOT_AUTHORIZED:
				errorDialog(_("googleのOCRエンジンを使用するにはお使いのgoogleアカウントを連携する必要があります。\n設定メニューよりン連携を行ってください。"))
				return
		elif self.parent.engineSelection[self.parent.engine.GetStringSelection()] == "tesseract":
			if self.parent.tesseract.Selection == -1:
				errorDialog(_("tesseract-ocrのモードが指定されていません。"))
				return
			e = tesseract.tesseractEngine(self.parent.tesseractModeSelection[self.parent.tesseract.GetStringSelection()])
		#sourceオブジェクトの生成
		if sourceSelection == 0:
			source = file.fileSource(globalVars.app.fileList)
		elif sourceSelection == 1:
			scannerSelection = self.parent.scannerList.GetFocusedItem()
			scannerName = self.parent.scannerList.GetItemText(scannerSelection)
			source = scanner.scannerSource(scannerName, blankPageDetect = self.parent.isBlankPageDetect.GetValue(), isDuplex = self.parent.isDuplex.GetValue())
		if qDialog(_("処理を開始します。よろしいですか？"), _("確認")) == wx.ID_NO:
			return
		manager = ocrManager.manager(e, source)
		pDialog = processingDialog.Dialog(manager)
		pDialog.Initialize()
		manager.start()
		pDialog.Show()
		text = manager.getText()
		if text == "":
			dialog(_("テキストが認識されませんでした。"))
			return
		resDialog = resultDialog.Dialog(text)
		resDialog.Initialize()
		resDialog.Show()
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
			authorizeDialog = authorizing.authorizeDialog()
			authorizeDialog.Initialize()
			status = authorizeDialog.Show()

			if status==errorCodes.OK:
				self.parent.menu.hMenuBar.Enable(menuItemsStore.getRef("GOOGLE"), False)
			elif status == errorCodes.CANCELED_BY_USER:
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

		if selected == menuItemsStore.getRef("SETTINGS"):
			settingDialog = settings.settingsDialog()
			settingDialog.Initialize()
			settingDialog.Show(True)
			settingDialog.Destroy()

		if selected == menuItemsStore.getRef("webpage"):
			webbrowser.open(constants.APP_DEVELOPERS_URL)
			return
		if selected == menuItemsStore.getRef("SENDREGIST"):
			shortCut = os.environ["APPDATA"]+"\\Microsoft\\Windows\\SendTo\\"+_("SOCで文字認識を開始.lnk")
			ws = win32com.client.Dispatch("wscript.shell")
			scut=ws.CreateShortcut(shortCut)
			scut.TargetPath=sys.argv[0]
			scut.Save()
			dialog(_("送るメニューの登録が完了しました。送るメニューから「SOCで文字認識を開始」で実行できます。"), _("完了"))
		if selected == menuItemsStore.getRef("ABOUT"):
			versionDialog.versionDialog()

		if selected == menuItemsStore.getRef("UPDATE"):
			globalVars.update.update()





