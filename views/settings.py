# -*- coding: utf-8 -*-
# settings dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class settingsDialog(BaseDialog):
	def __init__(self):
		self.cancel = False
		super().__init__("settingDialog")
	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定画面"),0)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.tab = self.creator.tabCtrl(_("カテゴリー"))
		self.okbtn = self.creator.button(_("OK"), self.onOkBtn)
		self.cancelBtn = self.creator.button(_("キャンセル"), self.onCancelBtn)
		

	def onOkBtn(self, event):
		print("ok")

	def onCancelBtn(self, event):
		print("cancel")

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
		return None
