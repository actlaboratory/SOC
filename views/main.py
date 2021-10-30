# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>
#Copyright (C) 2020 guredora <contact@guredora.com>

import ctypes
import copy
from jobObjects import job
import logging
import os
import pathlib
import re
import sys
import threading
import time
import webbrowser
from logging import getLogger

import clipboard
import clipboardHelper
import constants
import dtwain
import errorCodes
import eventReceiver
import globalVars
import keymap
import menuItemsStore
import ocrManager
import pdfUtil
import pywintypes
import win32com.client
import wx
from engines import google, tesseract
from simpleDialog import *
from sources import file, scanner

from stub import stub
from views import (authorizing, new, processingDialog, resultDialog, settings,
                   versionDialog, OcrDialog)

from .base import *

MSG_ALL = "（全て）"
IDX_ALL = 0

nextJobIndex = 0

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		evtReceiver = eventReceiver.EventReceiver(self)
		globalVars.manager.setOnEvent(evtReceiver.onEvent)
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
		self.menu.Enable(menuItemsStore.getRef("COPY_TEXT"), False)
		self.menu.Enable(menuItemsStore.getRef("SAVE"), False)

		self.initialized = False
		self.initializeVariables()
		self.installControls()
		self.initialized = True

	def initializeVariables(self):
		self.jobs = [None]
		self.pages = [[]]
		self.selectedPages = [0]
		self.texts = [""]
		self.cursors = [0]
		self.jobIds = []
		self.jobNames = []
		self.jobStatuses = []
		self.ocrEngines = []
		self.processedCounts = []
		self.totalCounts = []

	def installControls(self):
		tabCtrl = self.creator.tabCtrl(_("ページ切替"),sizerFlag=wx.ALL|wx.EXPAND, proportion=1, margin=5)

		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("進行状況"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)
		self.statusList, dummy = page.listCtrl(_("状況"))
		self.statusList.AppendColumn(_("名前"))
		self.statusList.AppendColumn(_("状態"))
		self.statusList.AppendColumn(_("認識済みページ数"))
		self.statusList.AppendColumn(_("OCRエンジン"))

		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("認識結果"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)
		self.selectorIdentifier = "selector"
		self.jobCtrl, dummy = page.listCtrl(_("認識済みファイル"), self.itemSelected)
		self.jobCtrl.AppendColumn(_("ファイル名"))
		self.jobCtrl.Append([MSG_ALL])
		self.jobCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.menu.keymap.Set(self.selectorIdentifier, self.jobCtrl)
		self.pageCtrl, dummy = page.listCtrl(_("ページ選択"), self.itemSelected)
		self.pageCtrl.AppendColumn(_("ページ"))
		self.pageCtrl.Append([MSG_ALL])
		self.pageCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.menu.keymap.Set(self.selectorIdentifier, self.pageCtrl)
		self.pageCtrl.Disable()
		self.text, dummy = page.inputbox(_("認識結果"), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.text.Disable()

	def updateText(self):
		jobIdx = self.jobCtrl.GetFocusedItem()
		if jobIdx < 0:
			return
		if jobIdx == 0:
			text = self.texts[jobIdx]
			cursor = self.cursors[jobIdx]
		else:
			pageIdx = self.pageCtrl.GetFocusedItem()
			text = self.texts[jobIdx][pageIdx]
			cursor = self.cursors[jobIdx][pageIdx]
		self.text.SetValue(text)
		self.text.SetInsertionPoint(cursor)

	def getJobIdx(self, job):
		return self.jobs.index(job)

	def itemSelected(self, event):
		self.menu.Enable(menuItemsStore.getRef("COPY_TEXT"), True)
		self.menu.Enable(menuItemsStore.getRef("SAVE"), True)
		self.text.Enable()
		jobIdx = self.jobCtrl.GetFocusedItem()
		hasMultiplePages = len(self.pages[jobIdx]) > 1
		obj = event.GetEventObject()
		if obj == self.jobCtrl:
			# ジョブが選択された
			if hasMultiplePages:
				self.pageCtrl.DeleteAllItems()
				self.pageCtrl.Append([MSG_ALL])
				for i in range(1, len(self.pages[jobIdx])):
					self.pageCtrl.Append([_("%dページ") % i])
				self.pageCtrl.Focus(self.selectedPages[jobIdx])
				self.pageCtrl.Select(self.selectedPages[jobIdx])
				self.pageCtrl.Enable()
			else:
				self.pageCtrl.Disable()
				self.pageCtrl.DeleteAllItems()
				self.pageCtrl.Append([MSG_ALL])
			self.updateText()
		elif obj == self.pageCtrl:
			# ページが選択された
			self.selectedPages[jobIdx] = self.pageCtrl.GetFocusedItem()
			self.updateText()

	def addJob(self, job, engine):
		global nextJobIndex
		name = job.getName()
		status = _("準備中")
		engine = engine.getName()
		processedCount = 0
		totalCount = 0
		self.jobIds.insert(nextJobIndex, job.getID())
		self.statusList.InsertItem(nextJobIndex, "")
		self.jobNames.insert(nextJobIndex, name)
		self.statusList.SetItem(nextJobIndex, 0, name)
		self.jobStatuses.insert(nextJobIndex, status)
		self.statusList.SetItem(nextJobIndex, 1, status)
		self.processedCounts.insert(nextJobIndex, processedCount)
		self.totalCounts.insert(nextJobIndex, totalCount)
		self.statusList.SetItem(nextJobIndex, 2, "%d/%d" % (processedCount, totalCount))
		self.ocrEngines.insert(nextJobIndex, engine)
		self.statusList.SetItem(nextJobIndex, 3, engine)
		nextJobIndex += 1

	def setProcessedCount(self, index, processed):
		self.processedCounts[index] = processed
		self.statusList.SetItem(index, 2, "%d/%d" % (self.processedCounts[index], self.totalCounts[index]))

	def getProcessedCount(self, index):
		return self.processedCounts[index]

	def setTotalCount(self, index, total):
		self.totalCounts[index] = total
		self.statusList.SetItem(index, 2, "%d/%d" % (self.processedCounts[index], self.totalCounts[index]))

	def getTotalCount(self, index):
		return self.totalCounts[index]

	def getJobIdIndex(self, id):
		return self.jobIds.index(id)

	def getJobStatus(self, index):
		return self.jobStatuses[index]

	def onContextMenu(self, event):
		if self.jobCtrl.GetFocusedItem() < 0:
			return
		menu = wx.Menu()
		menu.Bind(wx.EVT_MENU, self.events.OnMenuSelect)
		baseMenu = BaseMenu(self.selectorIdentifier)
		baseMenu.RegisterMenuCommand(menu, [
			"COPY_TEXT",
			"SAVE",
		])
		event.GetEventObject().PopupMenu(menu, event)

	def getText(self):
		jobIdx = self.jobCtrl.GetFocusedItem()
		if jobIdx < 0:
			return ""
		elif jobIdx == 0:
			return self.texts[0]
		else:
			return self.texts[jobIdx][self.pageCtrl.GetFocusedItem()]

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""
		#メニューの大項目を作る
		self.hFileMenu = wx.Menu()
		self.hSettingMenu=wx.Menu()
		self.hHelpMenu = wx.Menu()
		#ファイルメニューの中身
		self.RegisterMenuCommand(self.hFileMenu, [
			"NEW",
			"COPY_TEXT",
			"SAVE",
			"EXIT",
		])
		#設定メニューの中身
		self.RegisterMenuCommand(self.hSettingMenu, [
			"GOOGLE",
			"SENDREGIST",
			"SETTINGS",
		])
		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu, [
			"HOMEPAGE",
			"UPDATE",
			"ABOUT",
		])
		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu, _("ファイル(&F)"))
		self.hMenuBar.Append(self.hSettingMenu,_("設定(&S)"))
		self.hMenuBar.Append(self.hHelpMenu, _("ヘルプ(&H)"))
		target.SetMenuBar(self.hMenuBar)
		if globalVars.app.credentialManager.isOK():
			self.hMenuBar.Enable(menuItemsStore.getRef("GOOGLE"), False)

