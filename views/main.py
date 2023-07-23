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
			660,
			700,
			self.app.config.getint(self.identifier,"positionX"),
			self.app.config.getint(self.identifier,"positionY"),
			style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.BORDER_STATIC
		)

		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		self.menu.Enable(menuItemsStore.getRef("COPY_TEXT"), False)
		self.menu.Enable(menuItemsStore.getRef("SAVE"), False)

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

		page.GetPanel().Layout()

		# 認識結果ページ
		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.HORIZONTAL,label=_("認識結果"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)
		creator = views.ViewCreator.ViewCreator(self.viewMode, page.GetPanel(), page.GetSizer(), orient=wx.VERTICAL, proportion=1, style=wx.EXPAND)
		self.selectorIdentifier = "selector"

		self.jobCtrl, dummy = creator.virtualListCtrl(_("認識済みファイル"), self.itemFocused, proportion=1, sizerFlag=wx.EXPAND)
		self.jobCtrl.setList(globalVars.jobList)
		self.jobCtrl.AppendColumn(_("ファイル名"))
		self.jobCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.menu.keymap.Set(self.selectorIdentifier, self.jobCtrl)

		self.pageCtrl, dummy = creator.virtualListCtrl(_("ページ選択"), self.itemFocused, proportion=1, sizerFlag=wx.EXPAND)
		self.pageCtrl.AppendColumn(_("ページ"), width=250)
		self.pageCtrl.setList([])
		self.pageCtrl.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.menu.keymap.Set(self.selectorIdentifier, self.pageCtrl)
		self.pageCtrl.Disable()

		creator = views.ViewCreator.ViewCreator(self.viewMode, page.GetPanel(), page.GetSizer(), orient=wx.VERTICAL, proportion=1, style=wx.EXPAND)
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
		elif obj == self.pageCtrl:
			# ページが選択された
			job.setSelectedPage(self.pageCtrl.GetFocusedItem())
			self.updateText()

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
			d = settingsDialog.Dialog()
			d.Initialize()
			d.Show()

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
			update.checkUpdate()
		if selected == menuItemsStore.getRef("COPY_TEXT"):
			if self.parent.jobCtrl.GetFocusedItem() < 0:
				return
			text = self.parent.text.GetValue()
			with clipboardHelper.Clipboard() as c:
				c.set_unicode_text(text)
