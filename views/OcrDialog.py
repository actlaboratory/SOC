# -*- coding: utf-8 -*-
# Ocr Dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import copy
from views.base import BaseMenu

class Dialog(BaseDialog):
	def __init__(self):
		self.initialized = False
		self.jobs = []
		self.map = {}
		super().__init__("Ocr Dialog")

	def Initialize(self, manager):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("OCR実行中"))
		self.manager = manager
		self.InstallControls()
		self.initialized = True
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)
		tabCtrl = self.creator.tabCtrl(_("ページ切替"),sizerFlag=wx.ALL|wx.EXPAND, proportion=1, margin=5)

		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("進行状況"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)


		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("認識結果"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)
		self.tree, dummy = page.treeCtrl(_("認識済みファイル"), self.itemSelected)
		self.tree.Bind(wx.EVT_CONTEXT_MENU, self.onContextMenu)
		self.treeIdentifier = "resultTree"
		globalVars.app.hMainView.menu.keymap.Set(self.treeIdentifier, self.tree, globalVars.app.hMainView.events.OnMenuSelect)
		self.text, dummy = page.inputbox(_("認識結果"), style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.update()
		self.creator.okbutton(_("閉じる"), self.onClose)

		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.onTimerEvent)
		self.timer = wx.Timer(self.evtHandler)
		self.timer.Start(300)

	def getData(self):
		return None

	def update(self):
		jobs = self.manager.getProcessedJobs()
		if not self.initialized:
			# 初回のみ実行
			root = self.tree.AddRoot(_("（全て）"))
			ret = jobs
			self.map[root] = {"cursor": 0, "text": self.manager.getAllText()}
		else:
			# タイマーでのみ実行
			root = self.tree.GetRootItem()
			ret = jobs[len(self.jobs):]
			self.map[root]["text"] = self.manager.getAllText()
		for job in ret:
			item1 = self.tree.AppendItem(root, job.getFileName())
			if item1 in self.map:
				self.map[item1]["text"] = job.getAllItemText()
			else:
				self.map[item1] = {"cursor": 0, "text": job.getAllItemText()}
			items = job.getItems()
			if len(items) < 2:
				continue
			for item in items:
				item2 = self.tree.AppendItem(item1, item.getFileName())
				if item2 in self.map:
					self.map[item2]["text"] = item.getText()
				else:
					self.map[item2] = {"cursor": 0, "text": item.getText()}
		self.updateText()
		self.jobs = copy.deepcopy(jobs)

	def updateText(self):
		# 「全て」を選択時、新しく認識されたテキストを追加する
		root = self.tree.GetRootItem()
		if self.tree.GetFocusedItem() != root:
			return
		new = self.map[root]["text"][len(self.text.GetValue()):]
		cursor = self.text.GetSelection()
		self.text.AppendText(new)
		self.text.SetSelection(cursor[0], cursor[1])

	def itemSelected(self, event):
		prev = event.GetOldItem()
		cursor = self.text.GetInsertionPoint()
		if prev.GetID() is not None:
			self.map[prev]["cursor"] = cursor
		self.text.Clear()
		focus = event.GetItem()
		self.text.SetValue(self.map[focus]["text"])
		self.text.SetInsertionPoint(self.map[focus]["cursor"])

	def onTimerEvent(self, event):
		self.update()

	def onClose(self, event):
		self.timer.Stop()
		event.Skip()

	def onContextMenu(self, event):
		menu = wx.Menu()
		menu.Bind(wx.EVT_MENU, globalVars.app.hMainView.events.OnMenuSelect)
		baseMenu = BaseMenu(self.treeIdentifier)
		baseMenu.RegisterMenuCommand(menu, [
			"COPY_TEXT",
		])
		self.tree.PopupMenu(menu, event)