class Events(BaseEvents):
	def Exit(self, event = None):
		self.parent.hFrame.Close()

	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る

		if selected == menuItemsStore.getRef("NEW"):
			d = new.Dialog()
			d.Initialize()
			d.Show()
		if selected == menuItemsStore.getRef("SAVE"):
			if self.parent.jobCtrl.GetFocusedItem() < 0:
				return
			text = self.parent.getText()
			d = wx.FileDialog(self.parent.hFrame, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=_("テキストファイル(*.txt)") + "|*.txt|" + _("全てのファイル(*.*)") + "|*.*")
			if d.ShowModal() == wx.ID_CANCEL:
				return
			path = d.GetPath()
			try:
				with open(path, "w") as f:
					f.write(text)
			except IOError as e:
				errorDialog(_("保存に失敗しました。詳細: %s") % (e))
		if selected == menuItemsStore.getRef("EXIT"):
			self.Exit()
		if selected == menuItemsStore.getRef("DELETE"):
			self.onDelete()
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

		if selected == menuItemsStore.getRef("HOMEPAGE"):
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
		if selected == menuItemsStore.getRef("COPY_TEXT"):
			if self.parent.jobCtrl.GetFocusedItem() < 0:
				return
			text = self.parent.getText()
			with clipboardHelper.Clipboard() as c:
				c.set_unicode_text(text)
