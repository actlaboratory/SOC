# -*- coding: utf-8 -*-
# Ocr Dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

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
		else:
			# タイマーでのみ実行
			root = self.tree.GetRootItem()
			ret = self.jobs[len(jobs):]
		self.map[root] = self.manager.getAllText()
		for job in ret:
			item1 = self.tree.AppendItem(root, job.getFileName())
			self.map[item1] = job.getAllItemText()
			for item in job.getItems():
				item2 = self.tree.AppendItem(item1, item.getFileName())
				self.map[item2] = item.getText()
		self.updateText()
		self.jobs = jobs

	def updateText(self):
		# 「全て」を選択時、新しく認識されたテキストを追加する
		root = self.tree.GetRootItem()
		if self.tree.GetFocusedItem() != root:
			return
		new = self.map[root][len(self.text.GetValue()):]
		cursor = self.text.GetSelection()
		self.text.AppendText(new)
		self.text.SetSelection(cursor[0], cursor[1])

	def itemSelected(self, event):
		self.text.Clear()
		self.text.SetValue(self.map[event.GetItem()])

	def onTimerEvent(self, event):
		self.update()

	def onClose(self, event):
		self.timer.Stop()
		event.Skip()
