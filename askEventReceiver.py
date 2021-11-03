# Ask Event Receiver

import pprint
import simpleDialog
import views.ask
import wx

class AskEventReceiver:
	def onEvent(self, event, task):
		ret = wx.CallAfter(self.showDialog, event)
		# ret = self.showDialog(event.getMessage(), event.getSelections())

	def showDialog(self, event):
		message = event.getMessage()
		selections = event.getSelections()
		d = views.ask.Dialog(message, selections)
		d.Initialize()
		d.Show()
		ret = d.getData()
		event.setResult(ret)
