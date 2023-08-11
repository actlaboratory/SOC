# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2023 yamahubuki <itiro.ishino@gmail.com>
#Copyright (C) 2020 guredora <contact@guredora.com>


import os
import sys
import webbrowser
import win32com.client
import wx

import askEventReceiver
import clipboard
import clipboardHelper
import constants
import errorCodes
import eventReceiver
import globalVars
import keymap
import menuItemsStore
import update

from simpleDialog import *
from views import (authorizing, new, settingsDialog, versionDialog)
from .base import *

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.log.debug("created")
		self.events=Events(self,self.identifier)
		evtReceiver = eventReceiver.EventReceiver(self)
		self.evtReceiver = evtReceiver
		globalVars.manager.setOnEvent(evtReceiver.onEvent)
		askEvtReceiver = askEventReceiver.AskEventReceiver()
		globalVars.manager.setOnAskEvent(askEvtReceiver.onEvent)
		super().Initialize(
			constants.APP_NAME,
			self.app.config.getint(self.identifier,"sizeX",960,800),
			self.app.config.getint(self.identifier,"sizeY",600,600),
			self.app.config.getint(self.identifier,"positionX"),
			self.app.config.getint(self.identifier,"positionY"),
		)

		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		self.menu.Enable(menuItemsStore.getRef("COPY_TEXT"), False)
		self.menu.Enable(menuItemsStore.getRef("SAVE"), False)

		self.lastScale = (0,0)
		self.installControls()

	def installControls(self):
		tabCtrl = self.creator.tabCtrl(_("ページ切替"),sizerFlag=wx.ALL|wx.EXPAND, proportion=1, margin=0)

		# 進行状況ページ
		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("進行状況"),style=wx.ALL|wx.EXPAND,proportion=1,margin=0)
		self.statusList, dummy = page.virtualListCtrl(_("状況"), proportion=1, sizerFlag=wx.EXPAND)
		self.statusList.AppendColumn(_("名前"), width=300)
		self.statusList.AppendColumn(_("状態"), width=150)
		self.statusList.AppendColumn(_("認識済みページ数"), width=100)
		self.statusList.AppendColumn(_("OCRエンジン"), width=300)
		self.statusList.setList(globalVars.jobList)
		self.statusList.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.statusList.Bind(wx.EVT_MENU, self.events.OnMenuSelect)

		page.GetPanel().Layout()

		# 認識結果ページ
		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.HORIZONTAL,label=_("認識結果"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)

		creator = views.ViewCreator.ViewCreator(self.viewMode, page.GetPanel(), page.GetSizer(), orient=wx.VERTICAL, proportion=1, style=wx.EXPAND)
		self.jobCtrl, dummy = creator.virtualListCtrl(_("認識済みファイル"), self.itemFocused, proportion=1, sizerFlag=wx.EXPAND)
		self.jobCtrl.setList(globalVars.jobList)
		self.jobCtrl.AppendColumn(_("ファイル名"), width=250)
		self.jobCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.jobCtrl.Bind(wx.EVT_MENU, self.events.OnMenuSelect)

		self.pageCtrl, dummy = creator.virtualListCtrl(_("ページ選択"), self.itemFocused, proportion=1, sizerFlag=wx.EXPAND)
		self.pageCtrl.AppendColumn(_("ページ"), width=250)
		self.pageCtrl.setList([])
		self.pageCtrl.Disable()

		creator = views.ViewCreator.ViewCreator(self.viewMode, page.GetPanel(), page.GetSizer(), orient=wx.VERTICAL, proportion=3, style=wx.EXPAND|wx.LEFT|wx.RIGHT)
		creator.AddSpace(-1)
		self.imageView = creator.staticBitmap(_("ページ画像"), bitmap=wx.NullBitmap,proportion=1, sizerFlag=wx.EXPAND)
		self.imageView.Bind(wx.EVT_SIZE, self.updateImageLator)
		creator.AddSpace(-1)

		creator = views.ViewCreator.ViewCreator(self.viewMode, page.GetPanel(), page.GetSizer(), orient=wx.VERTICAL, proportion=3, style=wx.EXPAND)
		self.text, dummy = creator.inputbox(_("認識結果"), style=wx.TE_READONLY|wx.TE_MULTILINE, proportion=1, sizerFlag=wx.EXPAND)
		self.text.Bind(wx.EVT_KILL_FOCUS, self.onLeaveTextCtrl)
		self.text.Disable()

		page.GetPanel().Layout()


	def updateText(self):
		item = self.getCurrentItem()
		if not item:
			return
		self.text.SetValue(item.getText())
		self.text.SetInsertionPoint(item.getCursorPos())

	def updateImageLator(self,event):
		wx.CallAfter(self.updateImage)

	def updateImage(self, event=None):
		item = self.getCurrentItem()
		if not item:
			return
		try:
			if (item.getFormat() | constants.FORMAT_PDF_ALL)>0:
				image = wx.Image(item.getPath())
				x = self.imageView.GetContainingSizer().GetSize()[0] / image.GetWidth()
				y = self.imageView.GetContainingSizer().GetSize()[1] / image.GetHeight()
				scale = max(0.001,min(x,y))	# 0になると後続でエラーなのでmaxで対策
				self.imageView.SetBitmap(
					image.Rescale(
						int(image.GetWidth()*scale),
						int(image.GetHeight()*scale)
					).ConvertToBitmap()
				)
				if self.lastScale != (x,y):
					self.lastScale = (x,y)
					self.imageView.GetParent().Layout()
				return
		except NotImplementedError as e:
			pass
		self.imageView.SetBitmap(wx.NullBitmap)
		self.lastScale = (0,0)

	def itemFocused(self, event):
		self.menu.Enable(menuItemsStore.getRef("COPY_TEXT"), True)
		self.menu.Enable(menuItemsStore.getRef("SAVE"), True)
		self.text.Enable()
		job = self.getCurrentJob()
		if not job:
			return
		obj = event.GetEventObject()
		if obj == self.jobCtrl:
			# ジョブが選択された
			self.pageCtrl.setList(job.getProcessedItems())
			self.pageCtrl.Focus(job.getSelectedPage())
			self.pageCtrl.Select(job.getSelectedPage())
			self.pageCtrl.Enable()
			self.updateText()
			self.updateImage()
		elif obj == self.pageCtrl:
			# ページが選択された
			job.setSelectedPage(self.pageCtrl.GetFocusedItem())
			self.updateText()
			self.updateImage()

	def getCurrentItem(self):
		job = self.getCurrentJob()
		if not job:
			return None
		focus = self.pageCtrl.GetFocusedItem()
		if focus < 0:
			return None
		return job.getProcessedItems()[focus]

	def getCurrentJob(self):
		focus = self.jobCtrl.GetFocusedItem()
		if focus < 0:
			return None
		return globalVars.jobList[focus]

	def onContextMenu(self, event):
		menu = wx.Menu()
		menu.SetInvokingWindow(event.GetEventObject())
		self.menu.RegisterMenuCommand(menu, {
			"COPY_TEXT": self.events.copyText,
			"SAVE": self.events.saveText,
			"CANCEL": self.events.cancelJob,
		})
		if event.GetEventObject() == self.statusList:
			menu.Enable(menuItemsStore.getRef("SAVE"),False)
			menu.Enable(menuItemsStore.getRef("COPY_TEXT"),False)
		job = globalVars.jobList[event.GetEventObject().GetFocusedItem()]
		if event.GetEventObject().GetFocusedItem() == 0 or job.isDone() or job.hasCancelFlag():
			menu.Enable(menuItemsStore.getRef("CANCEL"),False)
		event.GetEventObject().PopupMenu(menu, event)

	def onLeaveTextCtrl(self, event):
		item = self.getCurrentItem()
		if not item:
			return
		item.setCursorPos(self.text.GetInsertionPoint())
		event.Skip()

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""
		#メニューの大項目を作る
		self.hFileMenu = wx.Menu()
		self.hSettingMenu=wx.Menu()
		self.hHelpMenu = wx.Menu()
		#ファイルメニューの中身
		self.RegisterMenuCommand(self.hFileMenu, {
			"NEW": self.parent.events.newJob,
			"COPY_TEXT": self.parent.events.copyText,
			"SAVE": self.parent.events.saveText,
			"EXIT": self.parent.events.exit,
		})

		#設定メニューの中身
		self.RegisterMenuCommand(self.hSettingMenu, {
			"GOOGLE": self.parent.events.googleAuth,
			"SENDREGIST": self.parent.events.registSendMenu,
			"SETTINGS": self.parent.events.setting,
		})

		#ヘルプメニューの中身
		self.RegisterMenuCommand(self.hHelpMenu, {
			"HOMEPAGE": self.parent.events.openDevelopperWebSite,
			"UPDATE": self.parent.events.update,
			"ABOUT": self.parent.events.about,
		})

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu, _("ファイル(&F)"))
		self.hMenuBar.Append(self.hSettingMenu,_("設定(&S)"))
		self.hMenuBar.Append(self.hHelpMenu, _("ヘルプ(&H)"))
		target.SetMenuBar(self.hMenuBar)
		if globalVars.app.credentialManager.isOK():
			self.hMenuBar.Enable(menuItemsStore.getRef("GOOGLE"), False)

