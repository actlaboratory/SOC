# -*- coding: utf-8 -*-
# Tesseract settings dialog
# Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import wx

import constants
import simpleDialog
import views.ViewCreator

from enum import Enum,auto
from views.baseDialog import *



class configType(Enum):
	BOOL = auto()
	INT = auto()
	STRING = auto()
	DIC = auto()


class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("settingsDialog")
		self.iniDic = {}
		self.tesseractModeSelection = {
			"jpn": _("横書き通常"),
			"jpn_fast": _("横書き低負荷版"),
			"jpn_vert": _("縦書き通常"),
			"jpn_vert_fast": _("縦書き低負荷版"),
		}

	def Initialize(self, parent):
		super().Initialize(parent,_("Tesseractエンジンの設定"))
		self.InstallControls()
		self.load()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.mode, dummy = self.creator.combobox(_("モード"), list(self.tesseractModeSelection.values()), state = 0)

		# buttons
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,style=wx.ALIGN_RIGHT)
		self.okbtn = creator.okbutton("OK", self.onOkButton, proportion=1)
		self.cancelBtn = creator.cancelbutton(_("キャンセル"), proportion=1)

	def load(self):
		self._setValue(self.mode, "tesseract","mode", configType.DIC, self.tesseractModeSelection, list(self.tesseractModeSelection.keys())[0])

	def onOkButton(self, event):
		result = self._save()
		event.Skip()

	def _setValue(self, obj, section, key, t, prm=None, prm2=None):
		assert isinstance(obj,wx.Window)
		assert type(section)==str
		assert type(key)==str
		assert type(t)==configType

		conf=self.app.config

		if t==configType.DIC:
			assert type(prm) == dict
			assert isinstance(obj,wx.ComboBox)
			obj.SetValue(prm[conf.getstring(section,key,prm2,prm.keys())])
		elif t==configType.BOOL:
			if prm==None:
				prm = True
			assert type(prm) == bool
			obj.SetValue(conf.getboolean(section,key,prm))
		elif t==configType.STRING:
			if prm==None:
				prm = ""
			assert type(prm) == str
			obj.SetValue(conf.getstring(section,key,prm,prm2))
		self.iniDic[obj]=(t,section,key,prm,prm2)

	def _save(self):
		conf = self.app.config
		for obj,v in self.iniDic.items():
			if v[0]==configType.DIC:
				conf[v[1]][v[2]] = list(v[3].keys())[obj.GetSelection()]
			else:
				conf[v[1]][v[2]] = obj.GetValue()
