# -*- coding: utf-8 -*-
# Add New dialog

import dtwain
import os
import wx

import engines
import defaultKeymap
import globalVars
import keymap
import task
import views.ViewCreator

from logging import getLogger
from views.baseDialog import *
from sources import file, scanner, clipboard
from simpleDialog import errorDialog

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("jobCreateDialog")
		self.files = []

	def Initialize(self, files=[]):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("新しく文字認識を開始"))
		self.InstallControls()
		self.addFiles(files)
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,margin=0)
		#タブコントロールの作成
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),wx.VERTICAL)
		self.tab = creator.tabCtrl(_("ソース選択"), event=None, style=wx.NB_NOPAGETHEME | wx.NB_MULTILINE, sizerFlag=wx.ALL, proportion=0, margin=20)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,label=_("ファイル"))
		hCreator=views.ViewCreator.ViewCreator(self.viewMode,creator.GetPanel(),creator.GetSizer(),wx.HORIZONTAL,proportion=1)
		vCreator=views.ViewCreator.ViewCreator(self.viewMode,hCreator.GetPanel(),hCreator.GetSizer(),wx.VERTICAL,style=wx.EXPAND)

		self.filebox, self.list = vCreator.listbox(_("ファイル一覧"), (), None,-1,0,(450,200),sizerFlag=wx.ALL,proportion=1,margin=10)
		fileListKeymap = keymap.KeymapHandler(defaultKeymap.defaultKeymap)
		acceleratorTable = fileListKeymap.GetTable("fileList")
		self.filebox.SetAcceleratorTable(acceleratorTable)
		self.filebox.SetDropTarget(DropTarget(self))	#D&Dの受け入れ

		vCreator=views.ViewCreator.ViewCreator(self.viewMode,hCreator.GetPanel(),hCreator.GetSizer(),wx.VERTICAL,20)
		self.open = vCreator.button(_("追加"), self.open)
		self.delete = vCreator.button(_("削除"), self.onDelete)


		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,label=_("クリップボード"))


		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,label=_("スキャナ"))
		self.scannerList, self.scannerListStatic = creator.listCtrl(_("スキャナ一覧"), style = wx.LC_REPORT,sizerFlag=wx.EXPAND | wx.ALL)
		self.scannerList.AppendColumn(_("名前"),width=550)
		for scanner in dtwain.getSourceStringList():
			self.scannerList.Append((scanner,))

		self.blankPageDetect = creator.checkbox(_("白紙を検出する"))
		self.duplex = creator.checkbox(_("利用可能な場合両面スキャンを使用する"))

		# エンジンの設定
		settingAreaCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),views.ViewCreator.FlexGridSizer,10, 2)
		self.engine, self.engineStatic = settingAreaCreator.combobox(_("OCRエンジン"), [i.getName() for i in engines.getEngines()], self.onEngineSelect, state = 0)
		settingAreaCreator.AddEmptyCell()
		self.engineConfigButton = settingAreaCreator.button(_("エンジンの設定(&S)"), self.onEngineSetting, sizerFlag=wx.ALIGN_RIGHT|wx.ALL)

		buttonAreaCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),wx.HORIZONTAL,20,style=wx.ALIGN_RIGHT)
		self.startButton = buttonAreaCreator.okbutton(_("開始"), self.onStart)
		self.cancelButton = buttonAreaCreator.cancelbutton(_("キャンセル"))

		self.onEngineSelect()	# 初期状態反映のため一度実行

	def open(self, event=None):
		dialog = wx.FileDialog(None, _("画像ファイルを選択"), style=wx.FD_OPEN|wx.FD_MULTIPLE, wildcard=_("画像ファイル(*.jpg;*.png;*.gif;*.pdf) | *.jpg;*.png;*.gif;*.pdf; | すべてのファイル(*.*) | *.*"))
		if dialog.ShowModal() == wx.ID_CANCEL:
			return
		files = dialog.GetPaths()
		self.addFiles(files)

	def addFiles(self, files):
		error = False
		add = False
		for file in files:
			if os.path.isdir(file):
				for tp in os.walk(file, False):
					for file in tp[2]:
						if self._addFile(tp[0] + "\\" + file):
							add = True
			else:
				if self._addFile(file):
					add = True
				else:
					error = True
		if error:
			if add:
				errorDialog(_("対応していないフォーマットのファイルは除外され、一部のファイルのみ追加されました。"))
			else:
				errorDialog(_("このフォーマットのファイルには対応していないため、追加できませんでした。"))

	def _addFile(self,file):
		if not os.path.isfile(file):
			return False
		if file in self.files:
			return True
		if os.path.splitext(file)[1][1:].lower() not in constants.EXT_TO_FORMAT.keys():
			return False
		self.files.append(file)
		self.filebox.Append(os.path.basename(file))
		return True

	def onDelete(self, event=None):
		index = self.filebox.GetSelection()
		if index == -1:
			return
		self.filebox.Delete(index)
		del self.files[index]
		self.filebox.SetSelection(index-1)
		return

	def onEngineSelect(self, event=None):
		self.engineConfigButton.Enable(engines.getEngines()[self.engine.GetSelection()].getSettingDialog() != None)
		return

	def onStart(self, event):
		# source
		sourceStr = self.tab.GetPageText(self.tab.GetSelection())
		if sourceStr == _("ファイル"):
			source = file.fileSource(self.files)
		elif sourceStr == _("スキャナ"):
			source = scanner.scannerSource(self.scannerList.GetItemText(self.scannerList.GetFocusedItem()), blankPageDetect=self.blankPageDetect.GetValue(), isDuplex=self.duplex.GetValue())
		elif sourceStr == _("クリップボード"):
			source = clipboard.ClipboardSource()

		# engine
		engine = engines.getEngines()[self.engine.GetSelection()]()

		# task
		globalVars.manager.addTask(task.task(source, engine))
		event.Skip()

	def onEngineSetting(self, event):
		d = engines.getEngines()[self.engine.GetSelection()].getSettingDialog()()
		d.Initialize(self.wnd)
		d.Show()


# D&D受入関連
class DropTarget(wx.DropTarget):
	def __init__(self,parent):
		super().__init__(wx.FileDataObject())
		self.parent=parent			#mainViewオブジェクトが入る

	#マウスオーバー時に呼ばれる
	#まだマウスを放していない
	def OnDragOver(self,x,y,defResult):
		return defResult

	#ドロップされずにマウスが外に出た
	#戻り値不要
	def OnLeave(self):
		pass

	#マウスが放されたら呼ばれる
	#現在データの受け入れが可能ならTrue
	def OnDrop(self,x,y):
		return True

	#データを受け入れ、結果を返す
	def OnData(self,x,y,defResult):
		self.GetData()
		self.parent.addFiles(self.DataObject.GetFilenames())
		return defResult		#推奨されたとおりに返しておく