class Events(BaseEvents):
	def newJob(self, event):
		d = new.Dialog()
		d.Initialize()
		d.Show()

	def copyText(self, event):
		if self.parent.jobCtrl.GetFocusedItem() < 0:
			return
		text = self.parent.text.GetValue()
		with clipboardHelper.Clipboard() as c:
			c.set_unicode_text(text)

	def saveText(self, event):
		if self.parent.jobCtrl.GetFocusedItem() < 0:
			return
		d = wx.FileDialog(self.parent.hFrame, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=_("テキストファイル(*.txt)") + "|*.txt|" + _("全てのファイル(*.*)") + "|*.*")
		if d.ShowModal() == wx.ID_CANCEL:
			return
		try:
			with open(d.GetPath(), "w") as f:
				f.write(self.parent.text.getValue())
		except IOError as e:
			errorDialog(_("保存に失敗しました。詳細: %s") % (e))

	def cancelJob(self, event):
		obj = event.GetEventObject()
		if type(obj) == wx.Menu:
			obj = obj.GetInvokingWindow()
		idx = obj.GetFocusedItem()
		if idx < 0:
			return
		globalVars.jobList[idx].cancel()

	def exit(self, event = None):
		self.parent.hFrame.Close()

	def googleAuth(self, event):
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

	def setting(self, event):
		d = settingsDialog.Dialog()
		d.Initialize()
		d.Show()

	def registSendMenu(self, event):
		shortCut = os.environ["APPDATA"]+"\\Microsoft\\Windows\\SendTo\\"+_("SOCで文字認識を開始.lnk")
		ws = win32com.client.Dispatch("wscript.shell")
		scut=ws.CreateShortcut(shortCut)
		scut.TargetPath=sys.argv[0]
		scut.Save()
		dialog(_("送るメニューの登録が完了しました。送るメニューから「SOCで文字認識を開始」で実行できます。"), _("完了"))

	def openDevelopperWebSite(self, event):
		webbrowser.open(constants.APP_DEVELOPERS_URL)

	def about(self, event):
		versionDialog.versionDialog()

	def update(self, event):
		update.checkUpdate()

	def WindowResize(self,event):
		#ウィンドウがアクティブでない時(ウィンドウ生成時など)のイベントは無視
		if self.parent.hFrame.IsActive():
			self.parent.imageView.SetBitmap(wx.NullBitmap)
		super().WindowResize(event)
