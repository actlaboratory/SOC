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
		self.autoUpdate = creator.checkbox(_("起動時にアップデートを確認"), style = wx.CHK_2STATE)
		self.timeout, dummy = creator.inputbox(_("アップデート確認時のタイムアウト（秒数）"))
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("OCR"))
		self.tmpEdit, dummy = creator.inputbox(_("一時ファイルの場所"))
		self.saveSelect = creator.checkbox(_("認識結果をもとの画像ファイルと同じディレクトリに保存する"), self.switch)
		self.saveDir, dummy = creator.inputbox(_("認識結果の保存先"), style = wx.TE_READONLY)
		self.changeBtn = creator.button(_("参照"), self.browse)


		self.okbtn = self.creator.okbutton(_("OK"), self.onOkBtn)
		self.cancelBtn = self.creator.cancelbutton(_("キャンセル"), self.onCancelBtn)


	def onOkBtn(self, event):
		print("ok")
		self.Destroy()

	def onCancelBtn(self, event):
		print("cancel")
		self.Destroy()

	def switch(self, event = None):
		if self.saveSelect.IsChecked():
			self.saveDir.Disable()
			self.changeBtn.Disable()
		else:
			self.saveDir.Enable()
			self.changeBtn.Enable()

	def browse(self, event):
		dialog = wx.DirDialog(None, _("保存先を選択"))
		if dialog.ShowModal() == wx.ID_OK:
			dir = dialog.GetPath()
			self.saveDir.SetValue(dir)
		return

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
		return None
