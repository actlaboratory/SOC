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
			"white": _("通常"),
			"dark": _("白黒反転")
		}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定"))
		self.InstallControls()
		self.loadSettings()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.tab = self.creator.tabCtrl(_("カテゴリ選択"))

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("一般"))
		creator.AddSpace(20)

		grid=views.ViewCreator.ViewCreator(self.viewMode,creator.GetPanel(),creator.GetSizer(),views.ViewCreator.FlexGridSizer,space=20,label=2)
		self.reader, dummy = grid.combobox(_("スクリーンリーダー"), list(self.readerSelection.values()),textLayout=wx.HORIZONTAL)
		self.color, dummy = grid.combobox(_("配色"), list(self.colorSelection.values()),textLayout=wx.HORIZONTAL)

		self.autoUpdate = creator.checkbox(_("起動時にアップデートを確認"), style = wx.CHK_2STATE)
		self.timeout, dummy = creator.inputbox(_("アップデート確認時のタイムアウト（秒）"),x=50,textLayout=wx.HORIZONTAL)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("OCR"))
		creator.AddSpace(20)
		self.tmpEdit, dummy = creator.inputbox(_("一時ファイルの場所"),None,x=-1)
		creator=views.ViewCreator.ViewCreator(self.viewMode,creator.GetPanel(),creator.GetSizer(),wx.VERTICAL,space=0,style=wx.EXPAND | wx.ALL,label=_("認識結果の保存先"))
		self.saveSelect = creator.checkbox(_("可能な場合ファイルと同じ場所に認識結果を保存する"))
		creator=views.ViewCreator.ViewCreator(self.viewMode,creator.GetPanel(),creator.GetSizer(),wx.HORIZONTAL,style=wx.EXPAND,space=5)
		self.saveDir, dummy = creator.inputbox(_("認識結果の保存先"), None,style = wx.TE_READONLY,sizerFlag=wx.LEFT,textLayout=None,margin=30)
		self.changeBtn = creator.button(_("参照"), self.browse,sizerFlag=wx.ALIGN_CENTER_VERTICAL)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,style=wx.ALIGN_RIGHT)
		self.okbtn = creator.okbutton(_("OK"), self.onOkBtn)
		self.cancelBtn = creator.cancelbutton(_("キャンセル"), self.onCancelBtn)

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
		self.tmpEdit.SetValue(globalVars.app.getTmpDir())
		savesourcedir = globalVars.app.config.getboolean("ocr", "saveSourceDir")
		self.saveSelect.SetValue(savesourcedir)
		savedir = globalVars.app.config.getstring("ocr", "savedir", "")
		self.saveDir.SetValue(savedir)
		return

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
		return None
