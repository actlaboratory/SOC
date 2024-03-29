# Ask Event Receiver

import StringUtil
import views.ask
import wx
import winsound

# 文字数制限
L_TITLE = 50
L_MESSAGE = 300
L_BUTTON = 30

class AskEventReceiver:
	def onEvent(self, event, task):
		ret = wx.CallAfter(self.showDialog, event)

	def showDialog(self, event):
		self._checkLength(event)
		title = event.getTitle()
		message = event.getMessage()
		selections = event.getSelections()
		d = views.ask.Dialog(title, message, selections)
		d.Initialize()
		winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
		d.Show()
		ret = d.getData()
		event.setResult(ret)

	def _checkLength(self, event):
		assert StringUtil.GetWidthCount(event.getTitle()) <= L_TITLE
		assert StringUtil.GetWidthCount(event.getMessage()) <= L_MESSAGE
		for i in event.getSelections():
			assert StringUtil.GetWidthCount(i) <= L_BUTTON
