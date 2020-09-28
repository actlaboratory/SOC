# -*- coding: utf-8 -*-
# settings dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import globalVars
import simpleDialog

class settingsDialog(BaseDialog):
	def __init__(self):
		super().__init__("settingDialog")
		self.readerSelection = {
			"AUTO": _("自動選択"),
			"SAPI5": "SAPI5",
			"PCTK": "pc-talker",
			"NVDA": "NVDA",
			"JAWS": "JAWS",
			"CLIPBOARD": _("クリップボード出力"),
			"NOSPEECH": _("読み上げなし")
		}
		self.colorSelection = {
			"white": "white",
			"dark": "dark"
		}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定画面"))
		self.InstallControls()
		self.loadSettings()
		self.switch()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.tab = self.creator.tabCtrl(_("カテゴリ選択"))
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("一般"))
		self.reader, dummy = creator.combobox(_("スクリーンリーダー"), list(self.readerSelection.values()))
		self.color, dummy = creator.combobox(_("配色"), list(self.colorSelection.values()))
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
		reader = list(self.readerSelection.keys())[self.reader.GetSelection()]
		colormode = list(self.colorSelection.keys())[self.color.GetSelection()]
		update = self.autoUpdate.GetValue()
		try:
			timeout = int(self.timeout.GetValue())
		except ValueError:
			simpleDialog.errorDialog(_("タイムアウト秒数の設定値が不正です。"))
		tmpdir = self.tmpEdit.GetValue()
		saveSourceDir = self.saveSelect.GetValue()
		savedir = self.saveDir.GetValue()
		globalVars.app.config["speech"]["reader"] = reader
		globalVars.app.config["view"]["colormode"] = colormode
		globalVars.app.config["general"]["update"] = update
		globalVars.app.config["general"]["timeout"] = timeout
		globalVars.app.config["ocr"]["tmpdir"] = tmpdir
		globalVars.app.config["ocr"]["savesourcedir"] = saveSourceDir
		globalVars.app.config["ocr"]["savedir"] = savedir
		simpleDialog.dialog(_("設定を保存しました。一部の設定は再起動後から有効になります。"))
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

	def loadSettings(self):
		reader = globalVars.app.config["speech"]["reader"]
		selectionStr = self.readerSelection[reader]
		self.reader.SetStringSelection(selectionStr)
		color = globalVars.app.config.getstring("view", "colormode")
		selectionStr = self.colorSelection[color]
		self.color.SetStringSelection(selectionStr)
		update = globalVars.app.config.getboolean("general", "update")
		if update:
			self.autoUpdate.SetValue(True)
		else:
			self.autoUpdate.SetValue(False)
		timeout = globalVars.app.config.getint("general", "timeout", 3)
		self.timeout.SetValue(str(timeout))
		tmpdir = globalVars.app.tmpdir
		self.tmpEdit.SetValue(tmpdir)
		savesourcedir = globalVars.app.config.getboolean("ocr", "saveSourceDir")
		print(savesourcedir)
		if savesourcedir:
			self.saveSelect.SetValue(True)
		else:
			self.saveSelect.SetValue(False)
		savedir = globalVars.app.config.getstring("ocr", "savedir", "")
		self.saveDir.SetValue(savedir)
		return

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
		return None
