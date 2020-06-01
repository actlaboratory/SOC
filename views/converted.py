# -*- coding: utf-8 -*-
# sample dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__()
		self.result = ""

	def Initialize(self):
		self.identifier="converted result dialog"#このビューを表す文字列
		self.log=getLogger(self.identifier)
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("認識結果"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.resultView,static = self.creator.inputbox("認識結果", x=800,defaultValue=self.result, style=wx.TE_MULTILINE|wx.TE_READONLY)
		self.bOk=self.creator.okbutton(_("OK"), None)

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
	#	return self.iText.GetLineText(0)
