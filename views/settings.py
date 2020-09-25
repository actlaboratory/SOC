# -*- coding: utf-8 -*-
# settings dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import globalVars

class settingsDialog(BaseDialog):
	def __init__(self):
		super().__init__("settingDialog")
		self.config = globalVars.app.config

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定画面"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.tab = self.creator.tabCtrl(_("カテゴリ選択"))
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("一般"))
		self.reader, dummy = creator.combobox(_("スクリーンリーダー"), 
			(_("自動選択"), _("sapi5"), _("pc-talker"), _("NVDA"), _("JAWS")))
		self.collar, dummy = creator.combobox(_("配色"), 
			(_("white"), _("dark")))

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("アップデートと通信"))
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("消滅"))
		lastHope,dummy=creator.inputbox(_("最後の願い事"),None,_("なにもない"),x=300)
		next,dummy=creator.inputbox(_("来世の希望"),None,_("なにもない"),x=300)


		self.okbtn = self.creator.okbutton(_("OK"), self.onOkBtn)
		self.cancelBtn = self.creator.cancelbutton(_("キャンセル"), self.onCancelBtn)


	def onOkBtn(self, event):
		print("ok")
		self.Destroy()

	def onCancelBtn(self, event):
		print("cancel")
		self.Destroy()

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
		return None
