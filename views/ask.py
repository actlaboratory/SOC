# -*- coding: utf-8 -*-
# Dialog for Ask Event

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self, message, selections):
		super().__init__("askDialog")
		self.message = message
		self.selections = selections
		self.result = None

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("確認"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)
		self.static = self.creator.staticText(self.message, proportion=1, sizerFlag=wx.EXPAND)
		self.buttons = {}
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,style=wx.ALL,margin=20)
		for k, v in self.selections.items():
			b = creator.button(k, self.onButtonPressed, proportion=1, sizerFlag=wx.EXPAND)
			self.buttons[b] = v

	def onButtonPressed(self, event):
		obj = event.GetEventObject()
		self.result = self.buttons[obj]
		self.wnd.EndModal(wx.ID_OK)

	def getData(self):
		return self.result
