# -*- coding: utf-8 -*-
# converting dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import constants

class langDialog(BaseDialog):
	def __init__(self):
		super().__init__()
	def Initialize(self):
		self.identifier="language selecter"#このビューを表す文字列
		self.log=getLogger("Soc%s" % (self.identifier))
		self.log.debug("created")
		super().Initialize(None,_("language settings"),0)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		#翻訳
		self.langSelect = self.creator.combobox(_("select language"), constants.SUPPORTED_LANGUAGE, stat=0)
		self.ok = self.creator.okbutton("ok", None)

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	def GetData(self):
		return self.langSelect.GetSelectionString()
