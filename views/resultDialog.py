# -*- coding: utf-8 -*-
# sample

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self, text):
		super().__init__("resultDialog")
		self.text = text

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("認識結果"))
		self.InstallControls()
		return True


	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)
		tabCtrl = self.creator.tabCtrl(_("ページ切替"),sizerFlag=wx.ALL|wx.EXPAND, proportion=1, margin=5):

		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("進行状況"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)


		page = views.ViewCreator.ViewCreator(self.viewMode,tabCtrl,None,wx.VERTICAL,label=_("認識結果"),style=wx.ALL|wx.EXPAND,proportion=1,margin=20)
		self.resEdit, dummy = creator.inputbox(_("認識結果"), defaultValue = self.text, style = wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_DONTWRAP, )

		self.button = self.creator.okbutton(_("閉じる"))

	def getData(self):
		return None
