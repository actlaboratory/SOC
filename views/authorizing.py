# -*- coding: utf-8 -*-
# authorize dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class authorizeDialog(BaseDialog):
	def __init__(self):
		self.cancel = False
		super().__init__("authorizingDialog")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("待機中..."),0)
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.creator.staticText(_("待機中..."),wx.ALIGN_CENTER,-1,wx.ALIGN_CENTER)
		self.static = self.creator.staticText(_("認証大気中..."),wx.ALIGN_CENTER | wx.ST_ELLIPSIZE_MIDDLE,530,wx.ALIGN_CENTER)
		self.bCancel=self.creator.button(_("キャンセル"), self.canceled,sizerFlag=wx.ALIGN_CENTER)

	def canceled(self, events):
		self.cancel = True


	def end(self):
		self.wnd.EndModal(wx.ID_OK)

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
		return None
