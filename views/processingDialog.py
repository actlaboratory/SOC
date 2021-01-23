# -*- coding: utf-8 -*-
#processing dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self, manager):
		super().__init__("viewBroadcasterDialog")
		self.manager = manager
		self.waiting = False

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("認識中"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.statusList,dummy = self.creator.listCtrl(_("状況"), style = wx.LC_REPORT)
		self.statusList.AppendColumn(_("項目"))
		self.statusList.AppendColumn(_("状況"))
		self.statusList.Append((_("出力"), ""))
		self.statusList.Append((_("認識"), ""))
		self.interruptButton=self.creator.button(_("中止"), self.onInterrupt)
		self.timer = wx.Timer(self.wnd)
		self.wnd.Bind(wx.EVT_TIMER, self.onTimer)
		self.timer.Start(100)

	def onTimer(self, event):
		if self.manager.isDone():
			self.timer.Stop()
			self.wnd.EndModal(wx.ID_OK)
		status = self.manager.getStatusString()
		self.statusList.SetItem(0, 1, status["source"])
		self.statusList.SetItem(1, 1, status["engine"])
		self.manager.updateMessageQueue()
		if self.manager.isMessageEmpty():
			return
		self._showMessage()

	def _showMessage(self):
		data = self.manager.getMessage()
		text = data[0]
		retQueue = data[1]
		result = simpleDialog.qDialog(text)
		retQueue.put(result)

	def onInterrupt(self, event):
		return

	def GetData(self):
		return None
		
