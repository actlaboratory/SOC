# -*- coding: utf-8 -*-
# authorize dialog

import wx
import time
import errorCodes
import threading
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import webbrowser
class authorizeDialog(BaseDialog):
	def __init__(self):
		super().__init__("authorizingDialog")
		self.web, self.pid = None, None
		self.authThread = None
		self.__isArrive = True
		self.__authStarted = False

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("OAuth認証"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL, 20)
		self.static = self.creator.staticText(_("ブラウザを開いて認証手続きを行います。\r\nよろしいですか？"),wx.ALIGN_LEFT | wx.ST_ELLIPSIZE_MIDDLE,-1,wx.ALIGN_LEFT)
		self.buttonCreator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20, style=wx.ALIGN_RIGHT)
		self.bStart=self.buttonCreator.button(_("開始") + "(&S)", self.authorize)
		self.bCancel=self.buttonCreator.button(_("キャンセル") + "(&C)", self.canceled)
		self.wnd.SetDefaultItem(self.bStart)


	def authorize(self,vevt):
		if self.__authStarted:
			self.finish()
			return
		self.__authStarted = True
		self.static.SetLabel(_("認証を待機中..."))
		self.bStart.Disable()


		#認証プロセスの開始、認証用URL取得
		url=globalVars.app.credentialManager.MakeFlow()
		#ブラウザの表示
		globalVars.app.say(_("ブラウザを開いています..."))
		#webView=views.web.Dialog(url,"http://localhost")
		#webView.Initialize()
		#webView.Show()
		webbrowser.open(url)

		self.authThread = threading.Thread(target=self.__auth)
		self.authThread.start()

	def __auth(self):
		
		#ユーザの認証待ち
		status=errorCodes.WAITING_USER
		evt=threading.Event()
		while(status==errorCodes.WAITING_USER):
			if not self.__isArrive: return
			if status==errorCodes.WAITING_USER:
				status=globalVars.app.credentialManager.getCredential()
				if status == errorCodes.OK:
					wx.CallAfter(self.authOk)
					return
			wx.YieldIfNeeded()
			evt.wait(0.1)
		wx.CallAfter(self.end, errorCodes.GOOGLE_ERROR)
	
	def canceled(self, events):
		self.__isArrive = False
		self.wnd.EndModal(errorCodes.CANCELED_BY_USER)


	def authOk(self):
		globalVars.app.say(_("認証完了。ブラウザを閉じてください。"))
		if self.web != None and self.pid != None and self.web.Exists(self.pid): wx.Process.Kill(self.pid,wx.SIGTERM) #修了要請
		self.static.SetLabel(_("認証が完了しました。"))
		self.bCancel.Disable()
		self.bStart.SetLabel(_("完了") + "(&F)")
		self.bStart.Enable()
	
	def end(self, code):
		self.wnd.EndModal(code)

	def finish(self):
		self.wnd.EndModal(errorCodes.OK)
