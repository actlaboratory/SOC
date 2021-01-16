# -*- coding: utf-8 -*-
#processing dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

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
		self.statusEdit,dummy = self.creator.inputbox(_("状況"), None, style = wx.TE_READONLY)
		self.interruptButton=self.creator.button(_("中止"), self.onInterrupt)
		self.timer = wx.Timer(self.wnd)
		self.wnd.Bind(wx.EVT_TIMER, self.onTimer)
		self.timer.Start(300)

	def onTimer(self, event):
		if self.manager.isDone():
			self.timer.Stop()
			self.wnd.EndModal(wx.ID_OK)
		status = self.manager.getStatusString()
		
		return

	def onInterrupt(self, event):
		return

	def GetData(self):
		return None
		
