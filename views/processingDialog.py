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

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("配信者の情報"))
		self.InstallControls()
		return True


	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.statusEdit,dummy = self.creator.inputbox(_("状況"), None, style = wx.TE_READONLY)
		self.cancelButton=self.creator.button(_("キャンセル"), self.onCancel)
		self.timer = wx.Timer(self.wnd)
		self.wnd.Bind(wx.EVT_TIMER, self.onTimer)
		self.timer.Start(300)

	def onTimer(self, event):
		if self.manager.isDone():
			self.timer.Stop()
			self.wnd.EndModal(wx.ID_OK)
		statusStr = self.manager.getStatusString()
		if statusStr == self.statusEdit.GetValue():
			return
		self.statusEdit.SetValue(statusStr)
		return

	def onCancel(self, event):
		return

	def GetData(self):
		return None
		
