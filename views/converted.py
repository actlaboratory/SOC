# -*- coding: utf-8 -*-
# sample dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from simpleDialog import *
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__()
		self.result = ""
		self.list = []
		self.tesseract_flag= False# Trueならスペース置換ボタンが有効になる

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
		self.resultView,static = self.creator.inputbox("認識結果", x=800,defaultValue=self.result, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)
		self.repButton = self.creator.button(_("スペースを置換"), self.onRep)
		if self.tesseract_flag == False:
			self.repButton.Disable()
		self.bOk=self.creator.okbutton(_("OK"), None)

	def onRep(self, event):
		if qDialog(_("余計なスペースをすべて置換します。文章が崩れる可能性があります。よろしいですか？")) == wx.ID_NO:
			return
		saved = ""
		for path in self.list:
			text=path.read_text().replace(" ", "")
			path.write_text(text)
			saved += text
		dialog(_("置換が完了しました。"), _("置換"))
		self.resultView.SetValue(saved)

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
	#	return self.iText.GetLineText(0)
