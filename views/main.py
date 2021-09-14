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

		self.initialized = False
		self.initializeVariables()
		self.installControls()
		self.initialized = True

	def initializeVariables(self):
		self.jobs = [None]
		self.pages = [[]]
		self.selectedPages = [-1]
		self.texts = [""]
		self.cursors = [0]

	def installControls(self):
		tabCtrl = self.creator.tabCtrl(_("ページ切替"),sizerFlag=wx.ALL|wx.EXPAND, proportion=1, margin=5)

		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("進行状況"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)


		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("認識結果"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)
		self.jobCtrl, dummy = page.listCtrl(_("認識済みファイル"), self.itemSelected)
		self.jobCtrl.AppendColumn(_("ファイル名"))
		self.jobCtrl.Append([MSG_ALL])
		self.jobCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.jobCtrlIdentifier = "jobCtrl"
		self.menu.keymap.Set(self.jobCtrlIdentifier, self.jobCtrl)
		self.pageCtrl, dummy = page.combobox(_("ページ選択"), [MSG_ALL], self.itemSelected)
		self.pageCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.pageCtrlIdentifier = "pageCtrl"
		self.menu.keymap.Set(self.pageCtrlIdentifier, self.pageCtrl)
		self.pageCtrl.Disable()
		self.text, dummy = page.inputbox(_("認識結果"), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.update()

		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.onTimerEvent)
		self.timer = wx.Timer(self.evtHandler)
		self.timer.Start(300)

	def update(self):
		self.log.debug("Fetching new jobs...")
		jobs = self.getAllJobs()
		if not self.initialized:
			# 初回のみ実行
			ret = jobs
		else:
			# タイマーでのみ実行
			ret = jobs[len(self.jobs):]
		self.log.debug("%d jobs retrieved." % len(ret))
		for job in ret:
			fileName = job.getFileName()
			self.log.debug("New job: %s" % fileName)
			self.jobCtrl.Append([fileName])
			self.pages.append([])
			text = self.getJobText(job)
			self.texts.append(text)
			self.cursors.append(0)
			self.selectedPages.append(-1)
			items = job.getItems()
			if len(items) < 2:
				self.log.debug("This job contains only one item.")
				continue
			self.selectedPages[-1] = 0
			self.texts[-1] = [text]
			self.cursors[-1] = [0]
			self.log.debug("This job contains %d items." % len(items))
			for item in items:
				self.pages[-1].append(item)
				self.cursors[-1].append(0)
				self.texts[-1].append(item.getText())
		self.updateText()
		self.jobs = copy.deepcopy(jobs)

	def getAllJobs(self):
		jobs = []
		for task in globalVars.manager.getTasks():
			for job in task.getProcessedJobs():
				jobs.append(job)
		return jobs

	def getAllText(self):
		ret = []
		for i in self.getAllJobs():
			ret.append(self.getJobText(i))
		return "".join(ret)

	def getJobText(self, job):
		ret = []
		for i in job.getItems():
			ret.append(i.getText())
		return "".join(ret)

	def updateText(self):
		jobIdx = self.jobCtrl.GetFocusedItem()
		if jobIdx < 0:
			return
		if len(self.pages[jobIdx]) > 0:
			pageIdx = self.pageCtrl.GetSelection()
			text = self.texts[jobIdx][pageIdx]
			cursor = self.cursors[jobIdx][pageIdx]
		else:
			text = self.texts[jobIdx]
			cursor = self.cursors[jobIdx]
		self.text.SetValue(text)
		self.text.SetInsertionPoint(cursor)

	def itemSelected(self, event):
		jobIdx = self.jobCtrl.GetFocusedItem()
		hasMultiplePages = len(self.pages[jobIdx]) > 0
		obj = event.GetEventObject()
		if obj == self.jobCtrl:
			# ジョブが選択された
			if hasMultiplePages:
				self.pageCtrl.Clear()
				self.pageCtrl.Append(MSG_ALL)
				for i in range(1, len(self.pages[jobIdx])):
					self.pageCtrl.Append(_("%dページ") % i)
				self.pageCtrl.SetSelection(self.selectedPages[jobIdx])
				self.pageCtrl.Enable()
			else:
				self.pageCtrl.Disable()
			self.updateText()

	def onTimerEvent(self, event):
		self.update()

	def onContextMenu(self, event):
		menu = wx.Menu()
		menu.Bind(wx.EVT_MENU, globalVars.app.hMainView.events.OnMenuSelect)
		baseMenu = BaseMenu(self.treeIdentifier)
		baseMenu.RegisterMenuCommand(menu, [
			"COPY_TEXT",
		])
		self.tree.PopupMenu(menu, event)

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
			"OPEN",
			"OPENVIEW",
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
		self.hMenuBar.Append(self.hFileMenu, _("ファイル(&f)"))
		self.hMenuBar.Append(self.hSettingMenu,_("設定(&s)"))
		self.hMenuBar.Append(self.hHelpMenu, _("ヘルプ(&h)"))
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

		if selected == menuItemsStore.getRef("OPEN"):
			self.open()
		if selected == menuItemsStore.getRef("NEW"):
			d = new.Dialog()
			d.Initialize()
			d.Show()
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
		if selected == menuItemsStore.getRef("OPENVIEW"):
			dialog = OcrDialog.Dialog()
			self.oDialog = dialog
			dialog.Initialize(stub())
			dialog.Show()
		if selected == menuItemsStore.getRef("COPY_TEXT"):
			item = self.oDialog.tree.GetFocusedItem()
			text = self.oDialog.map[item]["text"]
			with clipboardHelper.Clipboard() as c:
				c.set_unicode_text(text)

	def OnExit(self,event):
		# タイマーを止める
		try:
			self.hMainView.timer.Stop()
			self.hMainView.timer.Destroy()
		except:
			pass

		event.Skip()
